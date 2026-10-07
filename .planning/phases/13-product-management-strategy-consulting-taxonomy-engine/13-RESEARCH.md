# Phase 13: Product Management & Strategy Consulting Taxonomy Engine - Research

**Researched:** 2026-10-08
**Domain:** Role Track Ontology, Regex Token Classification, SQLite Composite Indexing, Query Expansion, NLP Fast-Path Routing, Database Migration & Backfill
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01 (Dedicated 6-Way Category Split):** Promote high-visibility specializations into first-class standalone categories in `CATEGORIES_TAXONOMY`:
  - `product`: Core Product Management (APM, PM, Senior PM, GPM, VP/Director of Product, Growth PM, AI PM)
  - `technical_product`: Technical Product Management (TPM, Platform PM, Infrastructure PM, Core Tech PM)
  - `product_ops`: Product Operations (ProdOps, Program Manager - Product, Product Enablement)
  - `management_consulting`: Management Consulting (Management Consultant, Associate Consultant, Engagement Manager, Principal, Partner)
  - `corporate_strategy`: Corporate Strategy & Strategic Planning (Corporate Strategy Analyst, Strategic Planning, Venture Architecture, Strategic Investments)
  - `founders_office`: Founder's Office & Executive Operations (Founder's Office, Chief of Staff, Executive Operations, BizOps, Strategic Initiatives)
- **D-02 (Domain Cluster Grouping with Alias Fallback):** Granular categories are grouped into parent clusters (`product_cluster` for `product`, `technical_product`, `product_ops`; `strategy_cluster` for `management_consulting`, `corporate_strategy`, `founders_office`). Broad user queries like "product" or "strategy" match the entire cluster unless a specific category is explicitly requested.
- **D-03 (Unified Canonical Seniority with Role-Specific Mapping):** Retain canonical database seniority levels (`entry`, `mid`, `senior`, `lead`, `intern`) and map domain title patterns deterministically (e.g. APM -> entry, Associate Consultant / Strategy Analyst -> entry, Engagement Manager -> lead, Chief of Staff -> lead unless prefixed with Junior/Associate).
- **D-04 (Dedicated `track` Column in SQLite & JobItem):** Extend SQLite `jobs` table schema with a `track TEXT` column and update `JobItem` model (`track: Optional[str] = None`) to persist exact detected tracks (e.g. 'Chief of Staff', 'APM', 'BizOps', 'TPM') alongside canonical `category` for faceted filtering and badge rendering.
- **D-05 (High-Performance Compiled Regex Classifier Engine):** Upgraded `classify_role(title: str, company: Optional[str] = None, domain_hint: Optional[str] = None) -> Tuple[str, str, Optional[str]]` returning `(category, seniority, track)` powered by pure compiled regular expressions and keyword dictionaries (<0.1ms per title, zero API cost, 100% deterministic, offline-resilient).
- **D-06 (Context-Aware Classification with Employer Sector Hints):** Classifier accepts company/domain hint; if employer is a Consulting firm or registered target with consulting focus, generic titles ('Associate', 'Business Analyst', 'Analyst') classify into `management_consulting` / `corporate_strategy` instead of general or finance.
- **D-07 (Explicit Specific-Over-Broad Precedence Order):** Role classification resolves with explicit collision priority: `founders_office` > `technical_product` > `product_ops` > `management_consulting` > `corporate_strategy` > generic `product` > `software_engineering` > `general`.
- **D-08 (SQLite Composite B-Tree Indexes):** Add composite index `idx_jobs_category_track` ON `jobs(category, track, is_active)` and single index `idx_jobs_track` ON `jobs(track)` to ensure sub-5ms query performance without FTS overhead.
- **D-09 (Hybrid Track Querying with Synonym Fallback):** In `query_jobs`, filtering by `track` filters primarily on the indexed `track = ?` column; if fewer than 5 results are returned, dynamically expand with track synonyms (`OR title LIKE ?`) to eliminate zero-result drop-offs.
- **D-10 (Fast-Path Taxonomy NLP Match Before LLM):** Natural language search (`/api/nlp/search` and `/api/nlp/parse`) checks taxonomy tracks, categories, and regex patterns upfront (<20ms). If unambiguous track/metro match is found, returns structured query directly; only falls back to LLM (Groq/Gemini) if intent is ambiguous or query yields insufficient results.
- **D-11 (Enriched Tracks API with Live Job Counts):** Extend `GET /api/categories/tracks` and add cluster metadata (`GET /api/categories/clusters`) returning track name, category ID, parent cluster, and cached active job counts for instant UI badge display.
- **D-12 (Full Idempotent Re-classification):** Backfill reclassifies all cached jobs in SQLite database table to populate new `track`, refine `category` into the 6 granular tracks, and align seniority in a single batch transaction.
- **D-13 (Automatic Startup Schema Migration + Standalone CLI Runner):** `init_db()` automatically runs column check and adds `track` if missing, while a standalone script `backend/scripts/reclassify_jobs.py` provides on-demand CLI execution with detailed logging.
- **D-14 (Detailed Observability Breakdown Table):** Reclassification outputs a structured console table showing total jobs processed, counts per new category, top tracks detected, and elapsed execution time.
- **D-15 (Non-Destructive Update with `--dry-run` Flag):** Migration only mutates `category`, `seniority`, and `track`, preserving all job IDs, dates, URLs, and active flags; CLI supports `--dry-run` to preview distributions without committing.

### Agent's Discretion
- Word boundary regexes and exact token matching logic.
- In-memory 60s cache on track live job counts.
- Exact styling and formatting of CLI breakdown summary table.

### Deferred Ideas (OUT OF SCOPE)
- Continuous scheduled batch sync worker (Phase 14).
- Dedicated Obsidian Dark frontend Career Directory Hub & 1-click filter ribbons (Phase 15).
</user_constraints>

<architectural_responsibility_map>
## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Ontology Taxonomy & Cluster Metadata | Backend Service | API/Backend | `backend/app/services/taxonomy.py` defining 6-way categories, clusters, synonyms, and skills. |
| Role & Track Classifier | Utilities / Scrapers | Ingestion Feeds | `backend/app/utils/classifier.py` returning `(category, seniority, track)` with sector hints. |
| Job Model & Filter Schemas | Data Models | API/Backend | `backend/app/models/job.py` extending `JobItem` and `JobFilterParams` with `track`. |
| Database DDL, Indexing & Query Engine | Database / Storage | API/Backend | `backend/app/db/database.py` adding `track` column, B-Tree indexes, cluster search, and hybrid fallback. |
| Categories & Tracks REST Endpoints | API/Backend | Backend Service | `backend/app/api/categories.py` exposing clusters and live track job counts. |
| NLP Fast-Path Router | API/Backend | Backend Service | `backend/app/api/nlp.py` prioritizing taxonomy match before LLM API calls. |
| Ingestion Connector Normalization | Scrapers | Backend Service | ATS connectors (`greenhouse`, `lever`, `ashby`, `workday`, `smartrecruiters`, `llm_scraper`) passing `track`. |
| Reclassification CLI & Migration Runner | Backend Script | Database / Storage | `backend/scripts/reclassify_jobs.py` for idempotent full DB backfill with `--dry-run`. |
</architectural_responsibility_map>

<research_summary>
## Summary

CareerLoom's primary value proposition is eliminating keyword search friction and ATS matching drop-offs. Prior to Phase 13, roles were classified into 8 coarse categories where high-demand roles like Chief of Staff, Founder's Office, APM, and TPM were either lumped into generic buckets or lost.

Phase 13 establishes a high-craft taxonomy engine delivering:
1. **Granular 6-Way Category Expansion**: First-class categories for `product`, `technical_product`, `product_ops`, `management_consulting`, `corporate_strategy`, and `founders_office`.
2. **Domain Clusters**: Parent clusters (`product_cluster`, `strategy_cluster`) enabling both broad umbrella searches and micro-track filtering without breaking backwards compatibility.
3. **Sub-0.1ms Regex Classification**: High-throughput rule engine supporting company sector hints to disambiguate consulting titles and resolve collisions via strict priority.
4. **Sub-50ms Query Performance**: Backed by SQLite composite B-Tree indexes (`category, track, is_active`), hybrid track synonym fallback, and fast-path natural language parsing that bypasses 500ms LLM latency for unambiguous queries.
5. **Safe Catalog Backfill**: Migration of 16,000+ cached jobs with non-destructive in-place updates, `--dry-run` inspection, and structured observability logging.
</research_summary>

<standard_stack>
## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `re` (Python stdlib) | 3.11+ | Compiled Regex Pattern Engine | Sub-0.1ms evaluation per title, 0 API cost, deterministic unit testing. |
| `aiosqlite` | 3.45+ | Async SQLite Driver | High concurrency reads, sub-millisecond B-Tree lookups, atomic transactions. |
| `FastAPI` | 0.115+ | REST API Framework | Automatic OpenAPI docs, native Pydantic v2 validation. |
| `Pydantic v2` | 2.10+ | Model & Parameter Validation | Strict type checks for `track` and filter parameters. |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `asyncio` | Python stdlib | Concurrency & Async Context | Executing async database queries and scripts. |
| `argparse` | Python stdlib | CLI Argument Parsing | Command-line flags (`--dry-run`, `--batch-size`) in `reclassify_jobs.py`. |
</standard_stack>

<architecture_patterns>
## Architecture Patterns

### Pattern 1: Fast-Path Taxonomy Query Resolution
```
[User Query / Prompt]
         |
         v
[match_category_phrase(prompt)] <--- Regex + Taxonomy Tracks (<1ms)
         |
    +----+----+
    |         |
 [Match]   [No Match / Ambiguous]
    |         |
    |         v
    |     [parse_natural_language_query] (LLM Adapter: Groq/Gemini ~500ms)
    |         |
    +----+----+
         |
         v
[query_jobs(filter_params)]
         |
    [track = ?] (Composite B-Tree index <5ms)
         |
   (Total < 5?)
    /        \
  [No]       [Yes]
   |           |
   |      Expand with Track Synonyms (OR title LIKE ?)
   |           |
   +-----+-----+
         |
         v
[Ranked Results (<20-50ms total)]
```

### Pattern 2: Category Precedence Hierarchy
When multiple pattern matches collide, resolve via:
1. `founders_office` (Chief of Staff, Founder's Office, BizOps)
2. `technical_product` (TPM, Platform PM, Core Infrastructure PM)
3. `product_ops` (Product Operations, ProdOps, Product Program Manager)
4. `management_consulting` (Management Consultant, Engagement Manager, Consulting Associate)
5. `corporate_strategy` (Corporate Strategy, Strategic Planning, CorpDev)
6. `product` (Product Manager, APM, Senior PM, GPM)
7. `software_engineering` / `data_ai` / other tech categories
8. `general` fallback
</architecture_patterns>

<pitfalls_and_landmines>
## Pitfalls and Landmines

### 1. Title Overlap Collisions
- **Issue**: "Technical Product Manager" contains "Product Manager". If `product` pattern evaluates before `technical_product`, it gets misclassified.
- **Mitigation**: Strict precedence chain evaluates specialized categories (`technical_product`, `product_ops`, `founders_office`) before general ones (`product`, `consulting_strategy`).

### 2. Consulting Firm Generic Role Names
- **Issue**: Firms like McKinsey, BCG, or Bain list roles simply as "Associate", "Business Analyst", or "Senior Practice Manager". In tech, "Business Analyst" could be IT or operations.
- **Mitigation**: Classifier checks `company` or `domain_hint`. If the company matches consulting registry targets (e.g. McKinsey, BCG, Bain, Kearney, Roland Berger, Alvarez & Marsal, Big 4), generic business analyst / associate roles classify into `management_consulting`.

### 3. Database Migration Locking
- **Issue**: Adding a column or updating thousands of rows while the server is active can cause SQLite database locks (`database is locked`).
- **Mitigation**: Use a single transaction with `BEGIN IMMEDIATE` / batch updates (`executemany`) with `WAL` mode already active in `database.py`.

### 4. Zero-Result Drop-Offs on Rare Track Titles
- **Issue**: A user specifically selects "Corporate Strategy" or "Chief of Staff", but strict equality misses slight spelling differences like "Chief-of-Staff" or "Founder's Associate".
- **Mitigation**: D-09 hybrid fallback expands with known synonyms if exact track match yields fewer than 5 listings.
</pitfalls_and_landmines>

<validation_strategy_preview>
## Validation Strategy Preview

1. **Unit Tests for Classifier**:
   - `test_pm_classification`: APM, Senior PM, TPM, ProdOps, VP Product -> verify category, seniority, and track.
   - `test_strategy_consulting_classification`: Chief of Staff, Founder's Office, Management Consultant, Corporate Strategy, BizOps -> verify category, seniority, and track.
   - `test_consulting_employer_hints`: "Associate" at "McKinsey & Company" -> `management_consulting`; "Associate" at "Google" -> `general` or `entry`.
2. **Database & Index Performance Tests**:
   - Verify `track` column presence in SQLite `jobs` table.
   - Benchmark `query_jobs` latency with `track` and `category` filters (<25ms).
3. **API & NLP Fast-Path Tests**:
   - `GET /api/categories`: returns 6 new categories + clusters.
   - `GET /api/categories/tracks`: returns all tracks with live active job counts.
   - `POST /api/nlp/parse` with "entry level product manager in bangalore" -> verifies fast-path returns <50ms without LLM timeout.
4. **Backfill Script Verification**:
   - Run `python backend/scripts/reclassify_jobs.py --dry-run` to preview distributions.
   - Run `python backend/scripts/reclassify_jobs.py` to execute live backfill and verify non-zero PM/Strategy job counts in database.
</validation_strategy_preview>
