---
phase: 12-reddit-discovery-pipeline-indian-ecosystem-catalog-scaling
plan: 01
subsystem: discovery
tags: [reddit, scanner, ats_prober, discovery_cache, probed_cache, fastapi]
provides:
  - SQLite discovery_cache and probed_cache tables with TTL indexing
  - RedditDiscoveryService querying r/developersIndia, r/IndianStartups, r/ProductManagement, r/consulting, r/bangalore
  - 24h caching with graceful 429 rate limit backoff and error resilience
  - DiscoveryEntityProber with regex extraction and concurrent multi-ATS probing (Greenhouse, Lever, Ashby, SmartRecruiters)
  - Auto-enrollment of verified targets into career_targets and 7-day negative domain caching
  - REST endpoints at /api/discovery/feed and /api/discovery/scan
  - Comprehensive automated test suite (test_reddit_discovery.py) with 100% pass rate
affects: [backend, discovery, database, targets]
actuals:
  tasks: 4
  duration: 5min
tech-stack:
  added: []
  patterns: [SQLite TTL cache, polite public Reddit scraper, concurrent ATS probing, negative cache]
key-files:
  created:
    - backend/app/services/reddit_scanner.py
    - backend/app/services/discovery_prober.py
    - backend/app/api/discovery.py
    - tests/test_reddit_discovery.py
  modified:
    - backend/app/db/database.py
    - backend/app/main.py
key-decisions:
  - "Reddit caching: SQLite discovery_cache with 24h TTL check ensures zero outbound calls on repeat runs"
  - "Multi-ATS probing: concurrent async requests with 3s timeout and negative domain caching (7-day TTL)"
  - "Auto-enrollment: verified targets with >= 1 job upserted into career_targets with role_focus and discovery metadata"
duration: 5min
completed: 2026-10-08
status: complete
---

# Phase 12 Plan 01 Summary: Reddit Discovery Scanner, Caching Engine & Multi-ATS Prober Pipeline

**Delivered automated Reddit career discovery pipeline with SQLite 24h TTL caching, entity extraction, concurrent ATS prober, and REST APIs with 100% test pass rate.**

## Accomplishments
- Extended `backend/app/db/database.py` with `discovery_cache` and `probed_cache` tables, including helper functions `save_discovery_posts`, `get_cached_discovery_posts`, `record_probed_domain`, and `is_domain_probed`.
- Created `RedditDiscoveryService` in `backend/app/services/reddit_scanner.py` supporting hybrid hot + keyword search queries across 5 target subreddits, custom User-Agent, 1.0s polite delays, and graceful degradation on HTTP 429.
- Built `DiscoveryEntityProber` in `backend/app/services/discovery_prober.py` featuring regex ATS URL pattern extraction, company entity detection, concurrent multi-ATS probing (Greenhouse, Lever, Ashby, SmartRecruiters), slug deduplication, and auto-registration into `career_targets`.
- Implemented discovery REST router in `backend/app/api/discovery.py` exposing `GET /api/discovery/feed` and `POST /api/discovery/scan`, integrated into `backend/app/main.py`.
- Authored test suite `tests/test_reddit_discovery.py` with 5 tests covering cache operations, scanner logic, graceful 429 recovery, ATS probing, and REST APIs. All 5 tests passed; full suite of 17 tests passed with zero regressions.

## Task Verification
1. **Task 1: Extend SQLite Schema with Discovery & Probed Cache Tables** - Verified via schema initialization and cache tests.
2. **Task 2: Implement Async RedditDiscoveryService** - Verified via mock HTTP feeds, cache hit assertion, and 429 fallback.
3. **Task 3: Build DiscoveryEntityProber for Multi-ATS Verification** - Verified via candidate parsing, Ashby/Lever/Greenhouse mock probes, and auto-registration.
4. **Task 4: Create Discovery REST Endpoints & Tests** - Verified via FastAPI test client on `/api/discovery/feed` and `/api/discovery/scan`.

## Next Plan Readiness
Ready for Plan `12-02`: Ecosystem Catalog Scaling (220+ Targets) & Seed Partitioning.
