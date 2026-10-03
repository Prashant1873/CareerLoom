# Requirements: CareerLoom (Global Job Discovery Engine)

**Defined:** 2026-10-03
**Core Value:** Empowers candidates to discover fresh, direct-from-source job listings across major global employers instantly using freeform natural language queries and category exploration, eliminating rigid keyword matching and ATS search friction.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Data Ingestion & Direct ATS Connectors (INGEST)

- [x] **INGEST-01**: User can query jobs aggregated across major tech, finance, and consulting firms via direct ATS public API connectors (Greenhouse, Lever, Ashby).
- [x] **INGEST-02**: System normalizes varying ATS data feeds into a uniform `JobItem` schema (title, company, domain, category, seniority, location, country, remote, date_posted, apply_url).
- [x] **INGEST-03**: System accurately extracts and normalizes the job publication date (`date_posted`) into ISO UTC timestamps.
- [x] **INGEST-04**: System persists and indexes normalized jobs in an embedded SQLite database for sub-100ms instant query performance.
- [x] **INGEST-05**: User can trigger an on-demand live fetch for a specific company or domain to pull the latest fresh postings.

### Natural Language Search & Category Exploration (NLP)

- [x] **NLP-01**: User can search for roles using conversational freeform natural language prompts (e.g., "entry level product management in Europe or remote").
- [x] **NLP-02**: System interprets natural language queries via free online AI model APIs (Groq Llama 3.3, Google Gemini Flash, OpenRouter free tier) and extracts structured filter parameters.
- [x] **NLP-03**: System provides an instant rule-based / regex heuristic fallback parser if external LLM APIs are offline or rate-limited.
- [x] **NLP-04**: User can explore jobs by broad role categories (e.g., "Product Entry Level", "Machine Learning New Grad", "Infrastructure Engineer") without requiring exact title keyword matches.
- [x] **NLP-05**: System caches parsed natural language queries in-memory to prevent redundant LLM API calls and optimize latency.

### Multi-Attribute Filtering & Freshness (FILTER)

- [x] **FILTER-01**: User can filter jobs by Country and Region (e.g., United States, United Kingdom, European Union, India, Global).
- [x] **FILTER-02**: User can filter jobs by Remote work status (Remote, Hybrid, Onsite).
- [x] **FILTER-03**: User can filter jobs by Industry Domain (Tech / Software, Fintech, Quantitative Finance, Consulting, AI / ML).
- [x] **FILTER-04**: User can filter jobs by Posting Freshness (Past 24 Hours, Past 7 Days, Past 14 Days, Past 30 Days).
- [x] **FILTER-05**: User can sort search results by date posted (newest first) or relevance match score.

### Frontend UI & Card Experience (UI)

- [x] **UI-01**: User can search and filter through a responsive, modern interface adhering to `frontend-skill` standards (anti-slop, clean visual hierarchy, optical balance).
- [x] **UI-02**: System arranges search results in clear, high-density cards displaying job title, company name, domain badge, location, and seniority.
- [x] **UI-03**: Each job card prominently highlights the posting date with both relative time ("2 days ago") and exact formatted date.
- [x] **UI-04**: Each job card provides a direct "Apply on Company Site" CTA button opening the verified official ATS career application portal.
- [x] **UI-05**: User can bookmark or save favorite jobs, persisted across browser sessions in local storage.

### Community Intelligence & Reviews (COMMUNITY - Phase 2)

- [x] **COMMUNITY-01**: User can view authentic community discussions and interview timelines pulled from Reddit (e.g. r/cscareerquestions, r/ProductManagement) for a selected company or role.
- [x] **COMMUNITY-02**: System extracts and summarizes consensus on interview stages, turnaround time, and insider advice without requiring a Reddit paid API key.

### Custom Enterprise Portal Scrapers (SCRAPER)

- [x] **SCRAPER-01**: System provides an extensible scraper pipeline (BeautifulSoup4 / ScrapeGraph-ai integration) for non-standard enterprise career sites lacking direct JSON ATS feeds.

## v2 Requirements: Visual Overhaul & Desktop-Grade Master-Detail Control Center

### Layout Shell & Navigation Rail (V2-SHELL)
- [ ] **V2-SHELL-01**: User interacts with a 3-column split layout (Collapsible Left Rail + Central Stream + Sticky Right Inspector) built with fluid CSS grid.
- [ ] **V2-NAV-01**: User can toggle navigation views (All Jobs, Saved Jobs with count, Fresh <24h, Fresh <7d) and expand/collapse category and filter accordions in the left rail.

### Central Stream & Keyboard Navigation (V2-STREAM)
- [ ] **V2-STREAM-01**: User can search using a sticky omnibox search header with real-time NLP badge, clearable filter chips, and sorting controls.
- [ ] **V2-KEYBOARD-01**: User can navigate the job stream using keyboard shortcuts: `J` (next job), `K` (previous job), `S` (bookmark), `Enter` (apply), and `/` (focus search).

### Persistent Job Inspector & Embedded Community Intel (V2-INSPECT)
- [ ] **V2-INSPECT-01**: Right-side inspector displays selected job summary, dual date badges, and verified ATS apply CTA without intrusive modal dialogs.
- [ ] **V2-INSPECT-02**: Right-side inspector embeds tabbed Reddit community intelligence (interview turnaround estimates, stage roadmap, insider tips, discussion thread links).

### Design Aesthetics & Fluid Motion (V2-AESTHETIC)
- [ ] **V2-AESTHETIC-01**: Interface adopts Obsidian Studio Dark styling (#0B0F17 canvas, hairline borders, emerald active glow, amber Reddit accents) conforming to `frontend-skill`.
- [ ] **V2-MOTION-01**: Micro-interactions feature Apple HIG spring physics, tactile `active: scale(0.98)` feedback, and fluid responsive column collapse.

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Automated Bot Application Auto-Submission | High anti-bot risk, violates employer terms of service, leads to candidate blacklisting; all links open official direct career portals. |
| Paid Third-Party Job Aggregator APIs | Incurs recurring monthly fees ($50-$200/mo); violates zero-cost requirement. |
| Mandatory User Account Registration & Paywall | Introduces high user friction; instant anonymous search with local storage is prioritized. |

## Traceability

Which phases cover which requirements. Populated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| INGEST-01 to 05 | Phase 1 | Complete |
| NLP-01 to 05 | Phase 2 | Complete |
| FILTER-01 to 05 | Phase 2 | Complete |
| UI-01 to 05 | Phase 3 | Complete |
| SCRAPER-01 | Phase 4 | Complete |
| COMMUNITY-01, 02 | Phase 5 | Complete |
| V2-SHELL-01, V2-NAV-01 | Phase 6 | Planned |
| V2-STREAM-01, V2-KEYBOARD-01 | Phase 7 | Planned |
| V2-INSPECT-01, V2-INSPECT-02 | Phase 8 | Planned |
| V2-AESTHETIC-01, V2-MOTION-01 | Phase 8 | Planned |

**Coverage:**
- v1 requirements: 23 total (23 Complete)
- v2 requirements: 8 total (8 Planned)
- Mapped to phases: 31
- Unmapped: 0

---
*Requirements defined: 2026-10-03*
*Last updated: 2026-10-03 for v2 Visual Overhaul*

