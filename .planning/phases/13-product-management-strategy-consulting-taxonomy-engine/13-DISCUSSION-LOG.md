# Phase 13: Product Management & Strategy Consulting Taxonomy Engine - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-10-08
**Phase:** 13-product-management-strategy-consulting-taxonomy-engine
**Areas discussed:** Role Track Taxonomy & Hierarchy, Semantic Classifier & Schema Extension, Sub-50ms Search & Query Expansion, Job Catalog Backfill Migration

---

## Role Track Taxonomy & Hierarchy

### Track Hierarchy Structure
| Option | Description | Selected |
|---|---|:---:|
| Dedicated Category Split | Promote high-visibility specializations like 'founders_office' or 'tpm' into top-level standalone categories alongside 'product' and 'consulting_strategy' | ✓ |
| Nested Sub-Tracks under canonical categories | Keep existing 8 top categories stable, adding structured sub_tracks with dedicated synonyms and skills metadata | |

**User's choice:** Dedicated Category Split — Promote high-visibility specializations like 'founders_office' or 'tpm' into top-level standalone categories alongside 'product' and 'consulting_strategy'.

### Standalone Category Partitioning
| Option | Description | Selected |
|---|---|:---:|
| Full 6-Way Granular Split | Dedicated categories for 'product', 'technical_product', 'product_ops', 'management_consulting', 'corporate_strategy', and 'founders_office' | ✓ |
| Focused 4-Way Expansion | Add 'founders_office' and 'technical_product' as dedicated categories alongside 'product' and 'consulting_strategy' | |
| 3-Way Focused Split | Add 'founders_office' as the only new standalone category | |

**User's choice:** Full 6-Way Granular Split — Dedicated categories for 'product', 'technical_product', 'product_ops', 'management_consulting', 'corporate_strategy', and 'founders_office'.

### Broad Query Resolution & Clustering
| Option | Description | Selected |
|---|---|:---:|
| Domain Cluster Grouping with Alias Fallback | Granular categories have a parent_cluster (e.g. 'product_cluster', 'strategy_cluster'); broad queries like 'product' or 'strategy' match the entire cluster unless a specific category is requested | ✓ |
| Strict Independent Filtering | Each of the 6 categories is strictly filtered by exact category ID | |

**User's choice:** Domain Cluster Grouping with Alias Fallback.

### Seniority Mapping Model
| Option | Description | Selected |
|---|---|:---:|
| Unified Canonical Levels with Role Aliases | Keep canonical levels ('entry', 'mid', 'senior', 'lead', 'intern') in database, and map track titles (APM -> entry, Associate Consultant -> entry, Engagement Manager -> lead) deterministically | ✓ |
| Domain-Specific Seniority Enum | Add consulting-specific levels ('analyst', 'associate', 'engagement_manager', 'partner') alongside tech levels | |

**User's choice:** Unified Canonical Levels with Role Aliases.

---

## Semantic Classifier & Schema Extension

### Job Schema Extension for Track
| Option | Description | Selected |
|---|---|:---:|
| Add 'track' column to JobItem and SQLite jobs table | Persist detected granular track (e.g. 'Chief of Staff', 'APM', 'BizOps', 'TPM') alongside 'category' for precise faceted filtering and badges | ✓ |
| Category-only persistence | Store the 6 granular categories in 'category' without adding a new column to jobs table | |

**User's choice:** Add 'track' column to JobItem and SQLite jobs table.

### Classifier Mechanism
| Option | Description | Selected |
|---|---|:---:|
| High-Performance Regex Pattern Engine | Pure compiled regex & synonym dictionary (<0.1ms per title, zero API cost, 100% deterministic and offline-resilient) | ✓ |
| Hybrid Rule-First with Async LLM Fallback | Regex first; if classified as 'general' and ambiguous keywords exist, query free-tier LLM | |

**User's choice:** High-Performance Regex Pattern Engine.

### Context-Aware Classification
| Option | Description | Selected |
|---|---|:---:|
| Context-Aware with Employer Sector Hints | Classifier accepts company/domain hint; if employer is a Consulting firm, generic titles ('Associate', 'Business Analyst') correctly resolve to 'management_consulting' | ✓ |
| Pure Title-Only String Matching | Classifier evaluates role title string in isolation without employer sector context | |

**User's choice:** Context-Aware with Employer Sector Hints.

### Collision & Precedence Resolution
| Option | Description | Selected |
|---|---|:---:|
| Explicit Priority Order (Specific over Broad) | Specialized rules trigger first: 'founders_office' > 'technical_product' > 'product_ops' > 'management_consulting' > 'corporate_strategy' > generic 'product' | ✓ |
| Longest Matched Phrase Precedence | Highest character length match wins across regex patterns | |

**User's choice:** Explicit Priority Order (Specific over Broad).

---

## Sub-50ms Search & Query Expansion

### SQLite Indexing Strategy
| Option | Description | Selected |
|---|---|:---:|
| B-Tree Composite Indexes | Add idx_jobs_category_track and idx_jobs_track indexes on jobs table (<5ms lookup on SQLite, lightweight, zero FTS overhead) | ✓ |
| SQLite FTS5 Full-Text Search Table | Create an FTS5 virtual table indexing title, description, and tags for bm25 relevance scoring | |

**User's choice:** B-Tree Composite Indexes.

### Track Query Expansion Logic
| Option | Description | Selected |
|---|---|:---:|
| Hybrid Track Match with Synonym Fallback | Query filters primarily by 'track = ?', but expands with track synonyms (OR title LIKE ?) if fewer than 5 results are returned, preventing zero-result drop-offs | ✓ |
| Strict Exact Track Matching | Query strictly filters by 'track = ?', relying entirely on the accuracy of the ingestion classifier | |

**User's choice:** Hybrid Track Match with Synonym Fallback.

### NLP Fast-Path Parsing
| Option | Description | Selected |
|---|---|:---:|
| Fast-path taxonomy match, then LLM if less accurate and matching results | Resolve prompt against taxonomy tracks and regex patterns upfront; if unambiguous track/metro detected, return structured query immediately; invoke LLM only if ambiguous or insufficient results | ✓ |
| Always-LLM with Taxonomy Validation | Always invoke Groq/Gemini LLM parser first, then validate and reconcile against taxonomy tracks | |

**User's choice:** First fast path taxonomy match, then LLM if less accurate and matching results.

### Tracks API Response Schema
| Option | Description | Selected |
|---|---|:---:|
| Enriched Tracks API with Live Job Counts | GET /api/categories/tracks returns tracks, parent cluster, and cached active job counts for instant UI badge display | ✓ |
| Static Metadata API | GET /api/categories/tracks returns tracks and metadata without querying database job counts | |

**User's choice:** Enriched Tracks API with Live Job Counts.

---

## Job Catalog Backfill Migration

### Backfill Scope
| Option | Description | Selected |
|---|---|:---:|
| Full Idempotent Re-classification | Scan and update all jobs in SQLite table to populate new 'track' and re-align categories in a single transaction (~1-2 seconds with fast regex) | ✓ |
| Targeted Migration Only | Only update jobs where 'track IS NULL' or current category is 'product' / 'consulting_strategy' / 'general' | |

**User's choice:** Full Idempotent Re-classification.

### Migration Execution Trigger
| Option | Description | Selected |
|---|---|:---:|
| Automatic Startup Migration + CLI Script | init_db() automatically executes schema migration (ALTER TABLE ADD COLUMN track) and reclassifies existing jobs on launch, with a dedicated backend/scripts/reclassify_jobs.py CLI runner | ✓ |
| Manual CLI Script Only | Dedicated backend/scripts/reclassify_jobs.py script must be invoked explicitly | |

**User's choice:** Automatic Startup Migration + CLI Script.

### Observability & Logging
| Option | Description | Selected |
|---|---|:---:|
| Detailed Category Breakdown Logs | Output a structured distribution table (total jobs, counts per new category, top tracks detected, elapsed ms) for observability | ✓ |
| Concise Summary Log | Print a single-line summary | |

**User's choice:** Detailed Category Breakdown Logs.

### Safety & Dry-Run Guarantees
| Option | Description | Selected |
|---|---|:---:|
| Non-Destructive Update with Dry-Run Flag | Only mutate category, seniority, and track columns; preserve all IDs/dates/tags; support --dry-run CLI flag to test reclassification distributions before write | ✓ |
| Direct In-Place Commit Only | Simple direct in-place update without dry-run preview flag | |

**User's choice:** Non-Destructive Update with Dry-Run Flag.

---

## Agent's Discretion
- Exact regex patterns and word boundary expressions for each new category and track.
- Number of track synonyms mapped per role track in `CATEGORIES_TAXONOMY`.
- In-memory caching TTL for category track job counts (e.g., 60 seconds).

## Deferred Ideas
None — discussion stayed within phase scope.
