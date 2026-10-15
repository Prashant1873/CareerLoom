---
phase: 12-reddit-discovery-pipeline-indian-ecosystem-catalog-scaling
plan: 02
subsystem: catalog
tags: [catalog_scaling, partitioned_datasets, seed_targets, run_discovery, pytest]
provides:
  - Partitioned catalog datasets in backend/app/data/targets/ (159 startups, 42 conglomerates, 32 consulting = 233 targets)
  - Standardized taxonomy tags ('product', 'strategy', 'tech', 'founders_office', 'consulting', 'leadership', 'operations')
  - Strict tier classification ('startup', 'unicorn', 'conglomerate', 'consulting')
  - Idempotent seed_targets.py preserving live scrape telemetry (job_count, last_scraped_at, last_status)
  - Standalone CLI runner backend/scripts/run_discovery.py with ANSI summary reporting
  - Sub-20ms indexed SQLite query latency across tiers and role tags
  - Automated test suite tests/test_catalog_scaling.py with 100% pass rate
affects: [backend, catalog, database, targets]
actuals:
  tasks: 3
  duration: 6min
tech-stack:
  added: []
  patterns: [partitioned JSON catalog, idempotent database upsert, telemetry preservation, headless CLI orchestration]
key-files:
  created:
    - backend/app/data/targets/indian_startups.json
    - backend/app/data/targets/indian_conglomerates.json
    - backend/app/data/targets/strategy_consulting.json
    - backend/scripts/build_catalog_partitions.py
    - backend/scripts/run_discovery.py
    - tests/test_catalog_scaling.py
  modified:
    - backend/scripts/seed_targets.py
    - backend/app/db/database.py
    - tests/test_targets_db.py
    - neural_map.md
key-decisions:
  - "Partitioning structure: split 233+ targets across indian_startups.json (159), indian_conglomerates.json (42), and strategy_consulting.json (32) for maintainability and modular ingestion"
  - "Telemetry preservation: upsert conflict resolution preserves job_count, last_scraped_at, and last_status on repeat seed passes"
  - "CLI discovery runner: headless execution with configurable subreddits, force-refresh, registry sync, and ANSI summary formatting"
duration: 6min
completed: 2026-10-08
status: complete
---

# Phase 12 Plan 02 Summary: Ecosystem Catalog Scaling (233 Targets), Partitioned Datasets & Discovery CLI

**Delivered complete ecosystem catalog scaling to 233 Indian employers partitioned across startups, conglomerates, and management consulting, refactored idempotent database seeder, headless discovery CLI runner, and test suite with 100% pass rate.**

## Accomplishments
- Generated three partitioned JSON catalogs in `backend/app/data/targets/`:
  - `indian_startups.json`: 159 high-growth tech startups and unicorns (fintech, quick commerce, SaaS, deeptech, mobility, healthtech, consumer internet).
  - `indian_conglomerates.json`: 42 premier Indian business houses and IT giants (Tata, Reliance, Infosys, Wipro, L&T, Mahindra, Aditya Birla, Godrej, ITC, Bajaj, HDFC, ICICI, etc.).
  - `strategy_consulting.json`: 32 elite management and strategy consulting practices (McKinsey, BCG, Bain, Kearney, Oliver Wyman, Strategy&, Alvarez & Marsal, Arthur D. Little, Dalberg, etc.).
- Standardized taxonomy to strictly validated role tags (`product`, `strategy`, `tech`, `founders_office`, `consulting`, `leadership`, `operations`) and official category tiers (`startup`, `unicorn`, `conglomerate`, `consulting`).
- Enhanced `backend/app/db/database.py` and `backend/scripts/seed_targets.py` with idempotent upsert preserving live scraper telemetry, active job counts, and status timestamps across multiple seed cycles.
- Created `backend/scripts/run_discovery.py` headless CLI runner providing automated Reddit mining, candidate entity extraction, multi-ATS probing, and registry synchronization with ANSI summary tables.
- Built comprehensive test suite `tests/test_catalog_scaling.py` covering partition constraints, schema validation, telemetry-preserving re-seed, sub-20ms indexed querying, and CLI dry-run/mock execution. All 4 tests passed; all 65 tests in the project suite passed with zero regressions.

## Task Verification
1. **Task 1: Create Partitioned JSON Catalog Files for 220+ Indian Target Companies** - Verified via `test_catalog_files` confirming 233 total targets, valid URLs, unique slugs, and clean taxonomy.
2. **Task 2: Refactor seed_targets.py to Idempotently Ingest Partitioned Datasets** - Verified via `test_seed_targets` confirming >= 220 records inserted and live telemetry (`job_count`, `last_scraped_at`, `last_status`) preserved on re-seed.
3. **Task 3: Build CLI Discovery Runner (run_discovery.py) & Verify Catalog Scaling** - Verified via `test_run_discovery_cli` and `test_scaled_targets_query` verifying sub-20ms query latency across consulting, conglomerate, product, and strategy filters.

## Phase 12 Completion Status
Both Plan `12-01` and Plan `12-02` are complete. Phase 12 is fully delivered.
