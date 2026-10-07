---
phase: 13
slug: product-management-strategy-consulting-taxonomy-engine
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-10-08
---

# Phase 13 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x |
| **Config file** | `pytest.ini` / root config |
| **Quick run command** | `pytest tests/test_taxonomy_engine.py -v` |
| **Full suite command** | `pytest tests/test_taxonomy_engine.py tests/test_taxonomy_search.py -v` |
| **Estimated runtime** | ~4 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_taxonomy_engine.py -v`
- **After every plan wave:** Run `pytest tests/test_taxonomy_engine.py tests/test_taxonomy_search.py -v`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 4 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 13-01-01 | 01 | 1 | TAXONOMY-01, 02 | — | N/A | unit | `pytest tests/test_taxonomy_engine.py -k test_categories_taxonomy -v` | ❌ W0 | ⬜ pending |
| 13-01-02 | 01 | 1 | TAXONOMY-01, 02 | — | N/A | unit | `pytest tests/test_taxonomy_engine.py -k test_classifier_tracks -v` | ❌ W0 | ⬜ pending |
| 13-01-03 | 01 | 1 | TAXONOMY-01, 02 | — | N/A | unit | `pytest tests/test_taxonomy_engine.py -k test_consulting_hints -v` | ❌ W0 | ⬜ pending |
| 13-01-04 | 01 | 1 | TAXONOMY-01, 02 | — | N/A | unit | `pytest tests/test_taxonomy_engine.py -k test_job_model_track -v` | ❌ W0 | ⬜ pending |
| 13-02-01 | 02 | 2 | TAXONOMY-03 | — | N/A | integration | `pytest tests/test_taxonomy_search.py -k test_schema_migration_and_indexes -v` | ❌ W0 | ⬜ pending |
| 13-02-02 | 02 | 2 | TAXONOMY-03 | — | N/A | integration | `pytest tests/test_taxonomy_search.py -k test_query_jobs_sub50ms -v` | ❌ W0 | ⬜ pending |
| 13-02-03 | 02 | 2 | TAXONOMY-03 | — | N/A | integration | `pytest tests/test_taxonomy_search.py -k test_nlp_fast_path -v` | ❌ W0 | ⬜ pending |
| 13-02-04 | 02 | 2 | TAXONOMY-03 | — | N/A | integration | `pytest tests/test_taxonomy_search.py -k test_reclassify_jobs_cli -v` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_taxonomy_engine.py` — unit tests for taxonomy dictionary, cluster resolution, compiled regex classifier, and employer hints
- [ ] `tests/test_taxonomy_search.py` — integration tests for schema migration, sub-50ms search, NLP fast path, and reclassify script

---

## Manual-Only Verifications

| Behavior | Verification Method | Why Automated Test Insufficient |
|----------|---------------------|---------------------------------|
| Sub-50ms query benchmark | Execute 50 sample PM and Strategy queries against active database cache and assert median latency < 50ms | Real SQLite query execution on production database size (~16k records) |
| CLI `--dry-run` vs Live Backfill | Run `python backend/scripts/reclassify_jobs.py --dry-run` and inspect category distribution output | Visual inspection of console table formatting |
