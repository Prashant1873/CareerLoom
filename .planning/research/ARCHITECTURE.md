# Architecture Research

**Domain:** Multi-Firm Career Portal Aggregator & NL Job Discovery Engine
**Researched:** 2026-10-03
**Confidence:** HIGH

## System Architecture

```mermaid
graph TD
    Client[React/Vite Frontend UI] -->|HTTP / REST| API[FastAPI Backend Gateway]

    subgraph "Backend API Layer"
        API --> SearchRouter[/api/jobs/search]
        API --> NLPRouter[/api/nlp/parse]
        API --> SyncRouter[/api/jobs/sync]
        API --> CommunityRouter[/api/community/insights]
    end

    subgraph "Intelligence & Parsing Engine"
        NLPRouter --> LLMManager[LLM Provider Adapter]
        LLMManager --> GroqAPI[Groq API: Llama 3.3]
        LLMManager --> GeminiAPI[Google Gemini Flash API]
        LLMManager --> RegexFallback[Rule-Based Heuristic Parser]
    end

    subgraph "Aggregation & Scraping Subsystem"
        SyncRouter --> IngestionManager[Ingestion Orchestrator]
        SearchRouter --> IngestionManager
        IngestionManager --> ATSFeed[Direct ATS Connector: Greenhouse / Lever / Ashby]
        IngestionManager --> CustomScraper[ScrapeGraph-ai / BS4 Crawler]
        ATSFeed --> Normalizer[Data Normalizer & Deduplicator]
        CustomScraper --> Normalizer
    end

    subgraph "Persistence & Indexing"
        Normalizer --> SQLite[(SQLite Job Store)]
        SearchRouter --> FastFilter[SQL / In-Memory Filter Engine]
        FastFilter --> SQLite
    end

    subgraph "Phase 2: Community Insights"
        CommunityRouter --> RedditConnector[Reddit Public JSON API Client]
        RedditConnector --> SentimentExtractor[Timeline & Review Summarizer]
    end
```

## Component Boundaries

### 1. Frontend Layer (`frontend/`)
- **Technology**: React 19 + TypeScript + Vite.
- **Responsibilities**:
  - Natural language input bar with auto-suggestions and category quick-pills.
  - Interactive faceted filters (Domain, Country, Remote, Seniority, Date Freshness).
  - High-density Job Card Grid with relative posting timestamps ("3 days ago") and direct apply link.
  - Community insights modal/drawer for Reddit interview discussions.
  - Zero heavy third-party UI library bloat; designed with clean CSS variables and Apple spring physics.

### 2. API Gateway & Controllers (`backend/app/api/`)
- **`GET /api/jobs`**: Queries the indexed SQLite job store with faceted filters (category, location, remote, date_posted_after, domain). Response time <50ms.
- **`POST /api/nlp/parse`**: Ingests natural language string; returns structured filter dictionary.
- **`POST /api/jobs/live-fetch`**: Triggers immediate ATS fetch for specific firm or live search.
- **`GET /api/community/insights`**: (Phase 2) Fetches Reddit interview timelines and company reviews.

### 3. Ingestion & Scraper Pipeline (`backend/app/scrapers/`)
- **Direct ATS Connectors**:
  - `GreenhouseConnector`: `https://boards-api.greenhouse.io/v1/boards/{company}/jobs`
  - `LeverConnector`: `https://api.lever.co/v0/postings/{company}?mode=json`
  - `AshbyConnector`: `https://jobs.ashbyhq.com/api/non-user-graphql?op=ApiJobBoardWithTeams`
- **Dynamic Scraper (ScrapeGraph-ai / BS4)**:
  - Targeted extractor for custom careers sites using BeautifulSoup for fast DOM traversal and optional ScrapeGraph-ai graph execution.

### 4. Normalized Data Model (`JobItem`)

```python
class JobItem(BaseModel):
    id: str  # MD5 hash of company + title + source_url
    title: str  # e.g., "Associate Product Manager"
    company: str  # e.g., "Stripe"
    domain: str  # e.g., "Fintech", "Software", "AI"
    category: str  # Canonical: "product", "software_engineering", "data_ai"
    seniority: str  # "entry", "mid", "senior", "lead", "intern"
    location: str  # e.g., "London, UK", "New York, USA"
    is_remote: bool
    country: str  # e.g., "United Kingdom", "United States", "Global"
    date_posted: datetime  # Verified posting timestamp
    apply_url: str  # Direct link to employer career portal
    source: str  # "greenhouse" | "lever" | "ashby" | "custom_scraper"
```

## Build Order & Dependency Chain

1. **Foundations**: Backend setup (FastAPI + SQLite schema + JobItem model).
2. **ATS Ingestion Core**: Direct connectors for Greenhouse, Lever, and Ashby with initial company seed list (top 50 tech/finance firms).
3. **NL Parser & Adapter**: Multi-model service (Groq / Gemini free tier / Rule fallback) to map natural language to query parameters.
4. **Search & Filter API**: High-speed filtering by category, country, remote, and freshness.
5. **Frontend UI Experience**: Search bar, category quick-pills, faceted filters, and responsive cards displaying `date_posted`.
6. **Custom Portal Scrapers**: ScrapeGraph-ai / BS4 fallback for non-ATS enterprise portals.
7. **Phase 2 Community Insights**: Reddit public JSON scraper for interview timelines and company reviews.
