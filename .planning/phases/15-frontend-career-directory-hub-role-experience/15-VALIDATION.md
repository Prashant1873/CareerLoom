---
phase: 15
slug: frontend-career-directory-hub-role-experience
status: approved
nyquist_compliant: true
wave_0_complete: true
created: 2026-10-08
---

# Phase 15 — Validation Strategy: Frontend Career Directory Hub & Role Experience

> Per-phase validation contract for continuous feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|---|---|
| **Framework** | TypeScript Compiler (`tsc -b`), Vite, Oxlint (`oxlint`), Pytest |
| **Config file** | `frontend/tsconfig.json`, `frontend/.oxlintrc.json` |
| **Quick run command** | `npm --prefix frontend run build` |
| **Full suite command** | `npm --prefix frontend run build && npm --prefix frontend run lint && pytest tests/test_targets_db.py -q` |
| **Estimated runtime** | ~3 seconds |

---

## Sampling Rate

- **After every task commit:** Run `npm --prefix frontend run build`
- **After every plan wave:** Run `npm --prefix frontend run build && npm --prefix frontend run lint`
- **Before `/gsd-verify-work`:** Full build and lint suites must be green with zero TypeScript errors
- **Max feedback latency:** 4 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---|---|---|---|---|---|---|---|---|---|
| 15-01-01 | 01 | 1 | V5-UI-01 | — | Type-safe CareerTarget, CareerTargetStats, BatchSyncStatus models and API service | typecheck | `npm --prefix frontend run build` | ✅ Yes | ⬜ pending |
| 15-01-02 | 01 | 1 | V5-UI-01 | T-15-01 | CareerDirectoryModal renders Obsidian grid, 8 shimmer skeletons, empty state, safe rel noopener links | integration | `npm --prefix frontend run build && npm --prefix frontend run lint` | ✅ Yes | ⬜ pending |
| 15-02-01 | 02 | 2 | V5-UI-02, V5-UI-03 | — | NavRail renders Career Directory CTA, 1-click PM/Strategy buttons, live sync freshness footer | unit/component | `npm --prefix frontend run build` | ✅ Yes | ⬜ pending |
| 15-02-02 | 02 | 2 | V5-UI-02 | — | MasterJobStream header renders sticky quick-filter ribbon with 1-click PM & Strategy pills | unit/component | `npm --prefix frontend run build` | ✅ Yes | ⬜ pending |
| 15-02-03 | 02 | 2 | V5-UI-01, V5-UI-02, V5-UI-03 | T-15-03 | App.tsx mounts CareerDirectoryModal, coordinates cluster filters and sync freshness polling | integration | `npm --prefix frontend run build && npm --prefix frontend run lint` | ✅ Yes | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|---|---|---|---|
| Modal Visual Craft & Backdrop Blur | V5-UI-01 | Visual styling and CSS animation validation | Open CareerDirectoryModal in browser; verify dark backdrop blur, card borders, and shimmer animations match 15-UI-SPEC |
| 1-Click Track Filter Interactivity | V5-UI-02 | Live UI interaction flow | Click `🇮🇳 PM` and `🇮🇳 Strategy` in NavRail and MasterJobStream; verify stream filters instantaneously (<50ms) |
| External Portal Launch Security | V5-UI-01 | External link navigation | Click "Launch Career Portal" on any company card; verify opens external URL in new tab safely |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify commands
- [x] Sampling continuity: no tasks without automated verify
- [x] Zero watch-mode flags
- [x] Feedback latency < 4s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-10-08
