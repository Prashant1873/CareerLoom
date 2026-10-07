# Neural Map: Project Architecture & Logic

```mermaid
graph TD
    User([User Prompt / Category / Filters]) --> UI[Frontend Interface: Search & Card Grid]
    UI --> NLP[Natural Language Parser & Query Expander]
    
    subgraph "AI Intelligence Layer"
        NLP -->|Free Online Model / API| LLM[LLM Engine: Groq / HuggingFace / Gemini]
        LLM -->|Structured Params: category, title, geo, seniority, stack| QueryEngine[Query Normalizer & Filter Dispatcher]
    end

    subgraph "Aggregation & Scraping Engine"
        QueryEngine --> Aggregator[Aggregator Orchestrator]
        Aggregator --> DirectATS[Direct ATS Ingestion: Greenhouse, Lever, Ashby, Workday]
        Aggregator --> ScrapeGraph[Scraper / ScrapeGraph-AI: Enterprise Career Portals]
    end

    subgraph "Storage & Indexing"
        DirectATS --> JobStore[(Normalized Job Store)]
        ScrapeGraph --> JobStore
        JobStore --> FilterIndex[Multi-Attribute In-Memory / Vector Filter]
    end

    FilterIndex -->|Structured & Ranked Cards with Date Posted| UI

    subgraph "Phase 2: Community Insights"
        UI -.->|On Card Expand / Query| CommunityScraper[Reddit / Public Forum Scraper]
        CommunityScraper -.-> SentimentEngine[Timeline & Review Summarizer]
        SentimentEngine -.-> UI
    end
```

## Core Modules & Logic Flow

1. **User Interface (`frontend/` - Phase 3 Complete)**
   - [Header.tsx](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/frontend/src/components/Header.tsx): Live feed badge, indexed job count, saved jobs toggle.
   - [SearchBar.tsx](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/frontend/src/components/SearchBar.tsx): Omnibox conversational search (`/` shortcut), real-time NLP parsing badge, prompt chips.
   - [CategoryPills.tsx](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/frontend/src/components/CategoryPills.tsx): Category ribbon and 36 curated discovery track pills.
   - [FilterSidebar.tsx](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/frontend/src/components/FilterSidebar.tsx): Faceted sidebar for freshness (24h/7d/14d/30d), remote mode, country, domain, seniority, sorting.
   - [JobCard.tsx](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/frontend/src/components/JobCard.tsx): High-craft job cards with prominent posting dates (relative + exact), verified ATS apply CTA, bookmark toggle.
   - [JobDetailModal.tsx](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/frontend/src/components/JobDetailModal.tsx): Interactive job inspection modal with skill chips and verified ATS link.
   - [useBookmarks.ts](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/frontend/src/hooks/useBookmarks.ts): Persistent saved jobs in `localStorage`.

2. **NL Query Interpreter & Taxonomy (`backend/app/services/` & `api/`)**
   - [backend/app/services/llm_adapter.py](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/backend/app/services/llm_adapter.py): Multi-model LLM adapter (Groq Llama 3.3, Google Gemini Flash, OpenRouter) with `HeuristicQueryParser` regex fallback.
   - [backend/app/services/taxonomy.py](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/backend/app/services/taxonomy.py): Canonical ontology of 8 categories, 36 curated tracks, and title synonyms with `match_category_phrase()`.
   - [backend/app/utils/query_cache.py](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/backend/app/utils/query_cache.py): In-memory LRU/TTL parsed query cache.
   - [backend/app/api/nlp.py](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/backend/app/api/nlp.py): `POST /api/nlp/parse` and `POST /api/nlp/search`.
   - [backend/app/api/categories.py](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/backend/app/api/categories.py): `GET /api/categories` and `GET /api/categories/tracks`.

3. **Aggregator & Custom Ingestion Engine (`backend/app/scrapers/` & `services/sync.py`)**
   - Direct ATS Connectors: [greenhouse.py](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/backend/app/scrapers/greenhouse.py), [lever.py](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/backend/app/scrapers/lever.py), [ashby.py](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/backend/app/scrapers/ashby.py).
   - Custom Portal Crawler: [custom_crawler.py](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/backend/app/scrapers/custom_crawler.py) (polite browser headers, HTML pre-processor & DOM block extractor).
   - LLM Portal Extractor: [llm_scraper.py](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/backend/app/scrapers/llm_scraper.py) (semantic normalization of unstructured custom portals with seed catalog [custom_portals.json](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/backend/app/data/custom_portals.json)).
   - [backend/app/services/sync.py](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/backend/app/services/sync.py): Bounded-concurrency background sync pipeline with 55 seed companies catalog and custom portal ingestion.
   - [backend/app/utils/date_parser.py](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/backend/app/utils/date_parser.py): Robust date parser supporting ISO 8601, epoch milliseconds, and relative timestamps.

4. **Normalized Job Storage (`backend/app/db/` & `models/`)**
   - [backend/app/models/job.py](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/backend/app/models/job.py): `JobItem` model with deterministic SHA-256 deduplication and UTC datetime enforcement.
   - [backend/app/db/database.py](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/backend/app/db/database.py): SQLite storage with composite indexes (`date_posted DESC`, `category`, `company`, `domain`, `country`), regional geographic expansion (e.g. Europe), and sorting.

5. **Community Insights (`backend/app/services/reddit.py`, `backend/app/api/insights.py`, & `frontend/`)**
   - [backend/app/services/reddit.py](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/backend/app/services/reddit.py): `RedditCommunityService` querying public Reddit `.json` search feeds with custom User-Agent headers, 24-hour in-memory TTL caching, benchmark consensus for top employers, and fallback synthesis.
   - [backend/app/api/insights.py](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/backend/app/api/insights.py): `GET /api/insights/company` providing turnaround estimates, interview round breakdowns, insider tips, and thread links.
   - [frontend/src/components/CommunityInsightsDrawer.tsx](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/frontend/src/components/CommunityInsightsDrawer.tsx): High-craft slide-over panel with turnaround highlight, hiring sentiment summary, stepped process roadmap, candidate tips, and authentic Reddit cards.
   - Integrated trigger buttons in [JobCard.tsx](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/frontend/src/components/JobCard.tsx) and [JobDetailModal.tsx](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/frontend/src/components/JobDetailModal.tsx).

6. **v2 Desktop-Grade Master-Detail Architecture (`frontend/`)**
   - **Column 1 (`NavRail.tsx`)**: Left collapsible navigation rail with quick counts (All, Saved, 24h Fresh), category badges, and faceted filter accordions.
   - **Column 2 (`MasterJobStream.tsx`)**: Omnibox search with `/` trigger, active filter chips, sort options, and high-density job cards with `J`/`K` keyboard cursor navigation.
   - **Column 3 (`JobInspectorPane.tsx`)**: Persistent right-side inspection pane with role summary, verified ATS apply CTA, and embedded tabbed Reddit community intel.

7. **Massive Multi-ATS Global Pipeline (200+ Firms)**
   - [backend/app/data/companies.json](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/backend/app/data/companies.json): Seed dataset of 200+ global industry leaders categorized by domain, region, and ATS connector type (Greenhouse, Lever, Ashby, SmartRecruiters, Workday).
   - [backend/app/services/sync.py](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/backend/app/services/sync.py): Bounded-concurrency async ingestion runner with rate-limit backoff, duplicate elimination, and batch insertion into SQLite.
   - [backend/app/db/database.py](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/backend/app/db/database.py): SQLite persistence layer with composite indexes for sub-50ms multi-attribute queries across thousands of active jobs.

8. **Indian Tech Startup & Unicorn Discovery Pipeline**
   - [backend/app/data/companies.json](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/backend/app/data/companies.json): Curated directory of 50+ verified Indian tech unicorns and startups (Paytm, Swiggy, Meesho, CRED, Groww, InMobi, Glance, Sarvam AI, Atlan, Zeta, HighRadius, Zenoti, Mindtickle, SigNoz, Druva, Kovai.co, etc.).
   - [backend/app/utils/classifier.py](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/backend/app/utils/classifier.py): Regional geographic mapping for all major Indian tech centers (Bengaluru, Hyderabad, Mumbai, Delhi NCR, Gurugram, Noida, Pune, Chennai, Ahmedabad) with ISO-2 code mapping (`IN`/`IND` -> `India`) and company-origin fallbacks.
   - [backend/app/scrapers/](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/backend/app/scrapers/): ATS connectors (Lever, Greenhouse, Ashby, SmartRecruiters) enriched with `company_hint` for deterministic country classification and verified direct listing links.

9. **Candidate Lead Capture & Referral Engine (`backend/app/api/leads.py` & `frontend/`)**
   - [backend/app/db/database.py](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/backend/app/db/database.py): SQLite `candidate_leads` schema for storing candidate profile submissions, target job IDs, CTC expectations, and referral status.
   - [backend/app/api/leads.py](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/backend/app/api/leads.py): `POST /api/leads/submit`, `GET /api/leads`, and `POST /api/leads/pitch` for candidate lead capture, referral pitch generation, and recruiter querying.
   - [frontend/src/components/LeadCaptureModal.tsx](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/frontend/src/components/LeadCaptureModal.tsx): Obsidian dark dialog with LinkedIn profile sync, YoE, CTC LPA numbers, Notice Period selector, and 1-click clipboard referral pitch copy.
   - [frontend/src/components/NavRail.tsx](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/frontend/src/components/NavRail.tsx): Dedicated "India Direct" toggle (🇮🇳 1.4k live count) and Indian Metro Tech Hub ribbon.
   - [frontend/src/utils/ctcFormatter.ts](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/frontend/src/utils/ctcFormatter.ts): High-fidelity INR CTC parser and calibrated compensation benchmark engine (₹ LPA).

10. **Indian Developer Community Intelligence & Verification (`backend/app/services/reddit.py` & `tests/`)**
    - [backend/app/services/reddit.py](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/backend/app/services/reddit.py): Regional routing to `r/developersIndia`, `r/IndianStartups`, and `r/IndiaTech` for Indian tech employers; benchmark consensus for Swiggy, CRED, Groww, Meesho, Razorpay, Atlan, Target India, and Thoughtworks.
    - [frontend/src/components/JobInspectorPane.tsx](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/frontend/src/components/JobInspectorPane.tsx): 5-stage Indian hiring roadmap (Online Assessment -> Machine Coding -> LLD/HLD -> Hiring Manager -> HR & Notice Period Buyout) and Community Hub source badge.
    - [tests/test_india_engine.py](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/tests/test_india_engine.py): Automated test suite verifying Indian catalog schemas, location and metro classifier, heuristic NLP parsing, sub-50ms query latency, and community intelligence routing.

11. **Milestone v5: Indian Career Repository & Batch Ingestion Pipeline**
    - `career_targets` Registry: SQLite table indexing 200+ companies (Startups, Unicorns, Conglomerates, Strategy Consulting), tracking direct career links, ATS connectors, scraping status, role tags, and scrape timestamps.
    - Reddit Discovery Engine: Mining `r/developersIndia`, `r/IndianStartups`, `r/ProductManagement`, `r/consulting`, and `r/bangalore` for emerging employers and active career URLs.
    - PM & Strategy Consulting Ontology: Canonical taxonomy for Product Management (APM, PM, SPM, GPM, TPM, ProdOps) and Strategy & Consulting (Consultant, Strategy Analyst, Chief of Staff, Founder's Office, BizOps) with sub-50ms query mapping.
    - Continuous Batch Engine: Bounded-concurrency async scraper (`asyncio.Semaphore(15)`) with stale job reconciler to purge expired postings.
    - Frontend Career Directory Hub: Obsidian view displaying all tracked companies, direct portal links, and live sync health indicators.


