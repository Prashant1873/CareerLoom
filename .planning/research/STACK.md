# Stack Additions & Upgrades: Milestone v5.0

## Overview
Milestone v5.0 introduces an expansive Indian career portal repository, Reddit-driven company discovery, specialized Product Management and Strategy Consulting role indexing, and a continuous high-throughput batch scraping engine.

## Recommended Stack Additions

| Component | Library / Tool | Version | Purpose | Why Recommended |
|-----------|---------------|---------|---------|-----------------|
| **Batch Task Scheduling** | `FastAPI BackgroundTasks` + Asyncio Periodic Worker | Standard / 0.115+ | Continuous batch sync execution | Zero extra dependencies, runs inside existing ASGI event loop, zero memory overhead. |
| **Reddit Thread Discovery** | `httpx` (Async Client) | 0.28+ | Extract company mentions & career URLs from Reddit | Native async, connection pooling, custom User-Agent rotation, robust retry logic. |
| **Career Registry Persistence** | `aiosqlite` (SQLite WAL) | 3.45+ | Persistent `career_targets` table | Embedded, zero maintenance, relational integrity with `jobs` table, sub-5ms queries. |
| **Indian ATS Connectors** | Custom Modular Connectors (`Keka`, `Darwinbox`, `Zoho Recruit`) | In-house | Ingest jobs from Indian HRMS/ATS platforms | Extends existing `BaseConnector` pattern used by Greenhouse, Lever, Ashby, and SmartRecruiters. |
| **HTML Sanitizer & Link Extractor** | `BeautifulSoup4` + `lxml` | 4.12+ | Extract career links and parse job postings | Blazing fast C-based parsing, minimal CPU overhead. |

## What NOT to Add (Strict Avoidance)

- **Celery + Redis / RabbitMQ**: Heavy external brokers requiring background daemon processes and paid hosting tiers. FastAPI's async event loop with `asyncio.Semaphore` provides all necessary queueing and concurrency control.
- **Paid Aggregator APIs (JSearch, RapidAPI, Apify)**: Defeats zero-cost mandate. Public ATS endpoints and Reddit JSON search are free.
- **Headless Browser Runtimes (Playwright / Puppeteer)**: Heavy memory footprint (>1GB RAM) that crashes free-tier cloud containers (Render/Hugging Face 512MB limits). Direct HTTP API feeds and lightweight BS4 crawling are 50x faster.
