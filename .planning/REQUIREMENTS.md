# Requirements: CareerLoom (Global Job Discovery Engine)

**Defined:** 2026-10-03
**Core Value:** Empowers candidates to discover fresh, direct-from-source job listings across major global employers instantly using freeform natural language queries and category exploration, eliminating rigid keyword matching and ATS search friction.

## Validated Requirements (Milestones v1 – v4)

### Milestone v1: Core Engine & Ingestion (INGEST, NLP, FILTER, UI, SCRAPER, COMMUNITY)

- [x] **INGEST-01 to INGEST-05**: Direct ATS public API connectors (Greenhouse, Lever, Ashby), uniform `JobItem` normalization, ISO UTC timestamps, SQLite index, and on-demand live fetch.
- [x] **NLP-01 to NLP-05**: Freeform natural language query parser via Groq/Gemini/OpenRouter, heuristic regex fallback, broad category mapping, and LRU caching.
- [x] **FILTER-01 to FILTER-05**: Country/region, remote status, domain, freshness filtering, and chronological sorting.
- [x] **UI-01 to UI-05**: Responsive card-based UI conforming to `frontend-skill`, date badges, direct apply CTA, and local storage bookmarks.
- [x] **SCRAPER-01**: Custom enterprise crawler framework with polite BS4 scraping and lightweight LLM extraction.
- [x] **COMMUNITY-01, COMMUNITY-02**: Reddit community discussions and interview timeline extraction.

### Milestone v2: Desktop-Grade Control Center (V2-SHELL, V2-STREAM, V2-INSPECT, V2-AESTHETIC, V2-MOTION)

- [x] **V2-SHELL-01, V2-NAV-01**: 3-column split layout shell (collapsible nav rail, central stream, right inspector) with Obsidian Dark tokens.
- [x] **V2-STREAM-01, V2-KEYBOARD-01**: Sticky omnibox search, active filter chips, sort options, and keyboard cursor navigation (`J`/`K`/`S`/`Enter`).
- [x] **V2-INSPECT-01, V2-INSPECT-02**: Persistent right-side job inspector pane with embedded tabbed Reddit community intel.
- [x] **V2-AESTHETIC-01, V2-MOTION-01**: Obsidian Studio dark palette, hairline borders, and Apple HIG fluid spring physics.

### Milestone v3: Massive Global Portal Expansion (SCALE)

- [x] **SCALE-01 to SCALE-05**: 237-employer catalog across 5 global sectors, multi-ATS connector hardening, bulk sync runner, and 16k+ live listings in SQLite.

### Milestone v4: India Launch & Indian Leads Engine (INDIA)

- [x] **INDIA-CATALOG-01**: 51+ top Indian tech unicorns, startups, and GCCs cataloged with verified feeds.
- [x] **INDIA-INGEST-02**: 1,478 verified live Indian listings cached across 7 metro tech hubs (BLR, HYD, NCR, PUN, BOM, MAA, Remote-India).
- [x] **INDIA-DISCOVER-03, INDIA-CTC-04**: 1-click "India Direct" toggle, metro ribbon, and INR CTC compensation badges (₹ LPA).
- [x] **INDIA-LEADS-05**: Candidate lead capture modal with SQLite persistence, REST endpoints, and 1-click clipboard referral pitch generator.
- [x] **INDIA-COMMUNITY-06**: `r/developersIndia` community intel with 5-stage Indian hiring roadmap and interview turnaround metrics.

---

## Milestone v5 Requirements: Indian Career Repository & Continuous Batch Scraping Engine

### SQLite Career Targets Registry (REGISTRY)

- [ ] **REGISTRY-01**: System persists a dedicated `career_targets` table in SQLite tracking company name, slug, career page URL, ATS connector type, direct feed endpoint, tier/sector (Startup, Unicorn, Conglomerate, Consulting), role focus tags, sync health, last scraped timestamp, and active job count.
- [ ] **REGISTRY-02**: Seed loader migrates 200+ Indian companies and existing global catalog into the `career_targets` database table with initial sync health metadata.
- [ ] **REGISTRY-03**: Backend exposes REST endpoints for targets registry (`GET /api/targets`, `GET /api/targets/stats`, `POST /api/targets/seed`) with domain, tier, and status filtering.

### Reddit & Web Discovery Pipeline (DISCOVERY)

- [ ] **DISCOVERY-01**: Automated Reddit discovery scanner mines discussions in `r/developersIndia`, `r/IndianStartups`, `r/ProductManagement`, `r/consulting`, and `r/bangalore` for trending companies and hiring links.
- [ ] **DISCOVERY-02**: Entity normalization pipeline extracts company names, detects career URLs, and probes ATS endpoints (Ashby, Lever, Greenhouse, SmartRecruiters, Workday).
- [ ] **DISCOVERY-03**: Catalog scales to cover 150+ Indian startups/unicorns, 40+ Indian conglomerates (Tata, Reliance, Infosys, Wipro, L&T, etc.), and 30+ top strategy consulting firms (McKinsey, BCG, Bain, Kearney, Roland Berger, Alvarez & Marsal, Big 4 India).

### Product Management & Strategy Consulting Taxonomy (TAXONOMY)

- [ ] **TAXONOMY-01**: Ontology and track definition for Product Management roles (APM, PM, Senior PM, Group PM, VP Product, TPM, Product Operations) with semantic title synonyms.
- [ ] **TAXONOMY-02**: Ontology and track definition for Strategy & Consulting roles (Management Consultant, Strategy Analyst, Chief of Staff, Founder's Office, BizOps, Corporate Strategy).
- [ ] **TAXONOMY-03**: Semantic title classifier and multi-attribute search integration ensuring sub-50ms filtering on PM and Strategy Consulting tracks.

### High-Throughput Continuous Batch Scraping Engine (BATCH)

- [x] **BATCH-01**: High-throughput async batch scraping runner (`sync_batch.py`) executes concurrent fetching across all active career targets with bounded concurrency (`asyncio.Semaphore(15)`) and error isolation.
- [x] **BATCH-02**: Stale job reconciler detects closed/unlisted postings during sync passes, purging or archiving them to prevent ghost jobs.
- [x] **BATCH-03**: Continuous background scheduling service and API trigger (`POST /api/targets/sync`) for automated periodic updates and on-demand sync refreshes.

### Frontend Career Directory Hub & Role Experience (V5-UI)

- [ ] **V5-UI-01**: Obsidian dark Career Directory Hub view/modal displaying all indexed companies, verified career links, ATS badges, and live opening counts.
- [ ] **V5-UI-02**: Dedicated Product Management (🇮🇳 PM) and Strategy Consulting (🇮🇳 Strategy) 1-click quick-filters in the navigation rail and stream header.
- [ ] **V5-UI-03**: Real-time sync freshness indicators in the UI showing last sync timestamp and monitored company count.

---

## Out of Scope

Explicitly excluded to protect zero-cost model and project focus:

| Feature | Reason |
|---------|--------|
| Automated Bot Application Submission | High anti-bot risk, violates employer terms of service; all applications open official direct career portals. |
| Paid Third-Party Job Aggregator APIs | Incurs recurring monthly fees ($50-$200/mo); violates zero-cost requirement. |
| Heavy Enterprise Message Queues (Celery/Redis) | Heavy memory footprint requiring paid multi-container hosting; FastAPI + asyncio provides all needed concurrency for free. |
| User Authentication / Mandatory Paywall | Friction-free exploration; local storage and open discovery prioritized. |

---

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| REGISTRY-01, 02, 03 | Phase 11 | Complete |
| DISCOVERY-01, 02, 03 | Phase 12 | Complete |
| TAXONOMY-01, 02, 03 | Phase 13 | Complete |
| BATCH-01, 02, 03 | Phase 14 | Complete |
| V5-UI-01, 02, 03 | Phase 15 | Planned |

**Coverage:**

- Milestone v5 requirements: 15 total
- Mapped to phases: 15
- Unmapped: 0

---
*Requirements defined: 2026-10-08 for Milestone v5.0*
