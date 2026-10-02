# CareerLoom (Global Job Discovery Engine)

## What This Is

CareerLoom is an intelligent job discovery engine that searches career portals across major global firms (tech, finance, consulting, healthcare) across domains, companies, and countries. Powered by free online AI models (Groq / Gemini / OpenRouter), it translates natural language queries and broad role categories (e.g., "product entry level", "junior machine learning remote") into structured searches, displaying verified direct listings in high-craft cards with exact posting dates. Phase 2 introduces community intelligence from Reddit and public career forums for interview timelines and insider reviews.

## Core Value

Empowers candidates to discover fresh, direct-from-source job listings across major global employers instantly using freeform natural language queries and category exploration, eliminating rigid keyword matching and ATS search friction.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Multi-provider Natural Language query parser using free online LLMs (Groq Llama 3.3, Google Gemini 2.5/1.5 Flash, OpenRouter free models) with structured JSON filter extraction.
- [ ] Category-first and broad-role exploration (e.g. "product entry level", "quantitative finance new grad", "infrastructure engineer") without rigid title requirements.
- [ ] Direct ATS job aggregation engine connecting to public API feeds (Greenhouse, Lever, Ashby, Workday public endpoints) across top global employers.
- [ ] AI-assisted and BeautifulSoup scraper pipeline (ScrapeGraph-ai integration) for custom enterprise career portals.
- [ ] Hybrid indexed database (SQLite/Turso) for instant sub-100ms search results with background sync + on-demand live fetch for specific firm queries.
- [ ] Multi-faceted filtering system: Country/Region, Remote status, Industry Domain, Seniority, and Posting Date freshness.
- [ ] High-craft card-based UI displaying job title, employer, domain badge, location, direct career site apply CTA, and prominently featured posting date (relative + exact).
- [ ] Community intelligence scraper (Reddit & public forums) for interview timelines, company reviews, and preparation advice.

### Out of Scope

- [Automated bot application submission] — High anti-bot risk and ethical concerns; all applications link directly to official employer career sites.
- [Paid third-party job board APIs] — Entire architecture must run and host for free using free tiers and public ATS endpoints.
- [User authentication / paywall] — Keep the search friction-free with immediate utility; local storage for bookmarks/saved jobs.

## Context

- **Tech Stack**: Python (FastAPI) backend for scraping, ATS ingestion, SQLite caching, and LLM orchestration; React (Vite) frontend with modern Vanilla CSS design system.
- **Free Hosting**: Python backend deployable on Hugging Face Spaces or Render (Free); Frontend deployable on Vercel or Cloudflare Pages (Free).
- **Design Philosophy**: Adheres to `frontend-skill` (anti-slop, clean visual hierarchy, optical balance, Apple fluid motion, keyboard accessibility).

## Constraints

- **Hosting & Model Cost**: Zero-cost operating model utilizing free LLM API tiers (Groq, Gemini, OpenRouter) and free cloud hosts.
- **Latency**: Sub-100ms search queries against local/cached database; resilient fallbacks and timeouts on external scrapers.
- **Data Integrity**: Accurate parsing of job publication dates (`date_posted`) to avoid stale listings.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Python (FastAPI) + React (Vite) | Native Python support for ScrapeGraph-ai, scraping tools, and LLMs paired with responsive modern UI | — Pending |
| Multi-provider LLM Adapter | Free-tier resilience across Groq, Gemini, and OpenRouter with mock/regex offline fallback | — Pending |
| Hybrid DB + On-Demand Fetch | Instant (<100ms) indexed searches for thousands of jobs with on-demand fresh sync | — Pending |
| Direct ATS Endpoints First | Greenhouse, Lever, Ashby, and Workday endpoints provide structured JSON with 0 lag and 0 ban risk | — Pending |
| Phase 2 Community Insights | Keeps Phase 1 focused on search, filtering, and cards; layers Reddit sentiment afterwards | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-10-03 after initialization*
