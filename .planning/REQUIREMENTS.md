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

- [ ] **COMMUNITY-01**: User can view authentic community discussions and interview timelines pulled from Reddit (e.g. r/cscareerquestions, r/ProductManagement) for a selected company or role.
- [ ] **COMMUNITY-02**: System extracts and summarizes consensus on interview stages, turnaround time, and insider advice without requiring a Reddit paid API key.

### Custom Enterprise Portal Scrapers (SCRAPER)

- [ ] **SCRAPER-01**: System provides an extensible scraper pipeline (BeautifulSoup4 / ScrapeGraph-ai integration) for non-standard enterprise career sites lacking direct JSON ATS feeds.

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Application Tracking & Alerts

- **ALERT-01**: Email or desktop push alerts when new jobs matching a saved natural language query are indexed.
- **TRACK-01**: Kanban board for tracking user application stages (Applied, Interviewing, Offered, Rejected).
- **RESUME-01**: Tailored resume keyword alignment analysis against job description requirements.

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
| INGEST-01 | Phase 1 | Complete |
| INGEST-02 | Phase 1 | Complete |
| INGEST-03 | Phase 1 | Complete |
| INGEST-04 | Phase 1 | Complete |
| INGEST-05 | Phase 1 | Complete |
| NLP-01 | Phase 2 | Complete |
| NLP-02 | Phase 2 | Complete |
| NLP-03 | Phase 2 | Complete |
| NLP-04 | Phase 2 | Complete |
| NLP-05 | Phase 2 | Complete |
| FILTER-01 | Phase 2 | Complete |
| FILTER-02 | Phase 2 | Complete |
| FILTER-03 | Phase 2 | Complete |
| FILTER-04 | Phase 2 | Complete |
| FILTER-05 | Phase 2 | Complete |
| UI-01 | Phase 3 | Complete |
| UI-02 | Phase 3 | Complete |
| UI-03 | Phase 3 | Complete |
| UI-04 | Phase 3 | Complete |
| UI-05 | Phase 3 | Complete |
| SCRAPER-01 | Phase 4 | Pending |
| COMMUNITY-01 | Phase 5 | Pending |
| COMMUNITY-02 | Phase 5 | Pending |

**Coverage:**
- v1 requirements: 23 total
- Mapped to phases: 23
- Unmapped: 0

---
*Requirements defined: 2026-10-03*
*Last updated: 2026-10-03 after research synthesis*
