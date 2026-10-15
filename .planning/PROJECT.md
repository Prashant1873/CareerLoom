# CareerLoom (Global Job Discovery Engine)

## What This Is

CareerLoom is an intelligent job discovery engine that searches career portals across major global firms (tech, finance, consulting, healthcare) across domains, companies, and countries. Powered by free online AI models (Groq / Gemini / OpenRouter), it translates natural language queries and broad role categories (e.g., "product entry level", "junior machine learning remote") into structured searches, displaying verified direct listings in high-craft cards with exact posting dates. Phase 2 introduces community intelligence from Reddit and public career forums for interview timelines and insider reviews.

## Core Value

Empowers candidates to discover fresh, direct-from-source job listings across major global employers instantly using freeform natural language queries and category exploration, eliminating rigid keyword matching and ATS search friction.

## Current Milestone: v6.0 Obsidian Light & Dual-Theme Ergonomics

**Goal:** Deliver a high-craft, anti-slop Light Mode for CareerLoom adhering strictly to `frontend-skill` (WCAG 2.2 AA contrast standards, hue-tinted cool slate / obsidian porcelain neutral architecture, calibrated semantic badge fills, and fluid theme switching without unstyled flash).

**Target features:**
- Dual-theme token architecture in CSS variables (`data-theme="dark"` and `data-theme="light"`).
- Hue-tinted cool slate / obsidian porcelain neutral ramp (eliminating washed out generic AI grays).
- WCAG 2.2 AA contrast compliance across all text layers (primary > 14:1, secondary > 7:1, muted > 4.5:1, brand emerald > 4.5:1).
- Accessible dual-theme badge system (subtle background tints with darkened high-contrast typography).
- Responsive, viscoelastic theme switcher component in navigation rail and mobile headers.
- Zero-flash theme hydration via local storage and system `prefers-color-scheme` support.
- Comprehensive component retheming across 3-column control center, modals, drawers, and omnibox stream.

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
- ✓ SQLite Career Targets Registry (`career_targets`) tracking 220+ employers, sync health, and scrape metrics — Phase 11
- ✓ Automated Reddit & forum discovery pipeline across Indian ecosystem (`r/developersIndia`, etc.) — Phase 12
- ✓ Dedicated Product Management and Strategy Consulting role taxonomies, tracks, and sub-50ms search — Phase 13
- ✓ Continuous batch scraping pipeline with async runner, background scheduler, and stale job reconciler — Phase 14
- ✓ Frontend Career Directory Hub and dedicated PM & Strategy Consulting 1-click exploration views — Phase 15

### Active

- [ ] Dual-theme CSS token architecture with calibrated Obsidian Porcelain & Cool Slate neutral ramp.
- [ ] WCAG 2.2 AA contrast matrix verification ensuring 4.5:1 text and 3:1 control compliance across both themes.
- [ ] Refactoring hardcoded dark background values in `App.css` and `CareerDirectoryModal.css` into semantic variables.
- [ ] Interactive viscoelastic theme toggle in navigation rail and header with system preference synchronization.
- [ ] Complete retheming pass for Master Job Stream, Job Cards, Inspector Pane, Lead Modal, and Career Directory.

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
