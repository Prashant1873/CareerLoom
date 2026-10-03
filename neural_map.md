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

1. **User Interface (`frontend/` - Phase 3)**
   - Conversational input bar + categorical pills ("Product Entry Level", "ML New Grad").
   - Faceted controls: Country / Remote, Domain / Industry, Freshness / Date Posted, Seniority.
   - Job Cards: High-craft aesthetic, direct apply CTA, dual date posted (relative + ISO), bookmarking.

2. **NL Query Interpreter & Taxonomy (`backend/app/services/` & `api/`)**
   - [backend/app/services/llm_adapter.py](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/backend/app/services/llm_adapter.py): Multi-model LLM adapter (Groq Llama 3.3, Google Gemini Flash, OpenRouter) with `HeuristicQueryParser` regex fallback.
   - [backend/app/services/taxonomy.py](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/backend/app/services/taxonomy.py): Canonical ontology of 8 categories, 36 curated tracks, and title synonyms with `match_category_phrase()`.
   - [backend/app/utils/query_cache.py](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/backend/app/utils/query_cache.py): In-memory LRU/TTL parsed query cache.
   - [backend/app/api/nlp.py](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/backend/app/api/nlp.py): `POST /api/nlp/parse` and `POST /api/nlp/search`.
   - [backend/app/api/categories.py](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/backend/app/api/categories.py): `GET /api/categories` and `GET /api/categories/tracks`.

3. **Aggregator & ATS Ingestion Engine (`backend/app/scrapers/` & `services/sync.py`)**
   - Direct ATS Connectors: [greenhouse.py](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/backend/app/scrapers/greenhouse.py), [lever.py](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/backend/app/scrapers/lever.py), [ashby.py](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/backend/app/scrapers/ashby.py).
   - [backend/app/services/sync.py](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/backend/app/services/sync.py): Bounded-concurrency background sync pipeline with 55 seed companies catalog.
   - [backend/app/utils/date_parser.py](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/backend/app/utils/date_parser.py): Robust date parser supporting ISO 8601, epoch milliseconds, and relative timestamps.

4. **Normalized Job Storage (`backend/app/db/` & `models/`)**
   - [backend/app/models/job.py](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/backend/app/models/job.py): `JobItem` model with deterministic SHA-256 deduplication and UTC datetime enforcement.
   - [backend/app/db/database.py](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/backend/app/db/database.py): SQLite storage with composite indexes (`date_posted DESC`, `category`, `company`, `domain`, `country`), regional geographic expansion (e.g. Europe), and sorting.

5. **Community Insights (Phase 5)**
   - Reddit API / public search for `[company] + [role] + interview timeline / review`.
   - Distill consensus on response times, rounds, and insider advice.
