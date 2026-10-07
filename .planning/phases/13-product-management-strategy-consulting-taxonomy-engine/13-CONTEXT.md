# Phase 13: Product Management & Strategy Consulting Taxonomy Engine - Context

**Gathered:** 2026-10-08
**Status:** Ready for planning

<domain>
## Phase Boundary

Expand the domain ontology, classification engine, and database search integration to deliver first-class coverage, semantic synonyms, and sub-50ms query filtering for Product Management and Strategy Consulting career tracks across global employers and Indian tech/consulting firms.

</domain>

<decisions>
## Implementation Decisions

### Role Track Taxonomy & Hierarchy
- **D-01:** Dedicated 6-Way Category Split: Promote high-visibility specializations into first-class standalone categories in `CATEGORIES_TAXONOMY`:
  - `product`: Core Product Management (APM, PM, Senior PM, GPM, VP/Director of Product, Growth PM, AI PM)
  - `technical_product`: Technical Product Management (TPM, Platform PM, Infrastructure PM, Core Tech PM)
  - `product_ops`: Product Operations (ProdOps, Program Manager - Product, Product Enablement)
  - `management_consulting`: Management Consulting (Management Consultant, Associate Consultant, Engagement Manager, Principal, Partner)
  - `corporate_strategy`: Corporate Strategy & Strategic Planning (Corporate Strategy Analyst, Strategic Planning, Venture Architecture, Strategic Investments)
  - `founders_office`: Founder's Office & Executive Operations (Founder's Office, Chief of Staff, Executive Operations, BizOps, Strategic Initiatives)
  — **Reversibility:** costly — updates `CATEGORIES_TAXONOMY` across backend and frontend category definitions.
- **D-02:** Domain Cluster Grouping with Alias Fallback: Granular categories are grouped into parent clusters (`product_cluster` for `product`, `technical_product`, `product_ops`; `strategy_cluster` for `management_consulting`, `corporate_strategy`, `founders_office`). Broad user queries like "product" or "strategy" match the entire cluster unless a specific category is explicitly requested.
  — **Reversibility:** reversible — helper resolver in taxonomy service.
- **D-03:** Unified Canonical Seniority with Role-Specific Deterministic Mapping: Retain canonical database seniority levels (`entry`, `mid`, `senior`, `lead`, `intern`) and map domain title patterns deterministically (e.g. APM -> entry, Associate Consultant / Strategy Analyst -> entry, Engagement Manager -> lead, Chief of Staff -> lead unless prefixed with Junior/Associate).
  — **Reversibility:** reversible — regex mapping rules in classifier.

### Semantic Classifier & Schema Extension
- **D-04:** Dedicated `track` Column in SQLite & JobItem: Extend SQLite `jobs` table schema with a `track TEXT` column and update `JobItem` model (`track: Optional[str] = None`) to persist exact detected tracks (e.g. 'Chief of Staff', 'APM', 'BizOps', 'TPM') alongside canonical `category` for faceted filtering and badge rendering.
  — **Reversibility:** one-way — database migration adding column and persistent model field.
- **D-05:** High-Performance Compiled Regex Classifier Engine: Upgraded `classify_role(title: str, company: Optional[str] = None, domain_hint: Optional[str] = None) -> Tuple[str, str, Optional[str]]` returning `(category, seniority, track)` powered by pure compiled regular expressions and keyword dictionaries (<0.1ms per title, zero API cost, 100% deterministic, offline-resilient).
  — **Reversibility:** reversible — modular utility in `backend/app/utils/classifier.py`.
- **D-06:** Context-Aware Classification with Employer Sector Hints: Classifier accepts company/domain hint; if employer is a Consulting firm or registered target with consulting focus, generic titles ('Associate', 'Business Analyst', 'Analyst') classify into `management_consulting` / `corporate_strategy` instead of general or finance.
  — **Reversibility:** reversible — lookup logic within classifier.
- **D-07:** Explicit Specific-Over-Broad Precedence Order: Role classification resolves with explicit collision priority: `founders_office` > `technical_product` > `product_ops` > `management_consulting` > `corporate_strategy` > generic `product` > `software_engineering` > `general`.
  — **Reversibility:** reversible — regex evaluation order in classifier.

### Sub-50ms Search & Query Expansion
- **D-08:** SQLite Composite B-Tree Indexes: Add composite index `idx_jobs_category_track` ON `jobs(category, track, is_active)` and single index `idx_jobs_track` ON `jobs(track)` to ensure sub-5ms query performance without FTS overhead.
  — **Reversibility:** costly — SQLite index definitions in `init_db`.
- **D-09:** Hybrid Track Querying with Synonym Fallback: In `query_jobs`, filtering by `track` filters primarily on the indexed `track = ?` column; if fewer than 5 results are returned, dynamically expand with track synonyms (`OR title LIKE ?`) to eliminate zero-result drop-offs.
  — **Reversibility:** reversible — SQL query builder logic in `database.py`.
- **D-10:** Fast-Path Taxonomy NLP Match Before LLM: Natural language search (`/api/nlp/search` and `/api/nlp/parse`) checks taxonomy tracks, categories, and regex patterns upfront (<20ms). If unambiguous track/metro match is found, returns structured query directly; only falls back to LLM (Groq/Gemini) if intent is ambiguous or query yields insufficient results.
  — **Reversibility:** reversible — router flow in `backend/app/api/nlp.py`.
- **D-11:** Enriched Tracks API with Live Job Counts: Extend `GET /api/categories/tracks` and add cluster metadata (`GET /api/categories/clusters`) returning track name, category ID, parent cluster, and cached active job counts for instant UI badge display.
  — **Reversibility:** reversible — REST endpoints in `backend/app/api/categories.py`.

### Job Catalog Backfill Migration
- **D-12:** Full Idempotent Re-classification: Backfill reclassifies all cached jobs in SQLite database table to populate new `track`, refine `category` into the 6 granular tracks, and align seniority in a single batch transaction.
  — **Reversibility:** costly — mutates persistent columns across jobs table.
- **D-13:** Automatic Startup Schema Migration + Standalone CLI Runner: `init_db()` automatically runs column check and adds `track` if missing, while a standalone script `backend/scripts/reclassify_jobs.py` provides on-demand CLI execution with detailed logging.
  — **Reversibility:** reversible — initialization code in `backend/app/db/database.py`.
- **D-14:** Detailed Observability Breakdown Table: Reclassification outputs a structured console table showing total jobs processed, counts per new category, top tracks detected, and elapsed execution time.
  — **Reversibility:** reversible — CLI script formatting.
- **D-15:** Non-Destructive Update with `--dry-run` Flag: Migration only mutates `category`, `seniority`, and `track`, preserving all job IDs, dates, URLs, and active flags; CLI supports `--dry-run` to preview distributions without committing.
  — **Reversibility:** reversible — CLI argument flag.

### Agent's Discretion
- Exact regex patterns and word boundary expressions for each new category and track.
- Number of track synonyms mapped per role track in `CATEGORIES_TAXONOMY`.
- In-memory caching TTL for category track job counts (e.g., 60 seconds).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements & Roadmap
- `.planning/REQUIREMENTS.md` §Milestone v5 (TAXONOMY-01, TAXONOMY-02, TAXONOMY-03)
- `.planning/ROADMAP.md` §Phase 13
- `.planning/phases/11-career-targets-registry-database-architecture/11-CONTEXT.md` (Target schema D-01 to D-06)
- `.planning/phases/12-reddit-discovery-pipeline-indian-ecosystem-catalog-scaling/12-CONTEXT.md` (Catalog scaling D-09 to D-12)

### Existing Implementations
- `backend/app/services/taxonomy.py` (Core taxonomy dictionary and match helpers)
- `backend/app/utils/classifier.py` (Role and seniority classification regex engine)
- `backend/app/models/job.py` (JobItem and JobFilterParams Pydantic schemas)
- `backend/app/db/database.py` (SQLite schema initialization and `query_jobs` engine)
- `backend/app/api/categories.py` (Categories and discovery tracks REST endpoints)
- `backend/app/api/nlp.py` (Conversational prompt parsing and NLP search router)
- `backend/app/services/llm_adapter.py` (Multi-provider LLM adapter with heuristic fallback)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `CATEGORIES_TAXONOMY` in `backend/app/services/taxonomy.py`: Structured dictionary providing metadata, tracks, synonyms, and related skills.
- `classify_role` in `backend/app/utils/classifier.py`: Centralized function already utilized across ATS connectors (Greenhouse, Lever, Ashby, Workday, SmartRecruiters) and scraper pipeline.
- `query_jobs` in `backend/app/db/database.py`: High-performance SQLite async query builder supporting pagination, faceted filtering, and sorting.
- `JobFilterParams` in `backend/app/models/job.py`: Pydantic request model with existing (previously unutilized) `synonyms` field.

### Established Patterns
- Pure Python compiled regexes for zero-latency, zero-cost classification.
- Idempotent SQLite migrations via `init_db()` (`CREATE TABLE IF NOT EXISTS`, column presence checks, `CREATE INDEX IF NOT EXISTS`).
- Fast async SQLite operations via `aiosqlite`.
- Modular FastAPI routers under `backend/app/api/`.

### Integration Points
- `backend/app/db/database.py`: Add `track TEXT` column migration and `idx_jobs_category_track` composite index; update `query_jobs` to support `params.track` and cluster-level queries.
- `backend/app/utils/classifier.py`: Expand `classify_role` to return `(category, seniority, track)` with employer context hints.
- `backend/app/services/taxonomy.py`: Add the 6 granular categories with clusters, curated tracks, and extensive synonyms.
- `backend/scripts/reclassify_jobs.py`: New standalone CLI script to backfill existing database jobs.
- `backend/app/api/categories.py`: Update endpoints to expose new categories, clusters, and live track counts.
- `backend/app/api/nlp.py`: Fast-path taxonomy matching before calling LLM adapter.

</code_context>

<specifics>
## Specific Ideas

- Ensure prominent tracks for:
  - PM: "Associate Product Manager (APM)", "Senior Product Manager", "Group Product Manager", "Director/VP Product", "AI Product Manager", "Growth Product Manager"
  - Technical PM: "Technical Product Manager (TPM)", "Platform Product Manager", "Data Product Manager"
  - Product Ops: "Product Operations Manager", "ProdOps Lead", "Product Program Manager"
  - Management Consulting: "Management Consultant", "Associate Consultant", "Engagement Manager", "Strategy Consultant", "Case Team Leader"
  - Corporate Strategy: "Corporate Strategy Analyst", "Strategic Planning Manager", "Venture Architect", "Strategy & Business Development"
  - Founder's Office: "Chief of Staff", "Founder's Office Associate", "Executive Operations Manager", "Business Operations (BizOps)"

</specifics>

<deferred>
## Deferred Ideas

- None — discussion stayed within phase scope.

</deferred>

---

*Phase: 13-Product Management & Strategy Consulting Taxonomy Engine*
*Context gathered: 2026-10-08*
