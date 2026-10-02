# Feature Research

**Domain:** Multi-Firm Career Portal Aggregator & NL Job Discovery Engine
**Researched:** 2026-10-03
**Confidence:** HIGH

## Feature Landscape

### Table Stakes (Users Expect These)

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Natural Language Search Bar** | Users want to express goals conversationally ("Junior PM roles in Europe or remote"). | MEDIUM | Parse into structured filters via free LLM (Groq/Gemini) with heuristic fallback. |
| **Category-First Exploration** | Users want to explore by role track ("Product Entry Level", "ML New Grad") without exact titles. | LOW | Canonical category ontology mapping 500+ title variations to standard buckets. |
| **Clear Posting Date on Cards** | Candidates prioritize recently posted jobs (<7 days) to maximize interview chances. | LOW | Prominent display of relative freshness ("2 days ago") + exact ISO date. |
| **Faceted Filtering Controls** | Quick refinement by Country, Remote status, Industry/Domain, and Seniority. | LOW | Synchronized between query string and UI state for instant re-ranking. |
| **Direct Apply Link** | Users want to apply on official company career sites, avoiding 3rd party spam. | LOW | Verified career URL directly from employer ATS. |
| **Responsive Card Grid** | High-density information display that scans easily on desktop and mobile. | MEDIUM | Follows `frontend-skill` (high contrast, border continuity, no visual slop). |

### Differentiators (Competitive Advantage)

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Hybrid Real-Time & Indexed DB** | Sub-100ms instant search across 5,000+ indexed listings + on-demand live fetch. | MEDIUM | SQLite database updated in background; live fetch for deep single-firm searches. |
| **Zero-Cost Multi-Model Adapter** | Free forever via Groq Llama 3.3, Google Gemini Flash, or OpenRouter free tier. | MEDIUM | User can test without entering credit cards; includes offline keyword parser. |
| **Multi-Firm ATS Direct Connect** | Bypasses anti-bot walls by querying public JSON endpoints of Greenhouse, Lever, Ashby. | MEDIUM | Covers thousands of high-tier firms (Stripe, Figma, OpenAI, Databricks, etc.). |
| **Community Intelligence (Phase 2)** | Pulls Reddit & public forum discussions on interview timelines, review scores, and tips. | HIGH | Aggregates r/cscareerquestions and career subreddits using public JSON endpoints. |

### Anti-Features (Commonly Requested, Often Problematic)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| **Automated 1-Click Application Bot** | Seems convenient for users. | Triggers employer anti-bot filters, leads to candidate blacklisting, requires complex CAPTCHA bypass. | Direct 1-click jump to official employer application form with autofill guide. |
| **Forced User Authentication / Sign-up** | Growth tactic for lead generation. | Introduces heavy friction, discourages casual job seekers, adds auth database complexity. | Instant anonymous search; persist bookmarks and search history in browser `localStorage`. |
| **Paid API Integration (RapidAPI, JSearch)** | Avoids writing scraping logic. | Incurs recurring monthly fees; violates zero-cost constraint. | Query public ATS feeds directly and use ScrapeGraph-ai for custom portals. |

## Feature Dependencies

```
[NL Query Parser] ──requires──> [LLM Adapter (Groq/Gemini/Fallback)]
       │
       └──produces──> [Structured Filter State]
                            │
                            ▼
               [Hybrid Job Query Engine]
               ├──queries──> [Indexed SQLite Cache]
               └──triggers──> [Live ATS Scraper (On-Demand)]
                            │
                            ▼
                 [Job Result Card Grid]
                 (Title, Company, Domain, Country, Date Posted, Apply Link)
                            │
                            ▼ (Phase 2)
                 [Reddit / Community Insights Drawer]
```

### Dependency Notes

- **NL Query Parser requires LLM Adapter**: The LLM normalizes user queries into standardized categories, locations, and timeframes. If offline, the regex rule-based engine acts as fallback.
- **Card Grid relies on Normalized Schema**: All scrapers (Greenhouse, Lever, Ashby, ScrapeGraph-ai) must normalize to a uniform `JobItem` schema with reliable `date_posted`.
- **Phase 2 Community Insights is loosely coupled**: Reddit timeline/culture extraction triggers on card expansion or detailed view, preventing blocking of main search results.
