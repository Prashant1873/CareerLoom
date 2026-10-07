# Project Research Summary: Milestone v5.0

## Executive Summary
Milestone v5.0 transitions CareerLoom from a hardcoded catalog to an enterprise-scale **Career Portal Repository & Continuous Batch Scraping Engine**. With a dedicated SQLite registry (`career_targets`), Reddit-powered discovery across Indian startup and consulting communities, heavy taxonomy enrichment for Product Management and Strategy Consulting, and a concurrency-bounded batch scraper with stale job pruning, CareerLoom ensures a self-refreshing, verified directory of high-demand Indian career openings.

## Key Findings

### 1. Stack & Architecture Additions
- **Career Targets Registry**: SQLite `career_targets` table storing company metadata, career links, ATS types, role focus tags, sync health, and scrape metrics.
- **Reddit Discovery Engine**: Async scanner querying `r/developersIndia`, `r/IndianStartups`, `r/ProductManagement`, `r/consulting`, and `r/bangalore` to uncover high-growth companies and career links.
- **High-Throughput Batch Engine**: `sync_batch.py` utilizing `asyncio.Semaphore(15)` with per-domain polite backoff and atomic reconciliation to purge expired/closed listings.
- **Specialized Taxonomy**: Dedicated classifications for Product Management (APM, PM, SPM, GPM, TPM, ProdOps) and Strategy Consulting (Consultant, Chief of Staff, Strategy & Ops, BizOps).

### 2. Table Stakes vs Differentiators
- **Table Stakes**:
  - `career_targets` table with 200+ Indian companies (Startups, Unicorns, Conglomerates, Strategy Consulting).
  - Batch ingestion pipeline with stale job pruning.
  - Product Management and Strategy Consulting search tracks.
- **Differentiators**:
  - Frontend Company Directory & Career Hub.
  - 1-click PM & Strategy quick pills.
  - Reddit discovery automation converting mentions to monitored targets.

### 3. Watch Out For
- **Ghost Jobs**: Solved via sync session timestamps and automated pruning of unverified postings.
- **Rate Limits (429)**: Solved via bounded concurrency, per-host delays, and realistic user-agents.
- **Lock Contention**: Solved via SQLite WAL mode and transaction-batched company writes.

## Implications for Roadmap

The recommended phase structure continues numbering from Phase 10:
- **Phase 11: Career Targets Registry & Database Architecture** — SQLite `career_targets` schema, CRUD endpoints, seed catalog migration (200+ firms), and stale job reconciler.
- **Phase 12: Reddit Discovery Pipeline & Indian Ecosystem Catalog Scaling** — Reddit scanner (`r/developersIndia`, `r/IndianStartups`, `r/ProductManagement`, `r/consulting`), entity extractor, and expansion to top Indian tech startups, unicorns, conglomerates, and consulting firms.
- **Phase 13: Product Management & Strategy Consulting Taxonomy Engine** — Domain ontology expansion, role track mapping, semantic title matching, and API filter enhancements.
- **Phase 14: Continuous Batch Scraping Pipeline & Ingestion Automation** — High-concurrency batch runner (`sync_batch.py`), scheduled periodic sync worker, error isolation, and metrics tracking.
- **Phase 15: Frontend Career Directory Hub & Role Experience** — Obsidian dark Company Directory modal/view, 1-click PM and Strategy filter ribbons, role badges, and live sync indicators.
