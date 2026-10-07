# Pitfalls & Risk Mitigation: Milestone v5.0

## Critical Pitfalls & Mitigation Strategies

### 1. The "Ghost Job" & Stale Listing Trap
- **The Pitfall**: Pure `upsert` operations add newly posted jobs but never remove closed or expired jobs. Over months of batch scraping, the database accumulates thousands of dead listings whose links return HTTP 404.
- **Mitigation Strategy**: Implement sync pass timestamps (`sync_session_id` or `last_seen_at`). Any job belonging to company `C` not present in the current sync session is marked `closed` or purged.

### 2. High-Concurrency IP Throttling (HTTP 429)
- **The Pitfall**: Running an unconstrained async loop across 200+ career sites triggers IP rate limits and temporary blocks from ATS providers (especially Lever and Ashby).
- **Mitigation Strategy**:
  - Bound global concurrency via `asyncio.Semaphore(10-15)`.
  - Group targets by ATS host and apply per-host polite delays (100-250ms).
  - Rotate standard realistic browser `User-Agent` headers.
  - Exponential backoff with jitter on HTTP 429 / 503.

### 3. Reddit Scraping Rate Limits & Structure Changes
- **The Pitfall**: Reddit's unauthenticated JSON search endpoints (`/r/{subreddit}/search.json`) aggressively block generic python HTTP clients (HTTP 429 Too Many Requests).
- **Mitigation Strategy**:
  - Send custom descriptive User-Agent strings (`CareerLoom/2.0 (by /u/careerloom_bot)`).
  - Cache Reddit query results aggressively (24–48 hours TTL).
  - Run discovery in batch mode rather than synchronous real-time requests.

### 4. Broad Role Title Ambiguity in Indian Startups
- **The Pitfall**: Indian startups frequently use idiosyncratic titles like "Founder's Office Associate", "Growth Hacker", "Category Manager", "Product Lead", "Program Manager", which may be missed by strict engineering/product filters.
- **Mitigation Strategy**:
  - Explicit taxonomy mapping in `taxonomy.py`:
    - "Product Management": APM, PM, SPM, GPM, Product Lead, Technical PM, Product Ops, Category Manager (Product).
    - "Strategy & Consulting": Management Consultant, Associate Consultant, Strategy & Ops, Founder's Office, Chief of Staff, Business Analyst, Corporate Strategy.
  - Multi-token semantic matching and title normalization.

### 5. SQLite Write Lock Contention During Continuous Batch Runs
- **The Pitfall**: If batch workers write individual job records concurrently, SQLite can throw `sqlite3.OperationalError: database is locked`.
- **Mitigation Strategy**:
  - SQLite WAL mode (`PRAGMA journal_mode=WAL`) and `PRAGMA synchronous=NORMAL`.
  - Batch writes at the company level using single transactions (`db.executemany`) rather than individual record writes.
