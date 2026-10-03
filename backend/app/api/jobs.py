import logging
from typing import List, Optional
from fastapi import APIRouter, BackgroundTasks, Query
from pydantic import BaseModel

from backend.app.db.database import (
    get_filter_options,
    get_stats,
    query_jobs,
)
from backend.app.models.job import JobFilterParams, JobItem
from backend.app.services.sync import JobSyncService

logger = logging.getLogger("careerloom.api.jobs")
router = APIRouter(prefix="/api/jobs", tags=["Jobs"])
sync_service = JobSyncService()


class LiveFetchRequest(BaseModel):
    name: str
    slug: str
    ats_type: Optional[str] = None


class JobsResponse(BaseModel):
    total: int
    limit: int
    offset: int
    jobs: List[JobItem]


@router.get("", response_model=JobsResponse)
async def list_jobs(
    search: Optional[str] = Query(None, description="Keywords to match against title or company"),
    company: Optional[str] = Query(None, description="Exact employer company name"),
    category: Optional[str] = Query(None, description="Canonical category (product, software_engineering, data_ai, design, etc.)"),
    domain: Optional[str] = Query(None, description="Industry domain"),
    country: Optional[str] = Query(None, description="Country or 'remote'"),
    seniority: Optional[str] = Query(None, description="Seniority level (entry, mid, senior, lead, intern)"),
    is_remote: Optional[bool] = Query(None, description="Filter for remote positions"),
    posted_within_days: Optional[int] = Query(None, description="Posting freshness in days (1, 7, 14, 30)"),
    sort_by: str = Query("date", description="Sort order: 'date' (newest first), 'company', or 'title'"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """
    Search and filter job listings from the indexed database with sub-50ms latency.
    Results are chronologically sorted by date_posted DESC by default.
    """
    params = JobFilterParams(
        search=search,
        company=company,
        category=category,
        domain=domain,
        country=country,
        seniority=seniority,
        is_remote=is_remote,
        posted_within_days=posted_within_days,
        sort_by=sort_by,
        limit=limit,
        offset=offset,
    )

    jobs, total = await query_jobs(params)
    return JobsResponse(
        total=total,
        limit=limit,
        offset=offset,
        jobs=jobs,
    )


@router.post("/sync")
async def trigger_sync(background_tasks: BackgroundTasks, limit_companies: Optional[int] = None):
    """
    Triggers concurrent synchronization of all registered major employer career feeds.
    Runs asynchronously in the background.
    """
    background_tasks.add_task(sync_service.sync_all, concurrency=5, limit_companies=limit_companies)
    return {
        "status": "sync_started",
        "message": f"Background sync initiated for {'all' if not limit_companies else limit_companies} companies",
    }


@router.post("/live-fetch")
async def live_fetch_company(req: LiveFetchRequest):
    """
    On-demand live fetch for a target employer ATS board.
    Fetches, normalizes, and upserts fresh listings immediately.
    """
    count = await sync_service.live_fetch_company(
        company_name=req.name,
        company_slug=req.slug,
        ats_type=req.ats_type,
    )
    return {
        "company": req.name,
        "slug": req.slug,
        "synced_jobs_count": count,
    }


@router.get("/companies")
async def list_companies():
    """
    Returns the catalog of supported seed employers and their ATS types.
    """
    companies = sync_service.load_companies()
    return {
        "total": len(companies),
        "companies": companies,
    }


@router.get("/stats")
async def get_database_stats():
    """
    Returns high-level statistics of the indexed job database.
    """
    stats = await get_stats()
    return stats


@router.get("/filter-options")
async def get_filter_dropdown_options():
    """
    Returns available filter values (categories, domains, countries, companies) for UI dropdowns.
    """
    options = await get_filter_options()
    return options
