# Phase 15: Frontend Career Directory Hub & Role Experience — Technical Research

**Phase:** 15  
**Slug:** frontend-career-directory-hub-role-experience  
**Requirements Covered:** V5-UI-01, V5-UI-02, V5-UI-03  
**Design Contract:** [15-UI-SPEC.md](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/.planning/phases/15-frontend-career-directory-hub-role-experience/15-UI-SPEC.md)

---

## User Constraints & Locked Contracts

### 1. Requirements Traceability
- **V5-UI-01:** Obsidian dark Career Directory Hub view/modal displaying all indexed companies, verified career links, ATS badges, and live opening counts.
- **V5-UI-02:** Dedicated Product Management (`🇮🇳 PM`) and Strategy Consulting (`🇮🇳 Strategy`) 1-click quick-filters in the navigation rail and stream header.
- **V5-UI-03:** Real-time sync freshness indicators in the UI showing last sync timestamp and monitored company count.

### 2. Design System & UI Contract (from 15-UI-SPEC.md)
- **Palette (Obsidian Dark 60/30/10):**
  - Dominant (60%): `#0b0d11` (base canvas, modal overlay backdrop)
  - Secondary (30%): `#131720` / `#1a202c` (cards, inputs, table containers, elevated bars)
  - Accent (10%): `#10b981` (primary CTA background, active filter pill border/glow, live pulse dot)
  - Destructive: `#f43f5e` (reset filter actions)
- **Typography:**
  - Font families: `Plus Jakarta Sans` for UI, `JetBrains Mono` for badges, counts, timestamps.
  - Scale: 4 sizes only (`12px`, `14px`, `18px`, `24px`), 2 weights only (`400`, `600`).
- **Spacing Scale:**
  - Multiples of 4 only: `4px` (xs), `8px` (sm), `16px` (md), `24px` (lg), `32px` (xl), `48px` (2xl), `64px` (3xl).
- **Copywriting Contract:**
  - Primary CTA: `Launch Career Portal`
  - Secondary CTA: `Trigger Background Sync`
  - Empty state heading: `No Employers Found Matching Filter Criteria`
  - Empty state body: `Adjust your search terms, clear active role tier filters, or switch to All Employers to view the complete catalog.`
  - Error state: `Failed to load career targets from local database. Check backend connection or refresh the page.`
  - Destructive confirmation: `Reset Directory Filters: Clear active role tier, domain, and keyword search inputs to restore default directory view.`

---

## Standard Stack & Integration Surface

### 1. Dependencies & Libraries
| Component | Technology | Version | Purpose |
|---|---|---|---|
| UI Framework | React | 19.x | Component rendering and modal state |
| Language | TypeScript | 5.7+ | Strict contract typing with backend Pydantic models |
| Styling | Vanilla CSS | Custom tokens | Zero external CSS runtime; follows `index.css` design system |
| Iconography | Lucide React | ^1.50.0 | Icons (`Building2`, `ExternalLink`, `RefreshCw`, `SlidersHorizontal`, etc.) |

### 2. Backend API Surface
The backend endpoints implemented in Phases 11-14 provide full support for Phase 15:
- **`GET /api/targets`:**
  - Parameters: `tier` (startup, unicorn, conglomerate, consulting), `domain`, `status`, `search`, `limit`, `offset`.
  - Returns: `{ items: CareerTarget[], total: number, limit: number, offset: number }`.
- **`GET /api/targets/stats`:**
  - Returns: `{ total_targets: number, active_targets: number, by_tier: Record<string, int>, total_live_jobs: number }`.
- **`GET /api/targets/sync/status`:**
  - Returns: `{ is_running: boolean, completed: number, total: number, last_run_timestamp: string, last_error: string }`.
- **`POST /api/targets/sync`:**
  - Initiates on-demand background sync pass (202 Accepted).
- **`GET /api/jobs`:**
  - Query parameters: `category` (supports `product_cluster` and `strategy_cluster` with automatic sub-50ms title synonym expansion) and `country="India"`.

---

## Component Architecture & State Flow

### 1. `CareerDirectoryModal` (`frontend/src/components/CareerDirectoryModal.tsx`)
- **Container:** Full-viewport overlay with backdrop blur and `#0b0d11` optical elevation.
- **Top Header Bar:**
  - Title: "Career Directory Hub" with active employer count badge.
  - Quick Search input (`Search 230+ companies by name, domain, or ATS...`).
  - Close button (`aria-label="Close directory modal"`).
- **Control Bar:**
  - Tier filter pills: `All`, `Startups`, `Unicorns`, `Conglomerates`, `Consulting`.
  - Domain filter dropdown: `All Domains`, `Tech`, `Fintech`, `Quantitative Finance`, `Consulting`, `Healthcare`.
  - Sync trigger CTA: "Trigger Background Sync" button with spin animation during in-flight runs.
- **Stats Banner:**
  - 3 metric cards: "Monitored Employers", "Verified Live Feeds", "Active Openings Indexed".
- **Grid View:**
  - Responsive cards (1 col mobile, 2 col tablet, 3 col desktop).
  - Each card includes: Company monogram / logo placeholder, name, tier tag, domain pill, ATS badge (`greenhouse`, `lever`, `ashby`, `workday`, `custom`), live job count, and "Launch Career Portal" external link button.
- **States (UI Considerations Probe 16/16):**
  - Loading: 8 pulse-shimmer skeleton cards matching grid geometry (`.skeleton`).
  - Empty: Designated empty card with reset filter action.
  - Error: Retry banner with troubleshooting guide.
  - Truncation: Card boundaries clip long URLs and titles with `text-overflow: ellipsis`.

### 2. 1-Click Role Track Quick-Filter Ribbons (`V5-UI-02`)
- **Locations:**
  1. `NavRail.tsx`: Under Views section, two dedicated prominent buttons:
     - `🇮🇳 Product (PM)`: Activates `category: 'product_cluster', country: 'India'`.
     - `🇮🇳 Strategy & Consulting`: Activates `category: 'strategy_cluster', country: 'India'`.
  2. `MasterJobStream.tsx`: Sticky quick-ribbon bar below search omnibox:
     - Pill toggles with emoji icons and active emerald glow.
- **Behavior:**
  - Single click toggles track ON.
  - Second click on the active track toggles OFF (returns to all listings).
  - Sub-50ms query round-trip to `/api/jobs?category=product_cluster&country=India`.

### 3. Real-Time Sync Freshness Indicator (`V5-UI-03`)
- **Locations:**
  1. `NavRail.tsx` footer: "237 Employers • Synced 5m ago" with live pulse dot.
  2. `MasterJobStream.tsx` header / stats row: Badge displaying real-time background sync state and button to launch Career Directory Hub.
- **Service Integration:**
  - Hook / state in `App.tsx` polls `/api/targets/sync/status` and `/api/targets/stats` on mount and after manual sync triggers.

---

## Common Pitfalls & Mitigations

| Pitfall | Risk | Mitigation |
|---|---|---|
| CSS Token Inconsistency | Visual regressions, breaking dark mode | Use CSS variables from `index.css` (`--bg-base`, `--bg-surface`, `--accent-primary`, etc.); avoid raw arbitrary hex values. |
| External Link Vulnerabilities | Tabnabbing / security leaks | Always include `target="_blank" rel="noopener noreferrer"` on all external career URLs. |
| Non-Multiple-of-4 Spacing | Breaks grid alignment | Strict adherence to `4px`, `8px`, `16px`, `24px`, `32px` spacing tokens. |
| State Stuttering on Sync | Freezing UI during background sync | Non-blocking API calls; sync button shows spinning loader while background scheduler runs asynchronously (202 response). |
| Mobile Layout Overflow | Horizontal scrolling on small screens | Grid adapts from 3 columns (`minmax(300px, 1fr)`) to 1 column on `<768px`; omnibox and stats pills wrap smoothly. |

---

## Validation Strategy
- **Type Checking:** `npm run build` (`tsc -b && vite build`) in `frontend` must compile with zero TypeScript errors.
- **Linting:** `npm run lint` (`oxlint`) in `frontend` must pass cleanly.
- **Functional Check:**
  - Verify directory modal opens and loads monitored targets from `/api/targets`.
  - Verify tier pills (`Startups`, `Unicorns`, `Conglomerates`, `Consulting`) filter correctly.
  - Verify clicking `🇮🇳 PM` and `🇮🇳 Strategy` updates the job stream with sub-50ms results.
  - Verify real-time freshness indicator updates properly.
