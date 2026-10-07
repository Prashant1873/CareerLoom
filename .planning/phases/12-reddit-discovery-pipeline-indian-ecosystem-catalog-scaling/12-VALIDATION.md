---
phase: 12
slug: reddit-discovery-pipeline-indian-ecosystem-catalog-scaling
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-10-08
---

# Phase 12 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x |
| **Config file** | `pytest.ini` / root config |
| **Quick run command** | `pytest tests/test_reddit_discovery.py -v` |
| **Full suite command** | `pytest tests/test_reddit_discovery.py tests/test_catalog_scaling.py -v` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_reddit_discovery.py -v`
- **After every plan wave:** Run `pytest tests/test_reddit_discovery.py tests/test_catalog_scaling.py -v`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 12-01-01 | 01 | 1 | DISCOVERY-01 | — | N/A | unit | `pytest tests/test_reddit_discovery.py -k test_discovery_cache -v` | ❌ W0 | ⬜ pending |
| 12-01-02 | 01 | 1 | DISCOVERY-01 | — | N/A | integration | `pytest tests/test_reddit_discovery.py -k test_reddit_scanner -v` | ❌ W0 | ⬜ pending |
| 12-01-03 | 01 | 1 | DISCOVERY-02 | — | N/A | unit | `pytest tests/test_reddit_discovery.py -k test_ats_prober -v` | ❌ W0 | ⬜ pending |
| 12-01-04 | 01 | 1 | DISCOVERY-01, 02 | — | N/A | integration | `pytest tests/test_reddit_discovery.py -k test_discovery_api -v` | ❌ W0 | ⬜ pending |
| 12-02-01 | 02 | 2 | DISCOVERY-03 | — | N/A | unit | `pytest tests/test_catalog_scaling.py -k test_catalog_files -v` | ❌ W0 | ⬜ pending |
| 12-02-02 | 02 | 2 | DISCOVERY-03 | — | N/A | integration | `pytest tests/test_catalog_scaling.py -k test_seed_targets -v` | ❌ W0 | ⬜ pending |
| 12-02-03 | 02 | 2 | DISCOVERY-03 | — | N/A | e2e | `pytest tests/test_catalog_scaling.py -k test_scaled_targets_query -v` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_reddit_discovery.py` — test stubs for discovery cache, Reddit scanner, and ATS prober
- [ ] `tests/test_catalog_scaling.py` — test stubs for catalog file validation and seeder integration

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Live Reddit connection probe (optional) | DISCOVERY-01 | Network rate-limit compliance | Run `python backend/scripts/run_discovery.py --live --limit 5` and inspect logs. |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 5s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-10-08
