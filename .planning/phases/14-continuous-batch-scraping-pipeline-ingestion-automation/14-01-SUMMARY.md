# Phase 14 Plan 01 Summary: Batch Scraping Core Engine, Stale Job Reconciler & CLI Runner

## Status: Completed

### Delivered Components
1. **Hardened Reconciler & Data-Loss Guard** ([database.py](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/backend/app/db/database.py)):
   - Updated `reconcile_target_jobs` with `is_successful_fetch: bool = True` parameter (T-14-02).
   - If `is_successful_fetch` is False (network error, timeout, 429), existing jobs are preserved and never marked inactive; `career_targets.last_status` is updated to `'error'`.
   - On successful scrape (`is_successful_fetch=True`): live jobs are marked `is_active = 1` and `last_seen_at = now`; vanished jobs for that employer are soft-archived (`is_active = 0`); `career_targets.job_count` and `last_scraped_at` are updated.
   - Added `purge_stale_jobs(days_inactive=30, dry_run=False)` permanently deleting inactive postings older than the threshold cutoff (T-14-04).
2. **Batch Scraping Engine** ([batch_runner.py](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/backend/app/services/batch_runner.py)):
   - Implemented `BatchScrapeRunner` with bounded concurrency via `asyncio.Semaphore(15)` (BATCH-01).
   - Implemented per-host politeness rate-limiting jitter (100-300ms) for shared ATS hosts (`greenhouse`, `lever`, `ashby`, etc.) to prevent upstream 429 throttling (T-14-03).
   - Strict per-target error isolation: failures on individual targets log warnings and record status without aborting or slowing down the batch.
   - Telemetry reporting via `BatchScrapeResult` with live throughput metrics (jobs/sec).
3. **Standalone Batch CLI Runner** ([sync_batch.py](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/backend/scripts/sync_batch.py)):
   - CLI flags: `--concurrency`, `--tier`, `--domain`, `--limit`, `--target`, `--purge-stale`, `--dry-run`, `--quiet`.
   - Formatted ANSI summary table and live progress tracker.
4. **Automated Verification**:
   - `tests/test_batch_runner.py`: 5/5 tests passing in 2.67s (concurrency semaphore check, error isolation, data-loss guard, stale job purge, CLI arguments).
