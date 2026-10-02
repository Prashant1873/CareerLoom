# Project Research Summary

**Project:** CareerLoom (Global Job Discovery Engine)
**Domain:** Multi-Firm Career Portal Aggregator & NL Job Discovery Engine
**Researched:** 2026-10-03
**Confidence:** HIGH

## Executive Summary

CareerLoom is designed as an intelligent career discovery portal that searches across major employers globally using natural language queries, category-based exploration, and fast ATS feeds. Modern job seekers face two primary pain points: keyword mismatch (missing relevant jobs because they didn't guess the exact title variation) and slow, bot-guarded enterprise career search engines. 

The recommended solution uses a Python (FastAPI) backend paired with a React 19 / Vite frontend. For natural language processing, free cloud LLMs (Groq Llama 3.3, Google Gemini Flash, and OpenRouter) extract structured query parameters (role category, seniority, geography, freshness) with zero recurring operational cost. To guarantee sub-100ms response times and avoid anti-bot blocks, the engine utilizes direct public JSON feeds from major ATS platforms (Greenhouse, Lever, Ashby, Workday) cached into a local SQLite store, with an on-demand fallback scraper (BeautifulSoup / ScrapeGraph-ai) for custom portals.

Key risks—including missing posting dates, cloud scraper timeouts, and rate limits—are mitigated through strict schema normalization, background cache synchronization, and LRU query caching. Phase 2 introduces community intelligence from Reddit and public career forums for interview turnaround timelines and authentic company feedback.

## Key Findings

### Recommended Stack

A high-performance Python ASGI backend (FastAPI) with SQLite for caching, coupled with a lightweight React 19 + TypeScript frontend.

**Core technologies:**
- **FastAPI (Python 3.11+)**: Asynchronous API gateway with native Pydantic validation and automatic OpenAPI documentation.
- **SQLite (aiosqlite)**: Zero-cost, zero-maintenance local embedded database delivering sub-millisecond query responses.
- **React 19 + Vite 6**: Instant HMR and clean component architecture conforming to anti-slop frontend craft.
- **Multi-Model LLM Adapter**: Groq Cloud Free Tier (Llama 3.3 70B) & Google Gemini Flash for instant query structuring, backed by a regex heuristic fallback.

### Expected Features

**Must have (table stakes):**
- **Natural Language Search**: Translates conversational prompts into structured filter criteria.
- **Category-First Browsing**: Direct navigation by domain track ("Product Entry Level", "Machine Learning New Grad") without strict title match hurdles.
- **Prominent Date Posted**: Accurate, relative ("2 days ago") and exact timestamps on every job card.
- **Faceted Filters**: Quick filtering by Country/Region, Remote, Industry Domain, and Seniority.
- **Verified Direct Apply Links**: Direct links to official employer career sites.

**Should have (competitive):**
- **Hybrid Real-Time & Indexed DB**: Instant sub-100ms search on cached listings + live fetch for deep company searches.
- **Community Intelligence (Phase 2)**: Reddit thread extraction for interview timelines and authentic company reviews.
- **AI-Guided Fallback Scraper**: ScrapeGraph-ai integration for unstructured custom enterprise career portals.

**Defer (v2+):**
- **Automated Resume Auto-Fill**: Kept out of scope to avoid employer anti-bot flags and candidate blacklisting.

### Architecture Approach

The architecture cleanly decouples ingestion from user queries. Ingestion connectors pull structured job data from public ATS feeds into SQLite. The client issues natural language searches to the FastAPI gateway, which utilizes a multi-model adapter to extract query parameters and execute indexed SQL queries.

**Major components:**
1. **Frontend UI**: Search input, quick category pills, faceted filters, and job card grid.
2. **NL Query Interpreter**: Translates freeform queries into structured filter parameters.
3. **Ingestion & Scraper Engine**: Direct ATS connectors (Greenhouse, Lever, Ashby) + custom portal scrapers.
4. **Normalized Job Store**: SQLite database indexing jobs by company, category, country, and posting date.
5. **Community Insights Engine (Phase 2)**: Reddit scraper for timeline and culture insights.

### Critical Pitfalls

1. **Inconsistent or Missing Posting Dates**: Solved by prioritizing ATS APIs with explicit timestamps and calculating fallback relative dates during ingestion.
2. **Latency Bottlenecks from Live Scraping**: Solved via hybrid architecture where search queries hit the indexed SQLite database (<50ms).
3. **Free LLM API Rate Limits (429)**: Solved via frontend debounce, in-memory parsed query caching, and instant fallback to a heuristic regex parser.
4. **Anti-Bot Blocking on Enterprise Portals**: Solved by relying primarily on public ATS JSON feeds that do not enforce anti-bot challenges.

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 1: Core Foundation & Ingestion Engine
**Rationale:** Job search requires reliable, normalized data before building UI or NL features.
**Delivers:** FastAPI backend, SQLite schema, direct ATS connectors (Greenhouse, Lever, Ashby) for top 50+ firms, and database sync.
**Addresses:** Data ingestion, schema normalization, date parsing.
**Avoids:** Inconsistent posting dates and anti-bot blocks.

### Phase 2: Natural Language Query & Filtering Engine
**Rationale:** The intelligence layer translates conversational user intent into database queries.
**Delivers:** Multi-provider LLM adapter (Groq, Gemini, OpenRouter), category taxonomy mapping, and faceted search endpoints.
**Uses:** Groq / Gemini SDKs, Pydantic, SQLite full-text and indexed search.
**Addresses:** Conversational job role search, category exploration, natural language filtering.

### Phase 3: High-Craft Frontend UI & Card Experience
**Rationale:** Provides an anti-slop, responsive, accessible interface for job exploration.
**Delivers:** Vite React app, NL search bar, category quick-pills, faceted sidebar, and card grid with prominent posting dates.
**Implements:** Frontend UI compliant with `frontend-skill` (Apple fluid motion, WCAG contrast, optical balance).
**Addresses:** Card layout, date display, responsive browsing.

### Phase 4: Custom Enterprise Portal Scrapers
**Rationale:** Extends coverage beyond standard ATS feeds to custom career portals.
**Delivers:** BeautifulSoup4 / ScrapeGraph-ai crawler pipeline for non-standard enterprise career sites.
**Addresses:** Custom domain scraping across major firms.

### Phase 5: Community Intelligence (Reddit Insights)
**Rationale:** Provides post-search contextual value (interview timelines, insider reviews).
**Delivers:** Public Reddit JSON scraper for interview timelines, review summaries, and company vibe meter.
**Addresses:** Phase 2 community intelligence requirement.

### Phase Ordering Rationale

- Ingestion and data storage must exist before search logic can be tested.
- NL parser and search endpoints must be validated before connecting the UI.
- Frontend delivers the core user value immediately after core search works.
- Custom scrapers and Reddit intelligence build upon the established foundation.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Python FastAPI + React/Vite + SQLite is well-proven and operates at $0 cost. |
| Features | HIGH | Clear table stakes and differentiators mapped to user requirements. |
| Architecture | HIGH | Hybrid DB + ATS feeds eliminates latency and blocking risks. |
| Pitfalls | HIGH | Clear prevention strategies for dates, rate limits, and scrapers. |

**Overall confidence:** HIGH

## Sources

### Primary (HIGH confidence)
- Greenhouse Public Job Board API Docs (`boards-api.greenhouse.io`)
- Lever Postings API Docs (`api.lever.co/v0/postings`)
- Ashby Job Board API (`jobs.ashbyhq.com/api`)
- Groq Cloud Documentation & API Reference (`console.groq.com/docs`)
- Google Gemini API Reference (`ai.google.dev`)
- ScrapeGraphAI Open Source Repository (`github.com/ScrapeGraphAI/Scrapegraph-ai`)
