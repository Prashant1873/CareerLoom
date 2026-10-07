# Plan 15-01 Summary: Career Targets API Client & Career Directory Modal

**Phase:** 15 - Frontend Career Directory Hub & Role Experience  
**Plan:** 01  
**Wave:** 1  
**Status:** Completed  
**Requirements Delivered:** V5-UI-01  

---

## What was built

1. **TypeScript Target Schema Contracts (`frontend/src/types/job.ts`):**
   - Exported `CareerTarget` representing monitored employer career portals and metadata.
   - Exported `CareerTargetStats` covering total targets, active targets, live jobs, and tier breakdown.
   - Exported `BatchSyncStatus` representing real-time execution metrics of the batch scraping engine.
   - Exported `TargetFilterParams` supporting faceted filtering by tier, domain, role tag, and keyword search.

2. **Frontend API Services (`frontend/src/services/api.ts`):**
   - Added `fetchTargets(params)` connecting to `GET /api/targets`.
   - Added `fetchTargetStats()` connecting to `GET /api/targets/stats`.
   - Added `fetchSyncStatus()` connecting to `GET /api/targets/sync/status`.
   - Added `triggerBatchSync(params)` posting to `POST /api/targets/sync` for on-demand background sync.

3. **Obsidian Career Directory Modal (`frontend/src/components/CareerDirectoryModal.tsx`, `CareerDirectoryModal.css`):**
   - Obsidian dark overlay conforming strictly to `15-UI-SPEC.md` (`#0b0d11` base, `#131720` surfaces, `#10b981` accents).
   - Omnibox search filtering 230+ monitored employers with live clear CTA.
   - 1-click tier selector pills: `All Employers`, `🦄 Unicorns`, `🚀 Startups`, `🏢 Conglomerates`, and `💼 Consulting`.
   - Domain selector dropdown across Tech, Fintech, Quantitative Finance, Consulting, and Healthcare.
   - Metrics bar displaying total monitored companies, active live feeds, and indexed openings.
   - "Trigger Background Sync" button with spin animation during in-flight runs.
   - 8-card shimmer loading skeleton state (`.skeleton`) during data fetching.
   - Designated empty state with exact copywriting and "Reset Directory Filters" button.
   - Error banner with retry affordance on API failure.
   - 3-column responsive cards grid displaying company monogram, tier tag, domain chip, ATS badge (Greenhouse, Lever, Ashby, Workday), and secure "Launch Career Portal" CTA (`target="_blank" rel="noopener noreferrer"`).

---

## Verification
- `npm --prefix frontend run build`: TypeScript compiler and Vite bundling succeeded in 668ms with 0 errors.
- `npm --prefix frontend run lint`: Oxlint completed with 0 errors across all 22 files.
