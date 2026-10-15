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

- [x] **REGISTRY-01**: System persists a dedicated `career_targets` table in SQLite tracking company name, slug, career page URL, ATS connector type, direct feed endpoint, tier/sector (Startup, Unicorn, Conglomerate, Consulting), role focus tags, sync health, last scraped timestamp, and active job count.
- [x] **REGISTRY-02**: Seed loader migrates 200+ Indian companies and existing global catalog into the `career_targets` database table with initial sync health metadata.
- [x] **REGISTRY-03**: Backend exposes REST endpoints for targets registry (`GET /api/targets`, `GET /api/targets/stats`, `POST /api/targets/seed`) with domain, tier, and status filtering.

### Reddit & Web Discovery Pipeline (DISCOVERY)

- [x] **DISCOVERY-01**: Automated Reddit discovery scanner mines discussions in `r/developersIndia`, `r/IndianStartups`, `r/ProductManagement`, `r/consulting`, and `r/bangalore` for trending companies and hiring links.
- [x] **DISCOVERY-02**: Entity normalization pipeline extracts company names, detects career URLs, and probes ATS endpoints (Ashby, Lever, Greenhouse, SmartRecruiters, Workday).
- [x] **DISCOVERY-03**: Catalog scales to cover 150+ Indian startups/unicorns, 40+ Indian conglomerates (Tata, Reliance, Infosys, Wipro, L&T, etc.), and 30+ top strategy consulting firms (McKinsey, BCG, Bain, Kearney, Roland Berger, Alvarez & Marsal, Big 4 India).

### Product Management & Strategy Consulting Taxonomy (TAXONOMY)

- [x] **TAXONOMY-01**: Ontology and track definition for Product Management roles (APM, PM, Senior PM, Group PM, VP Product, TPM, Product Operations) with semantic title synonyms.
- [x] **TAXONOMY-02**: Ontology and track definition for Strategy & Consulting roles (Management Consultant, Strategy Analyst, Chief of Staff, Founder's Office, BizOps, Corporate Strategy).
- [x] **TAXONOMY-03**: Semantic title classifier and multi-attribute search integration ensuring sub-50ms filtering on PM and Strategy Consulting tracks.

### High-Throughput Continuous Batch Scraping Engine (BATCH)

- [x] **BATCH-01**: High-throughput async batch scraping runner (`sync_batch.py`) executes concurrent fetching across all active career targets with bounded concurrency (`asyncio.Semaphore(15)`) and error isolation.
- [x] **BATCH-02**: Stale job reconciler detects closed/unlisted postings during sync passes, purging or archiving them to prevent ghost jobs.
- [x] **BATCH-03**: Continuous background scheduling service and API trigger (`POST /api/targets/sync`) for automated periodic updates and on-demand sync refreshes.

### Frontend Career Directory Hub & Role Experience (V5-UI)

- [x] **V5-UI-01**: Obsidian dark Career Directory Hub view/modal displaying all indexed companies, verified career links, ATS badges, and live opening counts.
- [x] **V5-UI-02**: Dedicated Product Management (🇮🇳 PM) and Strategy Consulting (🇮🇳 Strategy) 1-click quick-filters in the navigation rail and stream header.
- [x] **V5-UI-03**: Real-time sync freshness indicators in the UI showing last sync timestamp and monitored company count.

---

## Milestone v6 Requirements: Obsidian Light & Dual-Theme Ergonomics

### Dual-Theme Token Architecture & WCAG 2.2 AA Contrast (Phase 16)

- [x] **THEME-TOKEN-01**: Define dual-theme semantic CSS variables in `frontend/src/index.css` under `:root, [data-theme="dark"]` and `[data-theme="light"]`, deploying an Obsidian Porcelain canvas (`#f8fafc`), pure white surfaces (`#ffffff`), elevated slate panels, and subtle borders.
- [x] **THEME-CONTRAST-02**: Enforce WCAG 2.2 AA contrast compliance across all text tiers (primary `#0f172a` > 14:1, secondary `#334155` > 8:1, muted `#64748b` > 4.5:1) and calibrate light mode primary accent to emerald `#047857` (5.48:1 on white).
- [x] **THEME-BADGE-03**: Calibrate dual-theme semantic badge colors (Domain, Remote, Tier, Match, Compensation) using soft pastel backgrounds and deep saturated text to guarantee >4.5:1 readability on light mode.
- [x] **THEME-REFACTOR-04**: Eliminate hardcoded dark hex color values (`#080b11`, `#0e131f`, `#121826`, `#0d121c`) across `App.css` and `CareerDirectoryModal.css`, mapping them cleanly to semantic tokens.

### Theme Switcher, Component Retheming & Fluid Transitions (Phase 17)

- [x] **THEME-TOGGLE-05**: Implement accessible, viscoelastic theme toggle control with sun/moon icons and Apple fluid spring kinetics in `NavRail.tsx` and `Header.tsx`.
- [x] **THEME-HYDRATE-06**: Prevent flash of unstyled theme (FOUC) by synchronizing theme state in `localStorage` with `prefers-color-scheme` media query in initial HTML render and React `useTheme` hook.
- [x] **THEME-SURFACE-07**: Complete end-to-end component retheming across 3-Column Shell, Master Job Stream, Job Cards, Inspector Pane, Lead Modal, and Career Directory Hub.

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
| REGISTRY-01 | Phase 11 | Complete |
| REGISTRY-02 | Phase 11 | Complete |
| REGISTRY-03 | Phase 11 | Complete |
| DISCOVERY-01 | Phase 12 | Complete |
| DISCOVERY-02 | Phase 12 | Complete |
| DISCOVERY-03 | Phase 12 | Complete |
| TAXONOMY-01 | Phase 13 | Complete |
| TAXONOMY-02 | Phase 13 | Complete |
| TAXONOMY-03 | Phase 13 | Complete |
| BATCH-01 | Phase 14 | Complete |
| BATCH-02 | Phase 14 | Complete |
| BATCH-03 | Phase 14 | Complete |
| V5-UI-01 | Phase 15 | Complete |
| V5-UI-02 | Phase 15 | Complete |
| V5-UI-03 | Phase 15 | Complete |
| THEME-TOKEN-01 | Phase 16 | Complete |
| THEME-CONTRAST-02 | Phase 16 | Complete |
| THEME-BADGE-03 | Phase 16 | Complete |
| THEME-REFACTOR-04 | Phase 16 | Complete |
| THEME-TOGGLE-05 | Phase 17 | Complete |
| THEME-HYDRATE-06 | Phase 17 | Complete |
| THEME-SURFACE-07 | Phase 17 | Complete |

**Coverage:**

- Milestone v6 requirements: 7 total
- Mapped to phases: 7
- Unmapped: 0

---
*Requirements updated: 2026-10-16 for Milestone v6.0*
