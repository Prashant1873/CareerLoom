# Phase 11: Career Targets Registry & Database Architecture - Context

**Gathered:** 2026-10-08
**Status:** Ready for planning

<domain>
## Phase Boundary

Implement a persistent SQLite registry table (`career_targets`) for tracking hundreds of company career portal URLs, ATS providers, sync health, and scrape metrics, backed by REST API management endpoints, seed migration from existing catalogs, and a soft-archive stale job reconciler.

</domain>

<decisions>
## Implementation Decisions

### Target Registry Schema & Role Tags
- **D-01:** System stores career targets in SQLite table `career_targets` with schema:
  - `id` (TEXT PRIMARY KEY)
  - `name` (TEXT NOT NULL)
  - `slug` (TEXT UNIQUE NOT NULL)
  - `website` (TEXT)
  - `career_url` (TEXT NOT NULL)
  - `ats_type` (TEXT NOT NULL: `greenhouse`, `lever`, `ashby`, `smartrecruiters`, `workday`, `custom`)
  - `feed_url` (TEXT)
  - `category_tier` (TEXT NOT NULL: `startup`, `unicorn`, `enterprise`, `consulting`, `other`)
  - `domain` (TEXT NOT NULL)
  - `role_focus` (TEXT: JSON array `["product", "strategy", "tech", "founders_office"]`)
  - `status` (TEXT DEFAULT 'active': `active`, `syncing`, `error`, `paused`)
  - `last_scraped_at` (TEXT)
  - `last_status` (TEXT: `ok`, `404`, `rate_limited`, `failed`)
  - `job_count` (INTEGER DEFAULT 0)
  - `created_at` (TEXT NOT NULL)
- **D-02:** Composite indexes created on `category_tier`, `status`, and `last_scraped_at` to guarantee sub-10ms target querying.

### Seed Ingestion Strategy
- **D-03:** Hybrid seeding model:
  - On FastAPI startup, check if `career_targets` is empty; if empty, automatically populate from seed files.
  - Dedicated CLI script `backend/scripts/seed_targets.py` supporting `--force` flag for idempotent updates and manual maintenance.
- **D-04:** Initial catalog seed migrates both the 51+ curated Indian firms from `backend/scripts/add_indian_companies.py` and the 237 global firms from `backend/app/data/companies.json`.

### Stale Job Pruning & Lifecycle
- **D-05:** Soft-archive strategy:
  - Add `is_active INTEGER DEFAULT 1` and `last_seen_at TEXT` columns to `jobs` table schema.
  - Default `/api/jobs` search queries filter `is_active = 1` so stale jobs vanish from search.
  - Bookmark and lead associations remain valid without foreign key breaks.
  - Reconciler helper `reconcile_target_jobs(company, live_job_ids, sync_timestamp)` marks vanished jobs `is_active = 0`.

### Target Management REST APIs
- **D-06:** Expose comprehensive management endpoints in `backend/app/api/targets.py`:
  - `GET /api/targets` (supports filtering by `tier`, `domain`, `role_tag`, `status`, and text `q`).
  - `GET /api/targets/stats` (counts by tier, active status, total monitored companies, total live jobs).
  - `POST /api/targets/{slug}/sync` (on-demand test scrape for a single company updating `last_scraped_at`, `job_count`, and `last_status`).

### Agent's Discretion
- Exact SQL query optimization and transaction batching.
- Slug generation helper formatting.
- Default fallback values for unassigned role focus tags.

</decisions>

<canonical_refs>
## Canonical References

### Database & Scrapers
- `backend/app/db/database.py` — Existing SQLite schema, connection pooling (`PRAGMA journal_mode=WAL`), and index configuration.
- `backend/app/data/companies.json` — Existing 237-employer catalog.
- `backend/scripts/add_indian_companies.py` — Existing 51+ Indian unicorn & startup catalog.
- `backend/app/services/sync.py` — Current job sync service and ATS connector orchestration.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `backend/app/db/database.py`: `get_connection()` async context manager, WAL mode PRAGMAs.
- `backend/app/scrapers/`: Modular ATS connectors (`greenhouse.py`, `lever.py`, `ashby.py`, `smartrecruiters.py`, `workday.py`).
- `backend/app/models/job.py`: `JobItem` Pydantic model with hash deduplication.

### Established Patterns
- Pydantic models in `backend/app/models/` for request/response serialization.
- FastAPI routers registered in `backend/app/main.py`.
- Pure async operations with `aiosqlite`.

### Integration Points
- Add `career_targets` table and `jobs` schema migration in `backend/app/db/database.py`.
- Mount `targets_router` in `backend/app/main.py`.
- Add `backend/scripts/seed_targets.py`.

</code_context>

<deferred>
## Deferred Ideas

- Automated Reddit thread scanning to auto-generate targets (Phase 12).
- Batch scraping runner across all targets with cron worker (Phase 14).
- Frontend visual Career Directory Hub modal (Phase 15).

</deferred>

---

*Phase: 11-career-targets-registry-database-architecture*
*Context gathered: 2026-10-08*
