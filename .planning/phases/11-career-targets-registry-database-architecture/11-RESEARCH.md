# Phase 11: Career Targets Registry & Database Architecture - Research

**Researched:** 2026-10-08
**Domain:** SQLite Schema Design, Relational Data Lifecycle, FastAPI CRUD Architecture, Database Seeding
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01 (Registry Schema):** System stores career targets in SQLite table `career_targets` with fields: `id`, `name`, `slug`, `website`, `career_url`, `ats_type`, `feed_url`, `category_tier` (`startup`, `unicorn`, `enterprise`, `consulting`, `other`), `domain`, `role_focus` (JSON array string `["product", "strategy", "tech", "founders_office"]`), `status` (`active`, `syncing`, `error`, `paused`), `last_scraped_at`, `last_status`, `job_count`, `created_at`.
- **D-02 (Indexes):** Composite indexes on `category_tier`, `status`, and `last_scraped_at` for sub-10ms queries.
- **D-03 (Hybrid Seeding):** Auto-seed on backend startup if `career_targets` table is empty + idempotent standalone CLI script `seed_targets.py` supporting `--force`.
- **D-04 (Initial Data Sources):** Migrate both the 51+ curated Indian firms from `backend/scripts/add_indian_companies.py` and the 237 global firms from `backend/app/data/companies.json`.
- **D-05 (Soft-Archive Lifecycle):** Add `is_active INTEGER DEFAULT 1` and `last_seen_at TEXT` to `jobs` table. Default search queries filter `is_active = 1` while preserving bookmark/lead integrity. Implement `reconcile_target_jobs` helper to mark unlisted postings `is_active = 0`.
- **D-06 (REST API Suite):** `GET /api/targets` (with filters for tier, domain, role_tag, status, text query), `GET /api/targets/stats`, and `POST /api/targets/{slug}/sync` (single-target test scrape).

### the agent's Discretion
- Safe column addition via SQLite `PRAGMA table_info` checks.
- Slug generation and normalization routines.
- Default fallback tags for unclassified companies.

### Deferred Ideas (OUT OF SCOPE)
- Automated Reddit thread crawler to auto-generate targets (Phase 12).
- Batch scraping runner across all targets with background worker (Phase 14).
- Frontend Career Directory Hub UI component (Phase 15).
</user_constraints>

<architectural_responsibility_map>
## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| `career_targets` Table & Indexes | Database/Storage | — | Native SQLite DDL in `backend/app/db/database.py` with WAL PRAGMAs. |
| Schema Migration (`jobs.is_active`) | Database/Storage | — | Safe `ALTER TABLE` execution inside `init_db()` during startup. |
| Target Management REST APIs | API/Backend | Database/Storage | FastAPI router in `backend/app/api/targets.py`. |
| Seed Migrator & Catalog Parser | Backend Script / Service | Database/Storage | `backend/scripts/seed_targets.py` and startup hook. |
| Stale Job Reconciler | Database/Storage | API/Backend | Transactional SQL updates in `backend/app/db/database.py`. |
</architectural_responsibility_map>

<research_summary>
## Summary

Phase 11 establishes the central nervous system for CareerLoom's career portal repository. Previously, company definitions lived in static JSON files (`companies.json`), preventing runtime state tracking, dynamic health monitoring, and automated catalog expansion. By introducing the `career_targets` table, every monitored career portal becomes a first-class entity with tracked scrape history, health indicators, role focus tags, and live job counts.

To eliminate stale/ghost jobs without breaking candidate bookmarks or lead referrals, the `jobs` schema is extended with `is_active` and `last_seen_at`. When a target is re-scraped, any job belonging to that employer that is no longer returned in the live feed is transitioned to `is_active = 0`, keeping search results fresh while maintaining referential integrity.

**Primary recommendation:** Implement safe schema migrations in `init_db()`, build an idempotent seed loader consolidating existing Indian and global catalogs into `career_targets`, and expose high-performance REST endpoints for target querying and on-demand synchronization.
</research_summary>

<standard_stack>
## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `aiosqlite` | 3.45+ | Async SQLite driver | Native async connection pooling, WAL mode, transaction batching. |
| `FastAPI` | 0.115+ | Web framework | High performance ASGI, automatic OpenAPI docs, Pydantic v2 validation. |
| `Pydantic v2` | 2.10+ | Schema validation | Type-safe DTOs for `CareerTarget` models and filter query parsing. |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `slugify` / custom regex | Python stdlib | Slug generation | Converting company names into unique URL-safe slugs. |
| `json` | Python stdlib | Tag serialization | Storing role focus arrays (`["product", "strategy"]`) in SQLite. |
</standard_stack>

<architecture_patterns>
## Architecture Patterns

### Target Lifecycle State Machine
```
[created] -> status: 'active'
                 |
        [sync pass starts]
                 v
         status: 'syncing'
                 |
      +----------+----------+
      |                     |
 [fetch ok]           [fetch error]
      v                     v
last_status: 'ok'    last_status: 'failed' / '404'
status: 'active'     status: 'error' (if repeated > 3x: 'paused')
job_count: N
last_scraped_at: now()
```

### Safe SQLite Column Migration Pattern
```python
async def _ensure_column(db: aiosqlite.Connection, table: str, column: str, col_type: str) -> None:
    async with db.execute(f"PRAGMA table_info({table})") as cursor:
        columns = [row[1] for row in await cursor.fetchall()]
        if column not in columns:
            await db.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
```
</architecture_patterns>

<pitfalls_and_mitigations>
## Pitfalls & Mitigation

1. **Duplicate Slugs During Seeding**:
   - *Pitfall*: Company names like "Thoughtworks" and "Thoughtworks India" or "Tata 1mg" and "1mg" colliding on slug.
   - *Mitigation*: Deterministic unique slug generator with collision resolution (`company-slug-2`).
2. **Search Performance Degradation**:
   - *Pitfall*: Filtering by `is_active = 1` adding overhead to existing composite indexes.
   - *Mitigation*: Add composite index on `(is_active, date_posted DESC)` ensuring zero latency penalty (<20ms).
3. **Startup Race Condition on Auto-Seed**:
   - *Pitfall*: Multiple server workers trying to seed `career_targets` simultaneously.
   - *Mitigation*: Single transaction check `SELECT COUNT(*) FROM career_targets` with `INSERT OR IGNORE`.
</pitfalls_and_mitigations>

---
*Research completed: 2026-10-08 for Phase 11*
