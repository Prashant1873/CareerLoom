# Phase 12: Reddit Discovery Pipeline & Indian Ecosystem Catalog Scaling - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-10-08
**Phase:** 12-reddit-discovery-pipeline-indian-ecosystem-catalog-scaling
**Areas discussed:** Reddit Mining & Caching Engine, Entity Extraction & ATS Probing, Catalog Scaling (220+ Targets)

---

## Reddit Mining & Caching Engine

### Reddit Query Protocol
| Option | Description | Selected |
|---|---|:---:|
| Public Reddit JSON API (.json) | Custom User-Agent, polite per-request delay (1.0s), exponential backoff | ✓ |
| Public RSS/Atom feeds | reddit.com/r/{sub}/.rss parsed with lightweight XML parser | |
| Reddit official OAuth API | Requires registered Reddit developer credentials | |

**User's choice:** Public Reddit JSON API (.json) with custom User-Agent, polite per-request delay (1.0s), and exponential backoff.

### Cache Persistence Location
| Option | Description | Selected |
|---|---|:---:|
| SQLite table (discovery_cache) | Raw payload, post metadata, and 24h TTL expiry check | ✓ |
| Local JSON cache file | Stored in backend/app/data/ with timestamped post snapshots | |
| In-memory dictionary | 24h TTL, cleared on backend restart | |

**User's choice:** SQLite table (`discovery_cache`) with payload, post metadata, and 24h TTL expiry check.

### Thread Query Strategy
| Option | Description | Selected |
|---|---|:---:|
| Hybrid | Fetch recent 'hot' threads plus targeted keyword search ('hiring', 'referrals', 'openings') for maximum coverage | ✓ |
| Keyword search only | Query Reddit search endpoint with targeted hiring terms per subreddit | |
| Stream only | Fetch newest 50 posts from each subreddit without search queries | |

**User's choice:** Hybrid: Fetch recent 'hot' threads plus targeted keyword search ('hiring', 'referrals', 'openings') for maximum coverage.

### Error Resilience
| Option | Description | Selected |
|---|---|:---:|
| Graceful degradation | Use cached posts, apply exponential backoff on 429, continue with other subreddits without crashing | ✓ |
| Immediate abort | Stop scan immediately on first 429 to avoid IP penalty | |
| Aggressive retry | Retry 3 times with 5s/10s/20s backoff before skipping that subreddit | |

**User's choice:** Graceful degradation: Use cached posts, apply exponential backoff on 429, and continue with other subreddits without crashing.

---

## Entity Extraction & ATS Probing

### Entity Extraction Method
| Option | Description | Selected |
|---|---|:---:|
| Hybrid | Regex + Known Company dictionary matching + ATS URL pattern detection, with optional free-tier LLM fallback for ambiguous threads | ✓ |
| Deterministic only | Pure regex & dictionary lookup for company names and career URLs (zero LLM calls, sub-millisecond) | |
| LLM-first | Send thread title & text to Groq Llama 3.3 for structured JSON entity extraction | |

**User's choice:** Hybrid: Regex + Known Company dictionary matching + ATS URL pattern detection, with optional free-tier LLM fallback for ambiguous threads.

### ATS Probing Strategy
| Option | Description | Selected |
|---|---|:---:|
| Multi-ATS Prober | Inspect HTML for embedded ATS signatures + probe canonical API endpoints (Greenhouse, Lever, Ashby, SmartRecruiters) using async HTTP with 3s timeout | ✓ |
| Strict ATS link matching | Only accept listings that directly contain recognized ATS URLs in Reddit posts | |
| Career page crawler | Fetch homepage and crawl internal links looking for /careers and jobs subpages | |

**User's choice:** Multi-ATS Prober: Inspect HTML for embedded ATS signatures + probe canonical API endpoints (Greenhouse, Lever, Ashby, SmartRecruiters) using async HTTP with 3s timeout.

### Discovered Target Registration
| Option | Description | Selected |
|---|---|:---:|
| Auto-insert into career_targets | Active status if verified (HTTP 200 + active jobs found) and tag role_focus, plus record discovery source in metadata | ✓ |
| Stage in a discovery review table | Require approval before moving to active career_targets | |
| Log to JSON artifact only | Do not modify SQLite career_targets table | |

**User's choice:** Auto-insert into `career_targets` with `status='active'` if verified (HTTP 200 + active jobs found) and tag `role_focus`, plus record discovery source in a dedicated log/metadata.

### Deduplication & Negative Caching
| Option | Description | Selected |
|---|---|:---:|
| Slug deduplication + 7-day negative cache | Prevent repeated probing of existing companies and failed candidate domains | ✓ |
| Check career_targets table only | No negative caching of failed candidate domains | |
| In-memory session deduplication only | Cleared between scanner runs | |

**User's choice:** Slug-based deduplication against `career_targets` + 7-day negative cache for probed domains that failed verification.

---

## Catalog Scaling (220+ Targets)

### Catalog Dataset Structure
| Option | Description | Selected |
|---|---|:---:|
| Sector-partitioned JSON files | backend/app/data/targets/ (startups.json, conglomerates.json, consulting.json) loaded via seed_targets.py | ✓ |
| Single unified JSON catalog file | backend/app/data/indian_catalog_220.json containing all segments | |
| Embedded Python seed dictionaries | Within backend/scripts/seed_targets.py | |

**User's choice:** Sector-partitioned JSON files in `backend/app/data/targets/` (`startups.json`, `conglomerates.json`, `consulting.json`) loaded via `seed_targets.py`.

### Role Focus Taxonomy
| Option | Description | Selected |
|---|---|:---:|
| Standardized enum tags | product, strategy, tech, founders_office, consulting, leadership tailored per sector to directly support Phase 13/15 filtering | ✓ |
| Coarse domain tags only | tech, consulting, conglomerate matching existing categories | |
| Open-ended multi-keyword tags | Based on typical hiring profiles | |

**User's choice:** Standardized enum tags (`product`, `strategy`, `tech`, `founders_office`, `consulting`, `leadership`) tailored per sector to directly support Phase 13/15 filtering.

### Enterprise Target Registration
| Option | Description | Selected |
|---|---|:---:|
| Direct career portal URLs + custom/workday | Verified career URLs for instant 1-click apply links and readiness for Phase 14 batch scrapers | ✓ |
| Restrict catalog to open ATS endpoints | Only companies with Greenhouse, Lever, Ashby, SmartRecruiters | |
| Stub feed endpoints with mock generators | Fallbacks until custom enterprise scrapers are written | |

**User's choice:** Register with direct career portal URLs + `ats_type='custom'`/`'workday'`, with verified career URLs so users get direct 1-click links immediately and batch runners can hook in Phase 14.

### Seed Upsert Semantics
| Option | Description | Selected |
|---|---|:---:|
| Idempotent upsert | Seed with status='active' and last_status='pending', preserving existing job counts and timestamps on re-seed | ✓ |
| Synchronous seed & scrape | Scrape all 220+ targets immediately upon seeding | |
| Destructive replace | Clear career_targets table and re-insert fresh targets every time | |

**User's choice:** Idempotent upsert: Seed with `status='active'` and `last_status='pending'`, preserving any existing job counts and timestamps on re-seed.

---

## Agent's Discretion

- Exact regex patterns for URL and company mention parsing.
- Specific async concurrency semaphore for Reddit scraping and ATS probing (`asyncio.Semaphore(5)` for Reddit, `asyncio.Semaphore(10)` for ATS prober).
- Exact table schema details for `discovery_cache` and `probed_cache`.

## Deferred Ideas

- None — discussion stayed within Phase 12 scope (DISCOVERY-01, DISCOVERY-02, DISCOVERY-03).
