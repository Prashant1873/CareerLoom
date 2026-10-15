"""
Job Re-classification Script.
Idempotently re-evaluates all cached jobs against the compiled regex classifier
and assigns granular PM and Strategy Consulting categories and tracks.
Supports --dry-run for zero-risk impact auditing.
"""
import argparse
import asyncio
import logging
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

# Setup project root import
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.db.database import get_connection, init_db
from backend.app.utils.classifier import classify_role

logger = logging.getLogger("careerloom.reclassify")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

FOCUS_CATEGORIES = [
    "product",
    "technical_product",
    "product_ops",
    "management_consulting",
    "corporate_strategy",
    "founders_office",
]


async def reclassify_jobs(
    dry_run: bool = False,
    batch_size: int = 500,
    limit: int = None,
) -> Dict[str, object]:
    start_time = time.perf_counter()
    await init_db()

    query = "SELECT id, title, company, domain, category, seniority, track FROM jobs"
    if limit and limit > 0:
        query += f" LIMIT {limit}"

    async with get_connection() as db:
        async with db.execute(query) as cursor:
            rows = await cursor.fetchall()

    total_jobs = len(rows)
    logger.info(f"Loaded {total_jobs} jobs from SQLite for re-classification (dry_run={dry_run})")

    old_cat_counter = Counter()
    new_cat_counter = Counter()
    track_counter = Counter()
    updates: List[Tuple[str, str, str, str]] = []
    changed_count = 0

    for row in rows:
        job_id = row["id"]
        title = row["title"] or ""
        company = row["company"] or ""
        domain = row["domain"] or ""
        old_cat = row["category"] or "general"
        old_sen = row["seniority"] or "mid"
        old_track = row["track"]

        old_cat_counter[old_cat] += 1

        new_cat, new_sen, new_track = classify_role(
            title=title,
            company=company,
            domain_hint=domain,
        )

        new_cat_counter[new_cat] += 1
        if new_track:
            track_counter[new_track] += 1

        is_changed = (new_cat != old_cat) or (new_sen != old_sen) or (new_track != old_track)
        if is_changed:
            changed_count += 1
            updates.append((new_cat, new_sen, new_track, job_id))

    # Apply database updates if not dry run
    if not dry_run and updates:
        logger.info(f"Applying updates to {len(updates)} records in batches of {batch_size}...")
        async with get_connection() as db:
            for i in range(0, len(updates), batch_size):
                batch = updates[i : i + batch_size]
                await db.executemany(
                    """
                    UPDATE jobs
                    SET category = ?, seniority = ?, track = ?
                    WHERE id = ?
                    """,
                    batch,
                )
            await db.commit()
        logger.info(f"Successfully committed {len(updates)} record updates.")

    elapsed_ms = (time.perf_counter() - start_time) * 1000

    # Output Structured Distribution Table
    print("\n" + "=" * 80)
    print("CAREERLOOM TAXONOMY RE-CLASSIFICATION AUDIT REPORT")
    print("=" * 80)
    print(f"Mode:             {'DRY RUN (No SQLite updates)' if dry_run else 'LIVE EXECUTION (SQLite updated)'}")
    print(f"Total Evaluated:  {total_jobs} jobs")
    print(f"Total Modified:   {changed_count} jobs ({changed_count / max(1, total_jobs):.1%})")
    print(f"Elapsed Time:     {elapsed_ms:.2f} ms ({elapsed_ms / max(1, total_jobs):.3f} ms/job)")
    print("-" * 80)

    print("\n### Target Categories Breakdown:")
    print(f"{'Category':<25} | {'Old Count':<10} | {'New Count':<10} | {'Net Change':<10}")
    print("-" * 65)
    for cat in FOCUS_CATEGORIES:
        old_c = old_cat_counter.get(cat, 0)
        new_c = new_cat_counter.get(cat, 0)
        net = new_c - old_c
        sign = "+" if net > 0 else ""
        print(f"{cat:<25} | {old_c:<10} | {new_c:<10} | {sign}{net:<10}")

    print("\n### Top 10 Granular Tracks Detected:")
    print(f"{'Track':<45} | {'Job Count':<10}")
    print("-" * 60)
    for track, cnt in track_counter.most_common(10):
        print(f"{track:<45} | {cnt:<10}")
    print("=" * 80 + "\n")

    return {
        "total_jobs": total_jobs,
        "changed_count": changed_count,
        "dry_run": dry_run,
        "elapsed_ms": elapsed_ms,
        "new_cat_counts": dict(new_cat_counter),
        "track_counts": dict(track_counter),
    }


def main():
    parser = argparse.ArgumentParser(description="Re-classify existing SQLite jobs with Phase 13 PM/Strategy taxonomy.")
    parser.add_argument("--dry-run", action="store_true", help="Preview classification changes without updating SQLite.")
    parser.add_argument("--batch-size", type=int, default=500, help="Batch size for database updates (default: 500).")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of jobs processed for quick testing.")
    args = parser.parse_args()

    asyncio.run(reclassify_jobs(
        dry_run=args.dry_run,
        batch_size=args.batch_size,
        limit=args.limit,
    ))


if __name__ == "__main__":
    main()
