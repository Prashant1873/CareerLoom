# Pitfalls Research

**Domain:** Multi-Firm Career Portal Aggregator & NL Job Discovery Engine
**Researched:** 2026-10-03
**Confidence:** HIGH

## Critical Pitfalls & Mitigation Strategies

### 1. Inconsistent or Missing `date_posted` Across Job Boards

- **Warning Signs**: Job cards display "N/A" or "Invalid Date"; cards cannot be sorted chronologically; users see stale jobs from 6 months ago.
- **Root Cause**: Many ATS portals (Workday, custom portals) do not expose an exact ISO creation timestamp or only supply relative strings ("30+ days ago", "Today").
- **Prevention Strategy**:
  - Greenhouse, Lever, and Ashby APIs natively provide explicit timestamps (`updated_at`, `createdAt`).
  - For scrapers without timestamps, use the `first_seen_at` timestamp recorded when the scraper first indexes the listing.
  - Implement a date normalizer function converting relative strings ("2d ago", "Posted today") to normalized UTC datetimes.
- **Phase Mapping**: Phase 1 (Ingestion & Schema Normalization).

### 2. Live Request Scraping Causing Severe Latency Lags

- **Warning Signs**: Search takes 15–30 seconds to return results; UI freezes; free hosting timeouts (Render/HF Spaces timeout at 30–60s).
- **Root Cause**: Attempting to scrape 20+ live career websites synchronously on every user keystroke or search button click.
- **Prevention Strategy**:
  - Enforce the **Hybrid Architecture**: Searches query the indexed SQLite local store (<50ms response time).
  - Background sync updates the top firm boards periodically (or via a lightweight async sync endpoint).
  - Live on-demand scraping is explicitly scoped to a single target company when requested by the user.
- **Phase Mapping**: Phase 1 (Architecture & Database Indexing).

### 3. Free LLM Tier Rate Limits (429 Too Many Requests)

- **Warning Signs**: Natural language search throws errors or fails during user typing bursts; free API keys hit token-per-minute caps.
- **Root Cause**: Sending every keystroke or duplicate search phrase to external LLMs (Groq / Gemini) without debounce or caching.
- **Prevention Strategy**:
  - Implement a query hash cache (`TTLCache` in Python or memory dict): identical or similar queries return cached filter parameters instantly.
  - Debounce user input on frontend (300ms–500ms).
  - Graceful fallback: If LLM returns 429 or network fails, instantly fallback to the regex rule-based query parser without user disruption.
- **Phase Mapping**: Phase 1 (NLP Parser Layer).

### 4. Anti-Bot / CAPTCHA Blocking on Enterprise Career Portals

- **Warning Signs**: Scraper receives HTTP 403 Forbidden or Cloudflare challenge pages when accessing company careers sites.
- **Root Cause**: Using aggressive headless browser crawlers against anti-bot protected domains (Workday, Taleo).
- **Prevention Strategy**:
  - Prioritize Direct ATS public feeds (Greenhouse API, Lever API, Ashby API) which are open JSON APIs intended for job discovery and never blocked.
  - For custom career domains, use respectful headers (`User-Agent: Mozilla/5.0...`), random delays, and fallback to cached data if blocked.
- **Phase Mapping**: Phase 2 (Custom Portal Scrapers).

### 5. Reddit Scraping Blocking & API Restrictions

- **Warning Signs**: Reddit requests return 429 or 401 when fetching company interview discussions.
- **Root Cause**: Reddit's revised API policies restrict authenticated API access; unauthenticated scrapers may get rate limited.
- **Prevention Strategy**:
  - Use Reddit's public `.json` endpoints (e.g. `https://www.reddit.com/r/cscareerquestions/search.json?q={company}&restrict_sr=1`) with a custom descriptive `User-Agent`.
  - Cache Reddit discussion summaries per company for 7 days so repeated searches make 0 network requests.
- **Phase Mapping**: Phase 3 (Community Intelligence).
