import asyncio
import logging
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.db.database import get_connection, init_db, upsert_jobs
from backend.app.services.sync import JobSyncService

# Setup logging
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("careerloom").setLevel(logging.WARNING)
logger = logging.getLogger("careerloom.bulk_sync")


async def run_bulk_sync(
    concurrency: int = 8,
    limit: Optional[int] = None,
    domain_filter: Optional[str] = None,
):
    print("=" * 70)
    print(" CareerLoom: Global Job Discovery Engine - Bulk Ingestion Runner")
    print("=" * 70)

    await init_db()
    sync_service = JobSyncService()
    companies = sync_service.load_companies()

    if domain_filter:
        companies = [c for c in companies if domain_filter.lower() in c.get("domain", "").lower()]
        print(f"Filtered to {len(companies)} companies matching domain '{domain_filter}'")

    if limit:
        companies = companies[:limit]
        print(f"Limited to first {limit} companies")

    total_companies = len(companies)
    print(f"Starting bulk sync for {total_companies} companies with concurrency={concurrency}...\n")

    semaphore = asyncio.Semaphore(concurrency)
    total_jobs_synced = 0
    successful_companies = 0
    failed_companies = 0
    skipped_companies: List[str] = []
    processed_count = 0
    start_time = time.time()

    async def _sync_single(idx: int, comp: Dict[str, str]):
        nonlocal total_jobs_synced, successful_companies, failed_companies, processed_count
        name = comp["name"]
        slug = comp["slug"]
        ats_type = comp.get("ats_type", "greenhouse")
        domain = comp.get("domain", "Tech")

        async with semaphore:
            connector = sync_service.connectors.get(ats_type)
            if not connector:
                processed_count += 1
                failed_companies += 1
                skipped_companies.append(f"{name} (unknown ATS: {ats_type})")
                return

            try:
                jobs = await connector.fetch_jobs(
                    company_name=name,
                    company_slug=slug,
                    domain=domain,
                )
                if jobs:
                    inserted = await upsert_jobs(jobs)
                    total_jobs_synced += inserted
                    successful_companies += 1
                    processed_count += 1
                    elapsed = time.time() - start_time
                    print(
                        f"[{processed_count:3d}/{total_companies:3d}] ✓ {name:<26} ({ats_type:<10}) -> "
                        f"{len(jobs):4d} jobs (New/Upserted: {inserted:4d}) | Total: {total_jobs_synced:5d} | {elapsed:.1f}s"
                    )
                else:
                    processed_count += 1
                    failed_companies += 1
                    skipped_companies.append(f"{name} (0 jobs)")
                    print(f"[{processed_count:3d}/{total_companies:3d}] - {name:<26} ({ats_type:<10}) -> 0 jobs")
            except Exception as e:
                processed_count += 1
                failed_companies += 1
                skipped_companies.append(f"{name} ({str(e)[:30]})")
                print(f"[{processed_count:3d}/{total_companies:3d}] ✗ {name:<26} ({ats_type:<10}) -> Error: {str(e)[:40]}")

    tasks = [_sync_single(i, c) for i, c in enumerate(companies, 1)]
    await asyncio.gather(*tasks, return_exceptions=True)

    elapsed_total = time.time() - start_time
    print("\n" + "=" * 70)
    print(" Bulk Sync Complete!")
    print("=" * 70)
    print(f"Total Companies Evaluated: {total_companies}")
    print(f"Successful Companies:       {successful_companies}")
    print(f"Skipped/Empty Companies:    {failed_companies}")
    print(f"Total Jobs Upserted:        {total_jobs_synced}")
    print(f"Elapsed Time:               {elapsed_total:.2f}s ({total_jobs_synced / max(elapsed_total, 0.1):.1f} jobs/sec)")

    # Query DB stats directly
    async with get_connection() as db:
        async with db.execute("SELECT COUNT(*), COUNT(DISTINCT company), COUNT(DISTINCT category), COUNT(DISTINCT country) FROM jobs") as cur:
            row = await cur.fetchone()
            if row:
                print(f"\n[Database Live Stats]")
                print(f"Total Jobs in DB:      {row[0]:,}")
                print(f"Unique Companies:      {row[1]:,}")
                print(f"Unique Categories:     {row[2]:,}")
                print(f"Unique Countries:      {row[3]:,}")
    print("=" * 70)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="CareerLoom Bulk ATS Ingestion Runner")
    parser.add_argument("--concurrency", type=int, default=8, help="Number of concurrent HTTP requests")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of companies to sync")
    parser.add_argument("--domain", type=str, default=None, help="Filter by domain keyword")
    args = parser.parse_args()

    asyncio.run(run_bulk_sync(concurrency=args.concurrency, limit=args.limit, domain_filter=args.domain))
