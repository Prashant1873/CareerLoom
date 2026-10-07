# Phase 12: Reddit Discovery Pipeline & Indian Ecosystem Catalog Scaling - Research

**Researched:** 2026-10-08
**Domain:** Reddit Public JSON Crawling, Heuristic & Regex Entity Extraction, Asynchronous Multi-ATS Probing, SQLite TTL Caching, Catalog Data Engineering (220+ Indian Companies)
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01 (Reddit Access Protocol):** Public Reddit JSON feed API (`.json`) with custom `CareerLoom-Discovery/1.0` User-Agent header, polite 1.0s delay between requests, and exponential backoff.
- **D-02 (24h Cache Table):** Dedicated SQLite table (`discovery_cache`) tracking `subreddit`, `post_id`, `payload`, `scanned_at`, and `expires_at` with a 24-hour TTL check.
- **D-03 (Hybrid Query Strategy):** Scanner queries both recent top/hot threads and executes targeted keyword search queries (`"hiring"`, `"openings"`, `"careers"`, `"referral"`, `"who is hiring"`) across each target subreddit (`r/developersIndia`, `r/IndianStartups`, `r/ProductManagement`, `r/consulting`, `r/bangalore`).
- **D-04 (Error Resilience):** Graceful degradation on rate limits / network failure: on HTTP 429 or transient connection errors, the scanner serves cached posts, applies exponential backoff, logs warnings, and proceeds without crashing.
- **D-05 (Hybrid Entity Extraction):** Regex matching + Known Company dictionary matching + ATS URL pattern recognition (e.g. `greenhouse.io`, `lever.co`, `ashbyhq.com`), with optional free-tier LLM fallback for high-sentiment hiring threads where company name is ambiguous.
- **D-06 (Multi-ATS Prober):** Inspect HTML for embedded ATS signatures and probe canonical API endpoints concurrently (Greenhouse, Lever, Ashby, SmartRecruiters) using async HTTP with a 3.0s timeout.
- **D-07 (Target Auto-Registration):** Candidate employers verified with active ATS endpoints and >= 1 active job are automatically upserted into `career_targets` with `status='active'`, assigned standardized `role_focus` tags, and tagged with discovery metadata (`discovered_via='reddit'`).
- **D-08 (Probe Deduplication):** Slug-based deduplication against existing `career_targets` and a 7-day negative cache table (`probed_cache`) preventing repetitive probing of non-ATS domains.
- **D-09 (Catalog Dataset Partitioning):** 220+ Indian target companies partitioned across sector JSON seed files in `backend/app/data/targets/`:
  - `indian_startups.json` (150+ startups and unicorns)
  - `indian_conglomerates.json` (40+ conglomerates)
  - `strategy_consulting.json` (30+ consulting firms)
  Aggregated and loaded via `backend/scripts/seed_targets.py`.
- **D-10 (Standardized Role Focus):** Standardized enum taxonomy tags (`product`, `strategy`, `tech`, `founders_office`, `consulting`, `leadership`).
- **D-11 (Enterprise Portals):** Custom portals or enterprise ATS registered with direct career portal URLs and `ats_type='custom'` or `'workday'`.
- **D-12 (Idempotent Upsert):** `seed_targets.py` seeds with `status='active'` and `last_status='pending'`, preserving existing scrape timestamps and live job counts.

### Agent's Discretion
- Concurrency control via `asyncio.Semaphore(5)` for Reddit scraping and `asyncio.Semaphore(10)` for ATS probing.
- Exact regex patterns for URL and company mention parsing.
- Precise column structure for `discovery_cache` and `probed_cache`.

### Deferred Ideas (OUT OF SCOPE)
- Full continuous periodic scheduler and batch scraping runner (Phase 14).
- Frontend Career Directory Hub UI component (Phase 15).
</user_constraints>

<architectural_responsibility_map>
## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| `discovery_cache` & `probed_cache` SQLite Tables | Database/Storage | — | DDL in `backend/app/db/database.py` with TTL indexes. |
| Reddit Discovery Scanner | Backend Service | API/Backend | `backend/app/services/reddit_scanner.py` with httpx async client. |
| Entity Extractor & Multi-ATS Prober | Backend Service | External HTTP | `backend/app/services/discovery_prober.py` probing ATS endpoints. |
| Sector Partitioned Catalog Datasets | Static Data | Database/Storage | `backend/app/data/targets/*.json` (220+ target companies). |
| Catalog Seeder Refactor | Backend Script | Database/Storage | Updated `backend/scripts/seed_targets.py` loading partition files. |
| Discovery REST Endpoints | API/Backend | Backend Service | FastAPI router in `backend/app/api/discovery.py`. |
| CLI Discovery Runner | CLI/Script | Backend Service | `backend/scripts/run_discovery.py` for headless invocation. |
</architectural_responsibility_map>

<research_summary>
## Summary

Phase 12 builds an intelligent company discovery loop and dramatically expands CareerLoom's monitored company universe. While Phase 11 created the SQLite `career_targets` table and basic REST APIs, its catalog was limited to 51 Indian startups and 237 global firms. Phase 12 scales the catalog to 220+ Indian companies across three vital sectors: 150+ high-growth startups/unicorns, 40+ premier Indian conglomerates (Tata, Reliance, Infosys, Wipro, L&T, Mahindra), and 30+ elite strategy consulting firms (McKinsey, BCG, Bain, Kearney, Roland Berger, Big 4 India).

In parallel, Phase 12 automates new employer discovery by mining Reddit communities (`r/developersIndia`, `r/IndianStartups`, `r/ProductManagement`, `r/consulting`, `r/bangalore`). Unstructured posts are converted into candidate employers via regex and dictionary parsing, followed by high-speed concurrent probing of public ATS endpoints (Greenhouse, Lever, Ashby, SmartRecruiters). Verified targets are automatically enrolled in `career_targets` with 24-hour result caching and 7-day negative domain caching to prevent wasteful network requests.
</research_summary>

<standard_stack>
## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `httpx` | 0.28+ | Async HTTP Client | Fast concurrent connection pooling, custom headers, timeout support. |
| `aiosqlite` | 3.45+ | Async SQLite driver | Sub-millisecond local reads, WAL mode, transaction batching. |
| `BeautifulSoup4 + lxml` | 4.12+ | HTML signature parser | Detecting embedded ATS iframes/scripts without browser overhead. |
| `FastAPI` | 0.115+ | Web framework | High performance ASGI, automatic OpenAPI docs, Pydantic v2 validation. |
| `Pydantic v2` | 2.10+ | Schema validation | Type-safe DTOs for discovery feeds and probed targets. |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `re` (Python stdlib) | 3.11+ | Pattern extraction | Extracting ATS domains and company names from Reddit text. |
| `urllib.parse` | Python stdlib | URL normalization | Parsing domains, subdomains, and query parameters. |
</standard_stack>

<architecture_patterns>
## Architecture Patterns

### Reddit Discovery & ATS Probing State Machine
```
[Scheduled / Manual Trigger]
            |
            v
Check `discovery_cache` (TTL < 24h)
       /                 \
  [Hit: Cached]     [Miss / Expired]
      |                    |
      |             Fetch Reddit JSON (.json)
      |             (polite delay 1.0s, User-Agent)
      |                    |
      v                    v
  Extract Posts ---> Save to `discovery_cache`
            |
            v
  Extract Company Mentions & URLs (Regex + Dictionary)
            |
            v
  Filter existing `career_targets.slug` & `probed_cache` (7d TTL)
            |
            v
  Concurrent Multi-ATS Prober (asyncio.Semaphore(10), timeout 3s)
  - Greenhouse: boards-api.greenhouse.io/v1/boards/{slug}/jobs
  - Lever: api.lever.co/v0/postings/{slug}?mode=json
  - Ashby: api.ashbyhq.com/posting-api/job-board/{slug}
  - SmartRecruiters: api.smartrecruiters.com/v1/companies/{slug}/postings
       /                 \
  [Verified: 200]    [Non-ATS / 404]
      |                    |
      v                    v
Upsert `career_targets`   Insert `probed_cache` (expires in 7 days)
(status='active')
```

### Probed Cache Negative Filtering
```sql
CREATE TABLE IF NOT EXISTS probed_cache (
    domain_or_slug TEXT PRIMARY KEY,
    status TEXT NOT NULL,
    probed_at TEXT NOT NULL,
    expires_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_probed_expires ON probed_cache (expires_at);
```
</architecture_patterns>

<pitfalls_and_mitigations>
## Pitfalls & Mitigation

1. **Reddit HTTP 429 Rate Limits**:
   - *Pitfall*: Aggressive querying across 5 subreddits triggering Reddit rate limiting blocks.
   - *Mitigation*: Respect polite 1.0s interval, use custom User-Agent `CareerLoom-Discovery/1.0`, enforce 24h SQLite TTL cache, and fall back gracefully on existing cache on 429.
2. **False Positive Company Entity Extraction**:
   - *Pitfall*: Common words ("Startup", "Remote", "India", "Software") misidentified as company names.
   - *Mitigation*: Stop-word blocklist + Known Company dictionary matching + ATS verification probe gate (only enroll if ATS returns valid job feed).
3. **ATS Probing Timeouts**:
   - *Pitfall*: Slow external career servers hanging the scanner.
   - *Mitigation*: Strict 3.0s timeout per probe attempt using `httpx.Timeout(3.0)` and bounded concurrency (`asyncio.Semaphore(10)`).
4. **Duplicate Slugs & Catalog Drift**:
   - *Pitfall*: Seeding 220+ companies creating collisions or overwriting live job counts.
   - *Mitigation*: Idempotent upsert logic preserving `last_scraped_at`, `job_count`, and `last_status`.
</pitfalls_and_mitigations>

## Validation Architecture

### Automated Verification Gates
- `tests/test_reddit_discovery.py`:
  - Verify SQLite `discovery_cache` TTL write/read/expiration logic.
  - Verify `RedditDiscoveryService` mock fetching and graceful 429 handling.
  - Verify `DiscoveryEntityProber` regex extraction and ATS probe endpoints.
  - Verify negative cache `probed_cache` prevents redundant requests.
- `tests/test_catalog_scaling.py`:
  - Verify 220+ target companies load across startups, conglomerates, and consulting.
  - Verify `role_focus` enums and valid ATS types (`custom`, `greenhouse`, `lever`, `ashby`, `workday`).
  - Verify idempotent seed execution in `seed_targets.py` leaves existing job counts intact.

---
*Research completed: 2026-10-08 for Phase 12*
