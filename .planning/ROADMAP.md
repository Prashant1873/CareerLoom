# Roadmap: CareerLoom (Global Job Discovery Engine)

## Overview

CareerLoom delivers a zero-friction job discovery portal across major global firms. The roadmap progresses through five vertical MVP phases in Milestone v1 (core ATS ingestion, NLP query engine, high-craft React UI, custom scrapers, Reddit insights), Milestone v2 (Obsidian 3-column control center), Milestone v3 (global 200+ company expansion), Milestone v4 (India launch & leads engine), and Milestone v5 (Indian career repository, Reddit-driven discovery, PM & Strategy Consulting specialization, and continuous batch scraping).

## Phases

**Phase Numbering:**

- Integer phases (1 to 15): Planned milestone work
- Decimal phases: Urgent insertions

### Milestone v1: Core Engine & Ingestion

- [x] **Phase 1: Ingestion Engine & ATS Direct Feeds** - Direct API connectors (Greenhouse, Lever, Ashby), uniform `JobItem` normalization, UTC date parsing, and SQLite caching.
- [x] **Phase 2: Natural Language Query & Filter Engine** - Multi-provider free LLM query parser (Groq / Gemini), heuristic rule fallback, category exploration, and multi-attribute SQL search.
- [x] **Phase 3: High-Craft Frontend UI & Card Experience** - Modern React/Vite UI, conversational search bar, category quick-pills, faceted filter sidebar, and job card grid with prominent posting dates.
- [x] **Phase 4: Custom Enterprise Portal Scrapers** - Extensible crawler pipeline with BeautifulSoup4 and lightweight LLM extractor for non-ATS enterprise career portals.
- [x] **Phase 5: Community Intelligence (Reddit Insights)** - Reddit and public forum sentiment scraper for interview timelines, turnaround stages, and authentic company reviews.

### Milestone v2: Desktop-Grade Control Center

- [x] **Phase 6: Obsidian Design System & 3-Column Shell** - Obsidian Studio dark tokens, 3-column layout shell, and collapsible left navigation rail.
- [x] **Phase 7: Master Job Stream & Keyboard Navigation Flow** - Sticky omnibox, active chips, and keyboard cursor navigation.
- [x] **Phase 8: Persistent Job Inspector & Embedded Community Intel** - Persistent right-side inspector pane with embedded tabbed Reddit community intel.

### Milestone v3: Massive Global Portal Expansion

- [x] **Phase 9: Massive Global Portal Expansion & Multi-ATS Ingestion (200+ Firms)** - Scale company catalog across 5 major global sectors and bulk-ingest thousands of live job listings into SQLite cache.

### Milestone v4: India Launch & Indian Leads Engine

- [x] **Phase 10: India Launch & Indian Leads Engine** - Curate 50+ Indian unicorns & GCCs, India-First discovery controls, CTC compensation badges, candidate lead capture & referral engine, and r/developersIndia community intel.

### Milestone v5: Indian Career Repository & Continuous Batch Scraping Engine

- [x] **Phase 11: Career Targets Registry & Database Architecture** - Persistent SQLite schema (`career_targets`), REST API management endpoints, seed migration, and stale job reconciler.
- [x] **Phase 12: Reddit Discovery Pipeline & Indian Ecosystem Catalog Scaling** - Reddit scanner (`r/developersIndia`, `r/IndianStartups`, `r/ProductManagement`, `r/consulting`), candidate company extractor, and 200+ Indian company expansion.
- [x] **Phase 13: Product Management & Strategy Consulting Taxonomy Engine** - Domain ontology expansion, APM/PM and Strategy Consulting role track mapping, and sub-50ms filtering.
- [x] **Phase 14: Continuous Batch Scraping Pipeline & Ingestion Automation** - High-concurrency async batch runner (`sync_batch.py`), scheduled periodic worker, and error isolation. (completed 2026-10-08)
- [ ] **Phase 15: Frontend Career Directory Hub & Role Experience** - Obsidian dark Career Directory modal/view, 1-click PM and Strategy filter ribbons, and live sync indicators.

---

## Phase Details

### Phase 11: Career Targets Registry & Database Architecture

**Goal**: Implement a persistent SQLite registry table (`career_targets`) for tracking hundreds of company career portal URLs, ATS providers, sync health, and scrape metrics, backed by REST API management endpoints and initial seed migration.
**Mode**: mvp
**Depends on**: Phase 10
**Requirements**: REGISTRY-01, REGISTRY-02, REGISTRY-03
**Success Criteria**:

  1. `career_targets` table initialized in SQLite with composite indexes for status, tier, and last scraped timestamp.
  2. Seed migrator populates 200+ Indian employers and existing global companies into the registry with verified career URLs.

**Plans**: 2 plans
Plans:

- [x] 11-01: SQLite Schema Extension, Target Models, and Stale Job Reconciler
- [x] 11-02: Catalog Seeder & REST API Management Endpoints

### Phase 12: Reddit Discovery Pipeline & Indian Ecosystem Catalog Scaling

**Goal**: Build an automated Reddit discovery engine scanning `r/developersIndia`, `r/IndianStartups`, `r/ProductManagement`, `r/consulting`, and `r/bangalore` to mine company mentions, discover career portals, and scale Indian coverage to 200+ companies across startups, conglomerates, and consulting firms.
**Mode**: mvp
**Depends on**: Phase 11
**Requirements**: DISCOVERY-01, DISCOVERY-02, DISCOVERY-03
**Success Criteria**:

  1. Async Reddit scanner queries target subreddits using custom User-Agent headers, with 24h caching.
  2. Candidate company extractor parses company mentions, identifies career URLs, and automatically probes ATS endpoints.
  3. Career registry scales to 200+ Indian companies spanning Startups/Unicorns, Indian Conglomerates (Tata, Reliance, Infosys, etc.), and Strategy Consulting firms (McKinsey, BCG, Bain, Kearney, etc.).

**Plans**: 2 plans
Plans:

- [x] 12-01: Reddit Discovery Scanner, Caching Engine & Multi-ATS Prober Pipeline
- [x] 12-02: Ecosystem Catalog Scaling (220+ Targets) & Seed Partitioning

### Phase 13: Product Management & Strategy Consulting Taxonomy Engine

**Goal**: Expand the domain ontology and classification engine to provide first-class coverage and sub-50ms filtering for Product Management and Strategy Consulting career tracks.
**Mode**: mvp
**Depends on**: Phase 12
**Requirements**: TAXONOMY-01, TAXONOMY-02, TAXONOMY-03
**Success Criteria**:

  1. Taxonomy ontology extended with granular Product Management tracks (APM, PM, Senior PM, Group PM, VP Product, TPM, ProdOps) and synonyms.
  2. Taxonomy ontology extended with Strategy & Consulting tracks (Management Consultant, Strategy Analyst, Chief of Staff, Founder's Office, BizOps, Corporate Strategy).
  3. Query parser and database filter return matching PM and Strategy Consulting jobs in under 50ms without title mismatch drop-offs.

**Plans**: 2 plans
Plans:

- [x] 13-01: Domain Ontology Expansion, Sub-0.1ms Regex Classifier & Model Extension
- [x] 13-02: Sub-50ms Search Engine, SQLite Indexing, NLP Fast-Path & Catalog Backfill

### Phase 14: Continuous Batch Scraping Pipeline & Ingestion Automation

**Goal**: Build an async, bounded-concurrency batch scraping engine (`sync_batch.py`) that iterates through all registered career targets, extracts live postings, prunes stale/closed jobs, and supports background scheduled execution.
**Mode**: mvp
**Depends on**: Phase 13
**Requirements**: BATCH-01, BATCH-02, BATCH-03
**Success Criteria**:

  1. Batch runner scrapes hundreds of career targets concurrently with bounded concurrency (`asyncio.Semaphore(15)`) and polite per-host delays.
  2. Stale job reconciler detects closed listings and purges/flags them, eliminating dead links and ghost jobs.
  3. API trigger (`POST /api/targets/sync`) and continuous background worker run reliably with isolated error handling.

**Plans**: 2 plans
Plans:

- [x] 14-01: Batch Scraping Core Engine, Stale Job Reconciler & CLI Runner
- [x] 14-02: Background Scheduler Service, REST API Endpoints & Lifespan Automation

### Phase 15: Frontend Career Directory Hub & Role Experience

**Goal**: Deliver an Obsidian dark Career Directory Hub view displaying all monitored companies and live portals, with 1-click filter ribbons for Product Management and Strategy Consulting and live sync indicators.
**Mode**: mvp
**Depends on**: Phase 14
**Requirements**: V5-UI-01, V5-UI-02, V5-UI-03
**Success Criteria**:

  1. Career Directory Hub allows users to browse all indexed companies, filter by tier/domain, and view verified direct career links.
  2. Left navigation rail and omnibox stream header provide 1-click filters for "Product Management (India)" and "Strategy & Consulting (India)".
  3. UI displays real-time sync status ("Monitored 220+ Companies", "Last Synced X mins ago").

**Plans**: 2 plans
Plans:

- [x] 15-01: Career Targets TypeScript Models, API Client & CareerDirectoryModal Component
- [x] 15-02: 1-Click Role Track Quick-Filter Ribbons, Sync Freshness Indicators & Shell Integration

---

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12 → 13 → 14 → 15

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Ingestion Engine & ATS Direct Feeds | 3/3 | Complete | 2026-10-03 |
| 2. Natural Language Query & Filter Engine | 3/3 | Complete | 2026-10-03 |
| 3. High-Craft Frontend UI & Card Experience | 3/3 | Complete | 2026-10-03 |
| 4. Custom Enterprise Portal Scrapers | 2/2 | Complete | 2026-10-03 |
| 5. Community Intelligence (Reddit Insights) | 2/2 | Complete | 2026-10-03 |
| 6. Obsidian Design System & 3-Column Shell | 1/1 | Complete | 2026-10-03 |
| 7. Master Job Stream & Keyboard Flow | 1/1 | Complete | 2026-10-03 |
| 8. Persistent Job Inspector & Community Intel | 1/1 | Complete | 2026-10-03 |
| 9. Massive Global Portal Expansion | 3/3 | Complete | 2026-10-03 |
| 10. India Launch & Indian Leads Engine | 4/4 | Complete | 2026-10-03 |
| 11. Career Targets Registry & Database Architecture | 2/2 | Complete | 2026-10-08 |
| 12. Reddit Discovery Pipeline & Indian Ecosystem Catalog Scaling | 2/2 | Complete | 2026-10-08 |
| 13. Product Management & Strategy Consulting Taxonomy Engine | 2/2 | Complete | 2026-10-08 |
| 14. Continuous Batch Scraping Pipeline & Ingestion Automation | 2/2 | Complete    | 2026-10-08 |
| 15. Frontend Career Directory Hub & Role Experience | 2/2 | Complete | 2026-10-08 |
