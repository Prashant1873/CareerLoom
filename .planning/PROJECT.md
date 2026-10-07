# CareerLoom (Global Job Discovery Engine)

## What This Is

CareerLoom is an intelligent job discovery engine that searches career portals across major global firms (tech, finance, consulting, healthcare) across domains, companies, and countries. Powered by free online AI models (Groq / Gemini / OpenRouter), it translates natural language queries and broad role categories (e.g., "product entry level", "junior machine learning remote") into structured searches, displaying verified direct listings in high-craft cards with exact posting dates. Phase 2 introduces community intelligence from Reddit and public career forums for interview timelines and insider reviews.

## Core Value

Empowers candidates to discover fresh, direct-from-source job listings across major global employers instantly using freeform natural language queries and category exploration, eliminating rigid keyword matching and ATS search friction.

## Current Milestone: v5.0 Indian Career Repository & Continuous Batch Scraping Engine

**Goal:** Establish an extensive SQLite-backed repository of hundreds of Indian career portals (popular startups, unicorns, established enterprises, strategy consulting firms) discovered via Reddit and web feeds, with heavy emphasis on Product Management and Strategy Consulting roles, powered by an automated continuous batch scraping pipeline.

**Target features:**
- SQLite Career Targets Registry (`career_targets` table) storing company metadata, career URLs, ATS connectors, scraping status, role focus tags, and sync timestamps.
- Reddit & Public Forum Discovery Pipeline querying `r/developersIndia`, `r/IndianStartups`, `r/ProductManagement`, `r/consulting`, `r/bangalore` to identify top companies and their careers endpoints.
- Massive expansion across Indian ecosystem: Tech Startups/Unicorns, Established Conglomerates (Tata, Reliance, Infosys, etc.), Global Strategy Consulting (McKinsey, BCG, Bain, Kearney, Big 4 India, etc.), and Fintech/Consumer.
- Specialized Taxonomy & Classifiers for Product Management (APM, PM, SPM, GPM, ProdOps) and Strategy Consulting (Associate, Consultant, Chief of Staff, Strategy & Ops, BizOps).
- High-Throughput Continuous Batch Scraper (`sync_batch.py`, API endpoint) with concurrency limits, dead-link handling, job deduplication, and scheduled cron execution.
- Frontend Career Repository Directory view with 1-click filtering for Product Management and Strategy Consulting tracks.

## Requirements

### Validated

- ✓ Direct ATS job aggregation engine connecting to public API feeds (Greenhouse, Lever, Ashby) across top global employers — Phase 1
- ✓ Normalized `JobItem` schema with timezone-aware UTC date parser (`date_posted`) — Phase 1
- ✓ Persistent SQLite storage with sub-50ms indexed queries and on-demand live fetch — Phase 1
- ✓ Multi-provider Natural Language query parser using free online LLMs (Groq Llama 3.3, Google Gemini Flash, OpenRouter free models) with structured JSON filter extraction & regex fallback — Phase 2
- ✓ Category-first and broad-role exploration with 36 canonical tracks (e.g. "product entry level", "machine learning new grad") without rigid title requirements — Phase 2
- ✓ Multi-faceted filtering system: Country/Region expansion, Remote status, Industry Domain, Seniority, and Posting Date freshness — Phase 2
- ✓ High-craft card-based UI displaying employer, title, domain, location, direct apply CTA, dual date posted (relative + exact), and bookmarks — Phase 3
- ✓ BeautifulSoup4 & LLM-assisted scraper pipeline for custom enterprise career portals without ATS feeds — Phase 4
- ✓ Community intelligence (Reddit insights & hiring roadmaps) — Phase 5, Phase 8, Phase 10
- ✓ Desktop-Grade 3-Column Obsidian Control Center — Phase 6, Phase 7, Phase 8
- ✓ Massive Global Portal Expansion (237 firms, 16k+ live listings) — Phase 9
- ✓ India Launch & Indian Leads Engine (51+ Indian tech unicorns, 1,478 listings, India Direct controls, CTC badges, referral engine) — Phase 10

### Active

- [ ] SQLite Career Targets Registry (`career_targets`) for managing hundreds of company career endpoints, scraping health, and metadata.
- [ ] Automated Reddit & forum discovery pipeline to extract top Indian startups, unicorns, established enterprises, and consulting firms.
- [ ] Massive Indian company directory expansion across Startups, Conglomerates, and Strategy Consulting firms.
- [ ] Dedicated Product Management and Strategy Consulting role taxonomies, tracks, and classifiers.
- [ ] High-throughput continuous batch scraping engine with scheduled / on-demand triggers and stale job pruning.
- [ ] Frontend Career Directory Hub and dedicated PM & Strategy Consulting exploration views.

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
| Python (FastAPI) + React (Vite) | Native Python support for ScrapeGraph-ai, scraping tools, and LLMs paired with responsive modern UI | ✓ Good |
| Direct ATS Endpoints First | Greenhouse, Lever, and Ashby public feeds provide structured JSON with 0 lag and 0 anti-bot blocks | ✓ Good |
| Hybrid DB + On-Demand Fetch | Instant (<50ms) indexed searches for thousands of jobs with on-demand fresh sync | ✓ Good |
| Multi-provider LLM Adapter + Regex Fallback | Free-tier resilience across Groq, Gemini, and OpenRouter with instant rule-based fallback | ✓ Good |
| Category & Track Taxonomy | Canonical mapping of 8 domains and 36 curated tracks to bridge user vernacular and ATS data | ✓ Good |
| Anti-Slop Vanilla CSS Tokens | Zero-bloat CSS variable tokens complying with frontend-skill without heavy Tailwind runtime | ✓ Good |
| Lightweight BS4 & LLM Scraper | Replaced heavy multi-GB ScrapeGraphAI with polite BS4 cleaner + LLM adapter to preserve free cloud resource limits | ✓ Good |

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
*Last updated: 2026-10-08 for Milestone v5.0*
