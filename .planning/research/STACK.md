# Stack Research

**Domain:** Multi-Firm Career Portal Aggregator & NL Job Discovery Engine
**Researched:** 2026-10-03
**Confidence:** HIGH

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| **Python** | 3.11+ | Backend Runtime | First-class ecosystem for AI/LLM SDKs, scraping tools (ScrapeGraph-ai, BS4), and data parsing. |
| **FastAPI** | 0.115+ | Web Framework & API | High-performance async ASGI framework with automatic OpenAPI docs and native Pydantic v2 support. |
| **SQLite (via aiosqlite / SQLAlchemy)** | 3.45+ | Persistent Job Cache | Zero-config, blazing sub-millisecond local reads, self-contained, no paid DB host required. |
| **React + Vite** | 19.x / 6.x | Frontend UI Layer | Instant HMR, minimal footprint, robust ecosystem for modern card layouts and responsive UX. |
| **TypeScript** | 5.7+ | Frontend Type Safety | Guarantees contract alignment with FastAPI Pydantic job models. |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| **httpx** | 0.28+ | Async HTTP Client | Fast concurrent fetching of public ATS endpoints (Greenhouse, Lever, Ashby, Workday). |
| **BeautifulSoup4 + lxml** | 4.12+ | HTML Parsing | Fast extraction of unformatted career pages without heavy browser overhead. |
| **ScrapeGraph-ai** | 1.10+ | AI Web Scraper Pipeline | Intelligent LLM-driven graph extraction for unstructured custom enterprise career portals. |
| **groq** | 0.15+ | Free LLM API Client | Ultra-fast inference (<500ms) with Llama 3.3 70B on Groq free cloud tier. |
| **google-genai** | 1.0+ | Gemini Flash API | Reliable fallback free-tier LLM for structured parameter extraction. |
| **lucide-react** | 0.475+ | UI Iconography | Crisp, lightweight icons for badges, locations, domains, and actions. |

### Development & Hosting Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| **Hugging Face Spaces / Render** | Free Backend Hosting | Runs FastAPI Docker/Python container for $0/month. |
| **Vercel / Cloudflare Pages** | Free Frontend CDN | Global edge deployment with zero cold starts for Vite static builds. |
| **GitHub Actions** | Automated Cron Sync | Daily run to refresh ATS boards of top 50+ major firms into SQLite cache for free. |

## Installation

```bash
# Backend (Python)
pip install fastapi uvicorn httpx pydantic beautifulsoup4 lxml aiosqlite groq google-genai python-dotenv

# Optional AI Scraper
pip install scrapegraphai

# Frontend (Node)
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install lucide-react
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| **FastAPI (Python)** | Next.js (Node.js) | Next.js is great for single-repo JS apps, but lacks native access to Python's ScrapeGraph-ai and Python AI libraries. |
| **SQLite / aiosqlite** | PostgreSQL / Supabase | Supabase is great for multi-user apps; SQLite is simpler, zero maintenance, and instant for local/single-tenant caching. |
| **Groq / Gemini Free** | OpenAI GPT-4o-mini | OpenAI requires paid API credits ($5 min), whereas Groq and Gemini AI Studio provide permanent free tiers. |
| **Direct ATS JSON API** | Headless Browser (Selenium/Playwright) | Direct endpoints are 50x faster (200ms vs 10s), consume 99% less memory, and avoid bot protection blocks. |

## What NOT to Use

- **Heavy Headless Browsers on Every Request**: Running Playwright/Puppeteer per search causes 15-second response lags and crashes free-tier cloud containers (512MB RAM limits).
- **Hardcoded Scraping Selectors**: Fragile CSS classes break weekly; prefer direct JSON feeds (Greenhouse/Lever/Ashby) and semantic LLM extraction for custom sites.
- **Paid Aggregator APIs (JSearch, RapidAPI)**: Defeats the zero-cost project goal; public career sites expose open feeds.
