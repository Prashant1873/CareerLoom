---
phase: 14
slug: continuous-batch-scraping-pipeline-ingestion-automation
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-10-08
---

# Phase 14 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x |
| **Config file** | `pytest.ini` / root config |
| **Quick run command** | `pytest tests/test_batch_runner.py -v` |
| **Full suite command** | `pytest tests/test_batch_runner.py tests/test_batch_api_scheduler.py -v` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_batch_runner.py -v`
- **After every plan wave:** Run `pytest tests/test_batch_runner.py tests/test_batch_api_scheduler.py -v`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 14-01-01 | 01 | 1 | BATCH-01 | T-14-03 | Bounded concurrency with Semaphore(15) and per-host delay jitter | unit | `pytest tests/test_batch_runner.py -k test_batch_runner_concurrency -v` | ❌ W0 | ⬜ pending |
| 14-01-02 | 01 | 1 | BATCH-01 | T-14-02 | Error isolation: failing target logs error, updates status, does not abort batch | unit | `pytest tests/test_batch_runner.py -k test_error_isolation -v` | ❌ W0 | ⬜ pending |
| 14-01-03 | 01 | 1 | BATCH-02 | T-14-02 | Stale job reconciliation marks vanished jobs inactive; protects jobs on error | unit | `pytest tests/test_batch_runner.py -k test_reconciliation_and_data_loss_guard -v` | ❌ W0 | ⬜ pending |
| 14-01-04 | 01 | 1 | BATCH-02 | T-14-04 | Purge stale jobs permanently deletes inactive records older than threshold | unit | `pytest tests/test_batch_runner.py -k test_purge_stale_jobs -v` | ❌ W0 | ⬜ pending |
| 14-01-05 | 01 | 1 | BATCH-01 | — | CLI script supports --limit, --tier, --domain, --dry-run | integration | `pytest tests/test_batch_runner.py -k test_sync_batch_cli_args -v` | ❌ W0 | ⬜ pending |
| 14-02-01 | 02 | 2 | BATCH-03 | T-14-01 | BackgroundBatchScheduler manages periodic worker loop and mutex lock | unit | `pytest tests/test_batch_api_scheduler.py -k test_scheduler_lifecycle_and_mutex -v` | ❌ W0 | ⬜ pending |
| 14-02-02 | 02 | 2 | BATCH-03 | T-14-01 | POST /api/targets/sync triggers background sync; returns 409 when already active | integration | `pytest tests/test_batch_api_scheduler.py -k test_api_targets_sync_trigger -v` | ❌ W0 | ⬜ pending |
| 14-02-03 | 02 | 2 | BATCH-03 | — | GET /api/targets/sync/status reports live progress and last run stats | integration | `pytest tests/test_batch_api_scheduler.py -k test_api_targets_sync_status -v` | ❌ W0 | ⬜ pending |
| 14-02-04 | 02 | 2 | BATCH-03 | — | FastAPI lifespan starts and gracefully stops scheduler | integration | `pytest tests/test_batch_api_scheduler.py -k test_lifespan_scheduler_integration -v` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_batch_runner.py` — unit and integration tests for BatchScrapeRunner, error isolation, reconciliation, and CLI
- [ ] `tests/test_batch_api_scheduler.py` — integration tests for BackgroundBatchScheduler, API triggers, mutex lock, and lifespan

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| CLI Terminal Output | BATCH-01 | Terminal rendering formatting | Run `python backend/scripts/sync_batch.py --limit 3 --dry-run` and inspect ANSI/plain summary table |
| Long-Running Background Sync | BATCH-03 | Real-time wall-clock sync behavior | Trigger `POST /api/targets/sync` and poll `/api/targets/sync/status` over several seconds |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 5s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-10-08
