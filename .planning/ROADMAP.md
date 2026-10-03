# Roadmap: CareerLoom (Global Job Discovery Engine)

## Overview

CareerLoom delivers a zero-friction job discovery portal across major global firms. The roadmap progresses through five vertical MVP phases: first establishing reliable data ingestion from direct ATS feeds (Greenhouse, Lever, Ashby) into SQLite, adding the multi-provider natural language query and filtering engine, building the high-craft card-based UI adhering to `frontend-skill`, extending coverage to custom enterprise career sites via scrapers, and integrating community intelligence (Reddit reviews and interview timelines).

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3, 4, 5): Planned milestone work
- Decimal phases: Urgent insertions

- [x] **Phase 1: Ingestion Engine & ATS Direct Feeds** - Direct API connectors (Greenhouse, Lever, Ashby), uniform `JobItem` normalization, UTC date parsing, and SQLite caching.
- [x] **Phase 2: Natural Language Query & Filter Engine** - Multi-provider free LLM query parser (Groq / Gemini), heuristic rule fallback, category exploration, and multi-attribute SQL search.
- [x] **Phase 3: High-Craft Frontend UI & Card Experience** - Modern React/Vite UI, conversational search bar, category quick-pills, faceted filter sidebar, and job card grid with prominent posting dates.
- [x] **Phase 4: Custom Enterprise Portal Scrapers** - Extensible crawler pipeline with BeautifulSoup4 and lightweight LLM extractor for non-ATS enterprise career portals.
- [x] **Phase 5: Community Intelligence (Reddit Insights)** - Reddit and public forum sentiment scraper for interview timelines, turnaround stages, and authentic company reviews.

## Phase Details


### Phase 1: Ingestion Engine & ATS Direct Feeds
**Goal**: Ingest verified job listings directly from public ATS endpoints across top global employers, normalize to a uniform schema with reliable posting dates, and cache in SQLite for sub-50ms queries.
**Mode**: mvp
**Depends on**: Nothing
**Requirements**: INGEST-01, INGEST-02, INGEST-03, INGEST-04, INGEST-05
**Success Criteria**:
  1. System fetches structured public job postings from Greenhouse, Lever, and Ashby APIs across seeded top firms.
  2. Postings are normalized into `JobItem` schema with valid UTC `date_posted` timestamps.
  3. Listings are indexed into embedded SQLite and searchable in under 50ms.
  4. On-demand live fetch updates a target company's listings immediately.
**Plans**: 3 plans
Plans:
- [x] 01-01: Backend architecture setup (FastAPI + SQLite schema + JobItem model)
- [x] 01-02: Direct ATS connectors for Greenhouse, Lever, and Ashby with date normalizer
- [x] 01-03: Seed company dataset (50+ global firms) and background sync service

### Phase 2: Natural Language Query & Filter Engine
**Goal**: Translate conversational prompts and category phrases into structured SQL queries using free online LLMs with heuristic fallbacks and multi-faceted filtering.
**Mode**: mvp
**Depends on**: Phase 1
**Requirements**: NLP-01, NLP-02, NLP-03, NLP-04, NLP-05, FILTER-01, FILTER-02, FILTER-03, FILTER-04, FILTER-05
**Success Criteria**:
  1. Freeform queries (e.g., "junior PM in Europe or remote") parse into structured filter dictionaries via Groq/Gemini/OpenRouter.
  2. Offline or rate-limited queries automatically succeed via rule-based regex fallback parser.
  3. Broad category searches ("Product Entry Level", "ML New Grad") return relevant listings without rigid title matching.
  4. Faceted filters (Country, Remote, Industry Domain, Freshness) accurately slice and sort search results by date posted.
**Plans**: 3 plans
Plans:
- [x] 02-01: Multi-model LLM adapter (Groq, Gemini, OpenRouter) and regex fallback parser with LRU query cache
- [x] 02-02: Role category taxonomy and semantic expansion engine
- [x] 02-03: Search & filter API endpoints with multi-attribute filtering and date sorting

### Phase 3: High-Craft Frontend UI & Card Experience
**Goal**: Build a responsive, accessible React/Vite interface adhering to `frontend-skill`, featuring conversational search, category quick-pills, faceted filters, and job cards highlighting posting dates.
**Mode**: mvp
**Depends on**: Phase 2
**Requirements**: UI-01, UI-02, UI-03, UI-04, UI-05
**Success Criteria**:
  1. Natural language search and category pills dynamically update results with fluid transitions.
  2. Job cards clearly present employer, role, location badge, domain tag, and prominent date posted (relative + exact).
  3. Direct "Apply on Company Site" CTA button links cleanly to official ATS career portals.
  4. Users can bookmark jobs with bookmarks persisted in browser local storage.
**Plans**: 3 plans
Plans:
- [x] 03-01: Frontend scaffolding (Vite + React 19 + TypeScript + design tokens adhering to `frontend-skill`)
- [x] 03-02: Search input, category quick-pills, and faceted filter controls
- [x] 03-03: Job Card Grid with posting date highlight, direct apply action, and bookmarks

### Phase 4: Custom Enterprise Portal Scrapers
**Goal**: Integrate an extensible crawler pipeline using BeautifulSoup4 and ScrapeGraph-ai to extract jobs from custom enterprise career sites that lack open ATS feeds.
**Mode**: mvp
**Depends on**: Phase 3
**Requirements**: SCRAPER-01
**Success Criteria**:
  1. Scraper extracts and normalizes jobs from non-ATS enterprise career sites.
  2. Extraction captures role title, description summary, location, and posting date with graceful fallback.
**Plans**: 2 plans
Plans:
- [x] 04-01: BeautifulSoup4 custom portal crawler framework with rate-limiting and browser headers
- [x] 04-02: ScrapeGraph-ai integration for unstructured complex career portal extraction

### Phase 5: Community Intelligence (Reddit Insights)
**Goal**: Pull and summarize authentic interview turnaround timelines, interview rounds, and company culture reviews from Reddit career communities.
**Mode**: mvp
**Depends on**: Phase 3
**Requirements**: COMMUNITY-01, COMMUNITY-02
**Success Criteria**:
  1. User can view an insights drawer for any company or role showing authentic Reddit discussions.
  2. System extracts consensus on interview turnaround times, stage counts, and candidate tips.
**Plans**: 2 plans
Plans:
- [x] 05-01: Reddit public JSON API client with company/role search and caching
- [x] 05-02: Timeline & sentiment summarizer drawer component in frontend

## Milestone v2: Major Visual Overhaul (Desktop-Grade Control Center)

### Phase 6: Obsidian Design System & 3-Column Shell
**Goal**: Implement the Obsidian Studio Dark design tokens, fluid CSS grid 3-column layout shell, and collapsible left navigation rail with quick counts and category accordions.
**Mode**: mvp
**Depends on**: Phase 5
**Requirements**: V2-SHELL-01, V2-NAV-01, V2-AESTHETIC-01
**Success Criteria**:
  1. Application renders a responsive 3-column grid (Left Rail, Center Stream, Right Inspector) with obsidian dark styling (#0B0F17).
  2. Left navigation rail toggles smoothly between expanded and collapsed icon-only mode.
  3. Quick views (All, Saved, Fresh <24h, Fresh <7d) update filter state immediately with badge counts.
**Plans**: 1 plan
Plans:
- [x] 06-01: Obsidian design tokens, 3-column layout shell, and collapsible left navigation rail

### Phase 7: Master Job Stream & Keyboard Navigation Flow
**Goal**: Deliver a high-density, scannable central job stream featuring an omnibox search header with real-time NLP pills, active filter chips, and keyboard-first cursor navigation (`J`/`K`/`S`/`Enter`).
**Mode**: mvp
**Depends on**: Phase 6
**Requirements**: V2-STREAM-01, V2-KEYBOARD-01, V2-MOTION-01
**Success Criteria**:
  1. Sticky header provides omnibox search with `/` keyboard trigger, NLP status badge, and clearable filter chips.
  2. Job cards render in high-density list items highlighting dual dates, company logo badges, and selected glowing border.
  3. Users can navigate up/down through jobs via `J`/`K` keys and toggle bookmarks via `S`.
**Plans**: 1 plan
Plans:
- [x] 07-01: Master job stream component, filter chips, sort bar, and keyboard navigation hook

### Phase 8: Persistent Job Inspector & Embedded Community Intel
**Goal**: Build the persistent right-side inspector pane showing instant job summaries, verified apply actions, and embedded tabbed Reddit community intel (turnaround estimates, stage roadmap, tips, discussions).
**Mode**: mvp
**Depends on**: Phase 7
**Requirements**: V2-INSPECT-01, V2-INSPECT-02, V2-AESTHETIC-01, V2-MOTION-01
**Success Criteria**:
  1. Selecting any job in the stream immediately populates the right-side inspector without modal popup interruptions.
  2. Inspector includes tabbed view switching between Role Overview and Community Intel (Reddit consensus roadmap & live thread cards).
  3. Mobile/tablet breakpoints gracefully collapse into slide-over drawer with Apple spring physics.
**Plans**: 1 plan
Plans:
- [x] 08-01: Persistent right-side job inspector pane with embedded community intel tabs and mobile responsive drawer

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8

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



