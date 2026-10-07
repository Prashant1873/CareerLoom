---
phase: 15
slug: frontend-career-directory-hub-role-experience
status: approved
shadcn_initialized: false
preset: none
created: 2026-10-08
reviewed_at: 2026-10-08T05:05:00Z
---

# Phase 15 — UI Design Contract: Career Directory Hub & Role Experience

> Visual and interaction contract for Phase 15 (Requirements: V5-UI-01, V5-UI-02, V5-UI-03).
> Defines Obsidian Dark design tokens, component hierarchy, responsive layout, micro-interactions, and state coverage.

---

## Design System

| Property | Value |
|---|---|
| Tool | none |
| Preset | not applicable |
| Component library | none (Native React 19 JSX components) |
| Icon library | lucide-react |
| Font | Plus Jakarta Sans (sans-serif), JetBrains Mono (monospace) |

---

## Spacing Scale

Declared values (must be multiples of 4):

| Token | Value | Usage |
|---|---|---|
| xs | 4px | Icon gaps, inline badge padding, dot margins |
| sm | 8px | Compact element spacing, chip gaps, button inner padding |
| md | 16px | Card padding, standard element spacing, form field gaps |
| lg | 24px | Section padding, modal content padding |
| xl | 32px | Layout gaps, modal header/footer spacing |
| 2xl | 48px | Major section breaks, container bounds |
| 3xl | 64px | Page-level spacing and margins |

Exceptions: none

---

## Typography

Constrained type scale with exactly 4 sizes and 2 weights:

| Role | Size | Weight | Line Height |
|---|---|---|---|
| Body | 14px | 400 | 1.5 |
| Label | 12px | 600 | 1.4 |
| Heading | 18px | 600 | 1.2 |
| Display | 24px | 600 | 1.2 |

- **Primary font family:** `'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`
- **Monospace font family:** `'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace` (used for opening counts, sync timestamps, ATS tags)

---

## Color

60/30/10 split explicitly declared:

| Role | Value | Usage |
|---|---|---|
| Dominant (60%) | #0b0d11 | Obsidian Charcoal base background, canvas, and modal backdrop |
| Secondary (30%) | #131720 | Surface cards, directory grid items, sidebar rails, input backgrounds |
| Accent (10%) | #10b981 | Primary CTAs, active ribbon selection, live pulse indicators |
| Destructive | #f43f5e | Destructive filter resets and critical error alerts |

Accent reserved for:
- Primary CTA button background ("Launch Career Portal", "Trigger Background Sync")
- Active quick-filter ribbon pill border and glow (`🇮🇳 PM`, `🇮🇳 Strategy`)
- Live sync status pulse dot (`.pulse-dot`) and active tab indicator
- Focus ring on interactive keyboard targets (`:focus-visible`)

### Supporting Semantic Accents (Read-only badges & tags)
- **Cyan (`#06b6d4`, subtle `rgba(6,182,212,0.12)`):** Product Management track pill, Ashby ATS tag
- **Indigo (`#6366f1`, subtle `rgba(99,102,241,0.12)`):** Strategy & Consulting track pill, Greenhouse ATS tag
- **Amber (`#f59e0b`, subtle `rgba(245,158,11,0.12)`):** Conglomerates tier badge, Lever ATS tag, in-flight sync pulse
- **Emerald (`#10b981`, subtle `rgba(16,185,129,0.12)`):** Unicorns tier badge, active live feed indicator

---

## Visual Hierarchy & Focal Points

- **Primary Focal Point:** Central Directory Grid with interactive employer cards and top search omnibox.
- **Hierarchy:**
  1. Top Directory Omnibox & Filter Bar (highest elevation, interactive search focus)
  2. Tier & Domain filter pills (horizontal selector ribbon)
  3. Company Cards Grid with ATS badges and live job counts (primary content)
  4. Direct Apply / External Career Portal link (high-contrast action anchor)
- **Accessibility & Contrast:** All text meets WCAG 2.2 AA contrast ratio (minimum 4.5:1 against respective surfaces). All icon-only actions provide explicit `aria-label` and `title` attributes.

---

## Copywriting Contract

| Element | Copy |
|---|---|
| Primary CTA | Launch Career Portal |
| Secondary CTA | Trigger Background Sync |
| Empty state heading | No Employers Found Matching Filter Criteria |
| Empty state body | Adjust your search terms, clear active role tier filters, or switch to All Employers to view the complete catalog. |
| Error state | Failed to load career targets from local database. Check backend connection or refresh the page. |
| Destructive confirmation | Reset Directory Filters: Clear active role tier, domain, and keyword search inputs to restore default directory view. |

---

## UI Considerations

> Populated by the ui-phase UI-consideration probe (Step 9.5).
> Shape-rooted UI state coverage (empty / loading / error / populated / partial / overflow / zero-one-many / long-text).

Applicable state considerations resolved: 16 covered, 0 backstop, 0 unresolved

| Category | Element(s) | Status | Resolution / Reason |
|---|---|---|---|
| empty | Career Directory Modal (E1) | ✅ covered | Zero-matching employer queries render empty card with designated copywriting and Reset Directory Filters button. |
| loading | Career Directory Modal (E1) | ✅ covered | Displays 8 pulse-shimmer skeleton cards matching grid geometry while targets fetch. |
| error | Career Directory Modal (E1) | ✅ covered | Displays error banner with retry affordance and troubleshooting message on target API failure. |
| populated | Career Directory Modal (E1) | ✅ covered | Renders 3-column responsive Obsidian grid of employer cards with tier, ATS badge, job counts, and external links. |
| partial | Career Directory Modal (E1) | ✅ covered | Targets with missing feed_url or zero listings render inactive feed badge without breaking grid layout. |
| overflow | Career Directory Modal (E1) | ✅ covered | Modal body scrolls vertically with custom styled scrollbars; company titles clip with text-overflow ellipsis. |
| zero-one-many | Career Directory Modal (E1) | ✅ covered | Header stat bar dynamically displays singular/plural employer count: 0 Employers, 1 Employer, N Employers. |
| long-text | Career Directory Modal (E1) | ✅ covered | Long employer names and URLs truncate with text-overflow ellipsis and title hover tooltips. |
| loading | Role Track Quick-Filter Ribbons (E2) | ✅ covered | Active toggle persists immediately while central stream enters loading skeleton state. |
| error | Role Track Quick-Filter Ribbons (E2) | ✅ covered | Stream error shows retry affordance without clearing active quick-filter selection. |
| overflow | Role Track Quick-Filter Ribbons (E2) | ✅ covered | Stream header pills wrap with 8px flex gap; nav rail buttons maintain 36px fixed vertical rhythm. |
| long-text | Role Track Quick-Filter Ribbons (E2) | ✅ covered | Quick-filter labels use compact emoji tags with descriptive accessible tooltips and title attributes. |
| loading | Real-Time Sync Freshness Indicator (E3) | ✅ covered | Pulse dot switches to amber and text shows Syncing In Progress when batch runner is active. |
| error | Real-Time Sync Freshness Indicator (E3) | ✅ covered | Sync failure switches indicator dot to rose with tooltip stating last error timestamp. |
| overflow | Real-Time Sync Freshness Indicator (E3) | ✅ covered | Header pill uses nowrap and collapses auxiliary text on mobile breakpoints below 768px. |
| long-text | Real-Time Sync Freshness Indicator (E3) | ✅ covered | Last synced time formats as concise relative string (e.g., Just now, 5m ago, 2h ago). |

---

## Registry Safety

| Registry | Blocks Used | Safety Gate |
|---|---|---|
| shadcn official | none | not required |

---

## Checker Sign-Off

- [x] Dimension 1 Copywriting: PASS
- [x] Dimension 2 Visuals: PASS
- [x] Dimension 3 Color: PASS
- [x] Dimension 4 Typography: PASS
- [x] Dimension 5 Spacing: PASS
- [x] Dimension 6 Registry Safety: PASS

**Approval:** approved 2026-10-08
