import argparse
import asyncio
import logging
import sys
import time
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.db.database import (
    get_connection,
    get_target_by_slug,
    get_target_stats,
    init_db,
)
from backend.app.services.batch_runner import BatchScrapeRunner

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("careerloom").setLevel(logging.WARNING)


async def main():
    parser = argparse.ArgumentParser(
        description="CareerLoom Continuous Batch Scraping Runner"
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=15,
        help="Maximum concurrent scraping requests (default: 15)",
    )
    parser.add_argument(
        "--tier",
        type=str,
        default=None,
        help="Filter targets by tier: startup, unicorn, conglomerate, consulting",
    )
    parser.add_argument(
        "--domain",
        type=str,
        default=None,
        help="Filter targets by domain keyword",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of targets to evaluate",
    )
    parser.add_argument(
        "--target",
        type=str,
        default=None,
        help="Specific target company slug to synchronize",
    )
    parser.add_argument(
        "--purge-stale",
        type=int,
        default=None,
        help="Permanently delete inactive jobs older than N days (e.g. 30)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate scrape without mutating database jobs",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress real-time line progress",
    )

    args = parser.parse_args()

    print("=" * 74)
    print("  CareerLoom Discovery Engine: Continuous Batch Ingestion Pipeline")
    print("=" * 74)

    await init_db()

    target_list = None
    if args.target:
        specific = await get_target_by_slug(args.target)
        if not specific:
            print(f"Error: Target with slug '{args.target}' not found in registry.")
            sys.exit(1)
        target_list = [specific]
        print(f"Target Mode: Single target '{specific.name}' ({specific.ats_type})")
    else:
        filters = []
        if args.tier:
            filters.append(f"tier={args.tier}")
        if args.domain:
            filters.append(f"domain={args.domain}")
        if args.limit:
            filters.append(f"limit={args.limit}")
        filter_str = ", ".join(filters) if filters else "all active"
        print(f"Batch Scope: {filter_str} | Concurrency: {args.concurrency}")

    if args.dry_run:
        print("Mode: DRY-RUN (simulated execution, no database writes)")
    if args.purge_stale:
        print(f"Stale Purge: Enabled (cutoff threshold: {args.purge_stale} days inactive)")
    print("-" * 74)

    start_wall = time.time()
    runner = BatchScrapeRunner(concurrency=args.concurrency)

    def on_progress(p):
        if not args.quiet:
            pct = (p["processed"] / max(p["total"], 1)) * 100
            status_icon = "✓" if p["success"] else "✗"
            line = (
                f"[{p['processed']:3d}/{p['total']:3d} {pct:4.1f}%] {status_icon} "
                f"{p['current_target']:<24} -> jobs: {p['jobs_found']:3d} "
                f"| live: {p['live_jobs']:4d} | archived: {p['archived_jobs']:3d}"
            )
            print(line)

    result = await runner.run(
        targets=target_list,
        tier=args.tier,
        domain=args.domain,
        limit=args.limit,
        dry_run=args.dry_run,
        purge_stale_days=args.purge_stale,
        progress_callback=on_progress,
    )

    elapsed = time.time() - start_wall

    print("\n" + "=" * 74)
    print("  Batch Ingestion Summary Report")
    print("=" * 74)
    print(f"  Total Targets Evaluated:    {result.total_targets:>8d}")
    print(f"  Successful Targets:         {result.successful_targets:>8d}")
    print(f"  Failed / Error Targets:     {result.failed_targets:>8d}")
    print(f"  Live Jobs Discovered:       {result.live_jobs_found:>8d}")
    print(f"  Jobs Inserted/Upserted:     {result.new_jobs_upserted:>8d}")
    print(f"  Vanished Jobs Archived:     {result.archived_jobs_count:>8d}")
    if args.purge_stale:
        print(f"  Stale Postings Purged:      {result.purged_jobs_count:>8d}")
    print(f"  Total Execution Time:       {elapsed:>8.2f}s")
    print(f"  Ingestion Throughput:       {result.throughput_jobs_per_sec:>8.1f} jobs/sec")
    print("-" * 74)

    stats = await get_target_stats()
    async with get_connection() as db:
        async with db.execute("SELECT COUNT(*) as active_cnt FROM jobs WHERE is_active = 1") as cur:
            row = await cur.fetchone()
            live_active_jobs = row["active_cnt"] if row else 0

    print("  Repository Current Live State:")
    print(f"  • Monitored Targets:        {stats.total_targets:>8d}")
    print(f"  • Active Targets:           {stats.active_targets:>8d}")
    print(f"  • Live Active Jobs in DB:   {live_active_jobs:>8d}")
    print("=" * 74)


if __name__ == "__main__":
    asyncio.run(main())
