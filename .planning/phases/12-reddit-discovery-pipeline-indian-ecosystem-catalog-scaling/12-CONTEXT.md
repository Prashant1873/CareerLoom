# Phase 12: Reddit Discovery Pipeline & Indian Ecosystem Catalog Scaling - Context

**Gathered:** 2026-10-08
**Status:** Ready for planning

<domain>
## Phase Boundary

Build an automated Reddit discovery scanner mining Indian tech & career communities (`r/developersIndia`, `r/IndianStartups`, `r/ProductManagement`, `r/consulting`, `r/bangalore`) with polite caching, an entity extraction and multi-ATS endpoint probe engine, and scale the Indian career registry catalog to 220+ companies across startups/unicorns, conglomerates, and strategy consulting firms.

</domain>

<decisions>
## Implementation Decisions

### Reddit Mining & Caching Engine
- **D-01:** System accesses target subreddits using the public Reddit JSON feed API (`.json`) with custom `CareerLoom-Discovery/1.0` User-Agent header, polite 1.0s delay between requests, and exponential backoff.
  — **Reversibility:** reversible — configuration parameter in Reddit discovery service.
- **D-02:** Scanned Reddit threads and payloads are cached in a dedicated SQLite table (`discovery_cache`) tracking `subreddit`, `post_id`, `payload`, `scanned_at`, and `expires_at` with a 24-hour TTL check to guarantee zero redundant network requests.
  — **Reversibility:** costly — introduces SQLite schema addition and migration table.
- **D-03:** Hybrid discovery query strategy: scanner fetches both recent top/hot threads and executes targeted keyword search queries (`"hiring"`, `"openings"`, `"careers"`, `"referral"`, `"who is hiring"`) across each target subreddit.
  — **Reversibility:** reversible — query list easily adjustable.
- **D-04:** Graceful degradation on rate limits / network failure: on HTTP 429 or transient connection errors, the scanner serves cached posts, applies exponential backoff, logs warnings, and proceeds to remaining subreddits without process aborts.
  — **Reversibility:** reversible — local exception handling.

### Entity Extraction & ATS Probing
- **D-05:** Hybrid entity extraction: thread titles and bodies are evaluated via Regex matching + Known Company dictionary matching + ATS URL pattern recognition (e.g. `greenhouse.io`, `lever.co`, `ashbyhq.com`), with optional fallback to free-tier LLM (Groq / Gemini) for high-sentiment hiring threads where company name is ambiguous.
  — **Reversibility:** reversible — modular parser pipeline.
- **D-06:** Multi-ATS Prober: for candidate company names or discovered career domains, inspect HTML for embedded ATS signatures (iframes, script tags) and probe canonical API endpoints concurrently (Greenhouse, Lever, Ashby, SmartRecruiters) using async HTTP with a tight 3.0s timeout.
  — **Reversibility:** reversible — prober utility functions.
- **D-07:** Auto-registration of verified targets: candidate employers verified with active ATS endpoints and >= 1 active job are automatically upserted into `career_targets` with `status='active'`, assigned standardized `role_focus` tags, and tagged with discovery metadata (`discovered_via='reddit'`).
  — **Reversibility:** costly — updates persistent `career_targets` table.
- **D-08:** Slug-based deduplication against existing `career_targets` and a 7-day negative cache table (`probed_cache`) preventing repetitive, wasteful probing of non-ATS domains or previously rejected candidates.
  — **Reversibility:** reversible — cache table and lookup logic.

### Catalog Scaling (220+ Targets)
- **D-09:** Catalog dataset organization: 220+ Indian target companies partitioned across sector JSON seed files in `backend/app/data/targets/`:
  - `indian_startups.json` (150+ startups and unicorns)
  - `indian_conglomerates.json` (40+ conglomerates: Tata, Reliance, Infosys, Wipro, L&T, Aditya Birla, Mahindra, etc.)
  - `strategy_consulting.json` (30+ consulting firms: McKinsey, BCG, Bain, Kearney, Roland Berger, Alvarez & Marsal, Big 4 India, etc.)
  Aggregated and loaded via `backend/scripts/seed_targets.py`.
  — **Reversibility:** costly — structured seed files powering initial DB population.
- **D-10:** Standardized enum role focus tags: targets are tagged with standardized taxonomy focus tags (`product`, `strategy`, `tech`, `founders_office`, `consulting`, `leadership`) aligned with upcoming Phase 13 taxonomy and Phase 15 filtering.
  — **Reversibility:** reversible — string enum arrays stored as JSON in `career_targets.role_focus`.
- **D-11:** Enterprise & Consulting target integration: firms with custom portals or enterprise ATS (Workday, SuccessFactors, custom portals) are registered with verified direct career portal landing page URLs and `ats_type='custom'` or `'workday'`, ensuring instant 1-click apply links and readiness for Phase 14 batch scrapers.
  — **Reversibility:** reversible — target metadata fields.
- **D-12:** Idempotent seed upsert semantics: `seed_targets.py` seeds all targets with `status='active'` and `last_status='pending'`, preserving existing scrape timestamps, sync statuses, and live job counts when re-run.
  — **Reversibility:** reversible — database upsert logic.

### Agent's Discretion
- Exact regex patterns for URL and company mention parsing.
- Specific async concurrency semaphore for Reddit scraping and ATS probing (e.g. `asyncio.Semaphore(5)` for Reddit, `asyncio.Semaphore(10)` for ATS prober).
- Exact table schema details for `discovery_cache` and `probed_cache`.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements & Roadmap
- `.planning/REQUIREMENTS.md` §Milestone v5 (DISCOVERY-01, DISCOVERY-02, DISCOVERY-03)
- `.planning/ROADMAP.md` §Phase 12
- `.planning/phases/11-career-targets-registry-database-architecture/11-CONTEXT.md` (Target schema D-01 to D-06)

### Existing Implementations
- `backend/app/services/reddit.py` (Existing Reddit public JSON service and subreddit mapping)
- `backend/app/models/target.py` (CareerTarget and TargetCreate Pydantic models)
- `backend/app/db/session.py` (SQLite schema initialization for `career_targets`)
- `backend/app/api/targets.py` (Target management REST endpoints)
- `backend/scripts/seed_targets.py` (Seeding CLI script)
- `backend/scripts/add_indian_companies.py` (Curated Indian startup seeds)
- `backend/app/data/companies.json` (Existing global company catalog)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `RedditCommunityService` in `backend/app/services/reddit.py`: existing `_search_reddit_public` method implementing public JSON fetching with custom headers and error handling.
- `career_targets` table in `backend/app/db/session.py`: table already equipped with `category_tier`, `role_focus`, `status`, `ats_type`, and `feed_url` columns.
- `upsert_target` and `get_target_by_slug` in `backend/app/db/session.py`: ready-to-use helpers for database persistence.

### Established Patterns
- SQLite async database access using `aiosqlite` with dict row factories.
- High-craft, modular service separation under `backend/app/services/`.
- Polite HTTP requests via `httpx.AsyncClient` with custom user-agents and timeouts.

### Integration Points
- REST endpoints in `backend/app/api/discovery.py` or `backend/app/api/targets.py` to trigger Reddit scans and view discovered candidate targets.
- Seeding pipeline in `backend/scripts/seed_targets.py` to ingest the scaled 220+ companies across the 3 new JSON files.

</code_context>

<specifics>
## Specific Ideas

- Ensure prominent coverage of tier-1 Indian management consulting offices (McKinsey India, BCG India, Bain India, Kearney India, Strategy& India, Alvarez & Marsal India, Dalberg, Samagra) and Indian conglomerates (Tata Sons, Tata Digital, Reliance Jio, Infosys, Wipro, L&T, Titan, ITC, Mahindra Digital).
- Combine quick-commerce, fintech, and AI unicorns (Zepto, Swiggy, Zomato, CRED, Groww, Meesho, Razorpay, PhonePe, Urban Company, Atlan, InMobi, Glance, Sarvam AI, SigNoz).

</specifics>

<deferred>
## Deferred Ideas

- None — discussion stayed within Phase 12 scope (DISCOVERY-01, DISCOVERY-02, DISCOVERY-03).

</deferred>

---

*Phase: 12-Reddit Discovery Pipeline & Indian Ecosystem Catalog Scaling*
*Context gathered: 2026-10-08*
