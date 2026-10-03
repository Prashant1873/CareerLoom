import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api import categories, jobs, nlp
from backend.app.db.database import get_stats, init_db
from backend.app.services.sync import JobSyncService

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("careerloom.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize database schema
    logger.info("Starting CareerLoom Discovery Engine...")
    await init_db()
    
    # Auto-seed initial batch if database is empty
    stats = await get_stats()
    if stats.get("total_jobs", 0) == 0:
        logger.info("Empty database detected. Seeding initial tier-1 firms...")
        sync = JobSyncService()
        # Seed top 5 diverse firms on boot for instant availability
        await sync.sync_all(concurrency=3, limit_companies=5)

    yield
    # Shutdown
    logger.info("Shutting down CareerLoom Discovery Engine...")


app = FastAPI(
    title="CareerLoom Discovery Engine API",
    description="Intelligent Job Discovery Engine querying direct ATS feeds of major global employers",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for local dev and frontend deployment (Vercel / Cloudflare Pages)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "app": "CareerLoom Discovery Engine",
        "version": "1.0.0",
    }


@app.get("/")
async def root():
    return {
        "message": "Welcome to CareerLoom Discovery Engine API",
        "docs_url": "/docs",
        "endpoints": {
            "health": "/api/health",
            "jobs": "/api/jobs",
            "categories": "/api/categories",
            "nlp_parse": "/api/nlp/parse",
            "nlp_search": "/api/nlp/search",
            "companies": "/api/jobs/companies",
            "stats": "/api/jobs/stats",
            "filter_options": "/api/jobs/filter-options",
        },
    }


app.include_router(jobs.router)
app.include_router(categories.router)
app.include_router(nlp.router)
