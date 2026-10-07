import asyncio
import logging
import sys
import time
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.db.database import init_db, upsert_jobs, get_connection
from backend.app.services.sync import JobSyncService
from backend.app.utils.classifier import INDIAN_COMPANIES_HINTS

logging.basicConfig(level=logging.WARNING)


async def main():
    print("=" * 65)
    print(" CareerLoom: Indian Tech Ecosystem Ingestion Runner")
    print("=" * 65)

    await init_db()
    service = JobSyncService()
    all_companies = service.load_companies()

    indian_companies = [
        c for c in all_companies
        if c['slug'].lower() in INDIAN_COMPANIES_HINTS
        or "india" in c['name'].lower()
        or "india" in c.get('domain', '').lower()
    ]

    print(f"Targeting {len(indian_companies)} verified Indian tech employers & GCCs...\n")

    semaphore = asyncio.Semaphore(8)
    total_jobs = 0
    total_india_jobs = 0
    successful = 0
    start = time.time()

    async def sync_company(c):
        nonlocal total_jobs, total_india_jobs, successful
        ats_type = c.get("ats_type", "greenhouse")
        connector = service.connectors.get(ats_type)
        if not connector:
            return

        async with semaphore:
            try:
                jobs = await connector.fetch_jobs(
                    company_name=c["name"],
                    company_slug=c["slug"],
                    domain=c.get("domain", "Tech"),
                )
                if jobs:
                    inserted = await upsert_jobs(jobs)
                    india_jobs = sum(1 for j in jobs if j.country == "India")
                    total_jobs += len(jobs)
                    total_india_jobs += india_jobs
                    successful += 1
                    print(
                        f"[OK]   {c['name']:<28} ({ats_type:<14}) -> "
                        f"{len(jobs):4d} total jobs | {india_jobs:4d} India jobs",
                        flush=True
                    )
                else:
                    print(f"[-]    {c['name']:<28} ({ats_type:<14}) -> 0 jobs", flush=True)
            except Exception as e:
                print(f"[FAIL] {c['name']:<28} ({ats_type:<14}) -> Error: {str(e)[:45]}", flush=True)

    await asyncio.gather(*[sync_company(c) for c in indian_companies])
    elapsed = time.time() - start

    # Check database statistics
    async with get_connection() as db:
        async with db.execute("SELECT COUNT(*) FROM jobs WHERE country = 'India'") as cursor:
            india_in_db = (await cursor.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM jobs") as cursor:
            total_in_db = (await cursor.fetchone())[0]

    print("\n" + "=" * 65)
    print(f" Indian Sync Completed in {elapsed:.2f}s")
    print(f" Employers Synced Successfully: {successful}/{len(indian_companies)}")
    print(f" Total Live Jobs Ingested:      {total_jobs}")
    print(f" Jobs Tagged Country='India':    {total_india_jobs}")
    print(f" Total India Jobs in SQLite:     {india_in_db}")
    print(f" Total Global Jobs in SQLite:    {total_in_db}")
    print("=" * 65)


if __name__ == "__main__":
    asyncio.run(main())
