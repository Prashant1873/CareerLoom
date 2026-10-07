# Phase 14: Continuous Batch Scraping Pipeline & Ingestion Automation - Research

**Researched:** 2026-10-08
**Domain:** High-Throughput Async Scraping, Bounded Concurrency (asyncio.Semaphore), Host Rate Limiting, Stale Job Reconciliation, Data Loss Protection, Background Scheduled Workers, FastAPI Lifespan
**Confidence:** HIGH

<user_constraints>
## User Constraints (from REQUIREMENTS.md & ROADMAP.md)

### Phase Requirements
- **BATCH-01**: High-throughput async batch scraping runner (`sync_batch.py`) executes concurrent fetching across all active career targets with bounded concurrency (`asyncio.Semaphore(15)`) and error isolation.
- **BATCH-02**: Stale job reconciler detects closed/unlisted postings during sync passes, purging or archiving them to prevent ghost jobs.
- **BATCH-03**: Continuous background scheduling service and API trigger (`POST /api/targets/sync`) for automated periodic updates and on-demand sync refreshes.

### Key Architectural Guidelines
- Zero-cost operating model: Pure Python `asyncio` and SQLite, zero paid Redis/Celery infrastructure.
- Trust boundary data-loss protection: If an ATS request fails or times out, never soft-archive or delete existing jobs for that company.
- Sub-100ms API response latency: Background tasks run asynchronously without blocking API request threads.
- Standalone CLI runner with full observability: Table summary output, throughput metrics (jobs/sec), and `--dry-run` inspection.
</user_constraints>

<architectural_responsibility_map>
## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Batch Scraping Engine | Backend Service | Connectors | `backend/app/services/batch_runner.py` managing `asyncio.Semaphore(15)`, target partitioning, host jitter, and task orchestration. |
| Stale Job Reconciler & Purge | Database / Storage | Backend Service | `backend/app/db/database.py` updating `is_active`, `last_seen_at`, `career_targets.job_count`, and providing `purge_stale_jobs`. |
| Standalone Batch CLI | Backend Script | Service Layer | `backend/scripts/sync_batch.py` providing CLI flags (`--concurrency`, `--tier`, `--domain`, `--limit`, `--target`, `--dry-run`, `--purge-stale`). |
| Background Scheduler Service | Backend Service | FastAPI Lifecycle | `backend/app/services/scheduler.py` managing background loop, concurrency mutex, run history, and progress state. |
| Targets Batch REST API | API Layer | Backend Service | `backend/app/api/targets.py` exposing `POST /api/targets/sync`, `GET /api/targets/sync/status`, and `POST /api/targets/purge-stale`. |
| Application Lifecycle Integration | Application Core | API Server | `backend/app/main.py` starting and shutting down background scheduler cleanly during lifespan. |
</architectural_responsibility_map>

<research_summary>
## Summary

CareerLoom tracks 220+ global and Indian employers across 5 sectors. Prior to Phase 14, ingestion was triggered via one-off scripts (`bulk_sync.py`, `sync_india.py`) or single-company live fetches without continuous scheduling, per-host rate limiting, or automated batch status observability.

Phase 14 establishes a continuous batch scraping and reconciliation infrastructure:
1. **Async Batch Engine (`BatchScrapeRunner`)**:
   - Concurrency bounded via `asyncio.Semaphore(15)`.
   - Host-keyed politeness jitter to prevent 429 Too Many Requests against multi-tenant ATS APIs (Greenhouse, Lever, Ashby, SmartRecruiters, Workday).
   - Complete error isolation: individual employer errors do not crash or block the batch.
2. **Robust Stale Job Reconciliation (`reconcile_target_jobs`)**:
   - Trust boundary protection: only updates `is_active = 0` on verified successful HTTP 200 responses. Network timeouts and exceptions preserve existing listings.
   - Updates `is_active = 1` and `last_seen_at` for active jobs.
   - Optional hard purge (`purge_stale_jobs`) for long-dead listings (>30 days inactive).
3. **Background Scheduler (`BackgroundBatchScheduler`) & API Endpoints**:
   - Periodic async background loop running in FastAPI lifespan with graceful cancellation.
   - Non-blocking `POST /api/targets/sync` trigger with overlap prevention (mutex).
   - Real-time `GET /api/targets/sync/status` tracking processed count, active target, and live metrics.
4. **CLI Utility (`sync_batch.py`)**:
   - Full CLI control with ANSI/plain table reporting and `--dry-run` safety.
</research_summary>

<standard_stack>
## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `asyncio` | Python 3.11+ | Concurrency & Async Tasks | Built-in, high-efficiency task orchestration with `asyncio.Semaphore` and `create_task`. |
| `aiosqlite` | 3.45+ | SQLite Async Driver | WAL mode support, sub-millisecond atomic batch updates. |
| `FastAPI` | 0.115+ | Web Framework & Lifecycle | Asynchronous background tasks, OpenAPI documentation, native lifespan support. |
| `httpx` | 0.28+ | Async HTTP Client | Used in existing ATS connectors with connection pooling and timeouts. |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `argparse` | stdlib | CLI Flags Parsing | `sync_batch.py` parameter parsing. |
| `time` / `datetime` | stdlib | Timestamps & Durations | UTC timestamps, throughput calculation. |
| `random` | stdlib | Politeness Jitter | Delaying requests between identical ATS hosts by 100-300ms. |
</standard_stack>

<architecture_patterns>
## Architecture Patterns

### Pattern 1: Bounded Concurrency with Error Isolation
```
[Target List (220+)]
         |
         v
[asyncio.Semaphore(15)]
         |
  +------+------+------+ ... (up to 15 concurrent workers)
  |             |      |
[Target A]  [Target B] [Target C]
  |             |      |
  v             v      v
[Host Jitter: 100-300ms per ATS host]
  |             |      |
[fetch_jobs] [fetch_jobs] [fetch_jobs]
  |             |      |
  v (try/except)|      v
[Success?]      |   [Exception?]
  |             |      |
  v             |      v
[upsert_jobs]   |   [Log Warning]
[reconcile]     |   [Set target.last_status='error']
  |             |   [DO NOT soft-archive jobs]
  +------+------+------+
         |
         v
[Update Batch Metrics & Progress]
```

### Pattern 2: Safe Reconciliation State Machine
```
              +--------------------------+
              |   fetch_jobs(company)    |
              +--------------------------+
                           |
            +--------------+--------------+
            |                             |
      [Success 200]                 [Network Error / 429 / 500]
            |                             |
     [jobs list returned]          [Exception caught]
            |                             |
     +------+------+                      |
     |             |                      v
[jobs > 0]     [jobs == 0]       [DO NOT ALTER JOBS TABLE]
     |             |             [career_targets.last_status = 'error']
     v             v             [Retain existing active jobs]
[upsert_jobs]  [reconcile: 0 live]
[reconcile]    [is_active = 0]
[is_active=1]  [status = 'ok']
[status='ok']
```

### Pattern 3: Background Scheduler & Mutex State
```
[FastAPI Lifespan]
       |
       +---> scheduler.start() ---> [asyncio.Task: periodic_worker_loop]
       |                                   |
       |                            [Sleep interval]
       |                                   |
       |                            [Acquire sync mutex]
       |                            [Run batch scraper]
       |                            [Release sync mutex]
       |
       +---> [POST /api/targets/sync]
                    |
             [Check mutex: is_running?]
             +------+------+
             |             |
        [Yes]             [No]
             |             |
     [Return 409]   [Acquire mutex]
                    [Launch background task]
                    [Return 202 Accepted]
```
</architecture_patterns>

<threat_model>
## Threat Model (ASVS L1)

| Threat ID | Threat Description | Severity | Mitigation Strategy |
|-----------|--------------------|----------|---------------------|
| T-14-01 | Overlapping Sync Starvation: Multiple concurrent `POST /api/targets/sync` calls spawn uncontrolled batch processes, causing DB lock contention and memory exhaustion. | HIGH | Implement an async mutex/lock (`self._is_running`) in `BackgroundBatchScheduler`. Reject redundant triggers with HTTP 409 Conflict. |
| T-14-02 | Silent Data Destruction: Intermittent network timeouts or ATS 429 errors cause `fetch_jobs` to return 0 jobs, falsely marking all active company jobs as closed/inactive. | HIGH | Strict separation of fetch success vs error. Only call `reconcile_target_jobs` when fetch succeeds with HTTP 200. On exception, leave existing jobs untouched and record `last_status = 'error'`. |
| T-14-03 | Upstream ATS Host Flooding: Concurrent requests to the same ATS endpoint (e.g. 50 Greenhouse targets simultaneously) lead to IP ban / 429 rate limiting. | MEDIUM | Group or jitter requests by ATS provider domain with polite delay (100-300ms) and bounded global concurrency (`Semaphore(15)`). |
| T-14-04 | Stale Data Accumulation: Indefinite accumulation of soft-archived jobs degrades SQLite B-Tree performance over time. | LOW | Provide an automated `purge_stale_jobs(days_inactive=30)` helper and endpoint to hard-prune listings dead for over a month. |
</threat_model>

## Validation Architecture

1. **Unit Tests**:
   - `tests/test_batch_runner.py`:
     - Test bounded concurrency (`Semaphore(15)` respected).
     - Test error isolation (simulated failed target does not abort remaining targets).
     - Test data-loss protection (failed target does not deactivate existing jobs).
     - Test `purge_stale_jobs` logic and cutoff calculations.
2. **Integration Tests**:
   - `tests/test_batch_api_scheduler.py`:
     - Test `POST /api/targets/sync` returns 202 and launches sync.
     - Test `POST /api/targets/sync` returns 409 when sync is already active.
     - Test `GET /api/targets/sync/status` returns progress and stats.
     - Test `BackgroundBatchScheduler` start/stop lifecycle and clean cancellation.
3. **CLI Smoke Test**:
   - Run `python backend/scripts/sync_batch.py --limit 3 --dry-run` to verify CLI argument parsing and summary output.
