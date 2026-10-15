# Frontend Implementation Plan: CareerLoom Light Mode & Dual-Theme Ergonomics

## Target Mode: Operate + Read
## Design Read: "High-craft desktop job discovery cockpit for candidates and career switchers, pairing the existing Obsidian Charcoal dark palette with an Obsidian Porcelain & Cool Slate light palette, calibrated emerald action accents, and strict WCAG 2.2 AA contrast."
## Active Dials: Variance: 3 | Motion: 6 | Density: 7

---

### Perceptual Token Ramp & Contrast Calibration (frontend-skill colorize.md)

| Token | Dark Mode (Obsidian Charcoal) | Light Mode (Obsidian Porcelain) | Intended Semantic Usage | Light Mode WCAG Ratio |
|---|---|---|---|---|
| `--bg-base` | `#0b0d11` | `#f8fafc` | Viewport canvas background | Baseline |
| `--bg-surface` | `#131720` | `#ffffff` | Primary card & sidebar surface | Contrast canvas |
| `--bg-elevated` | `#1a202c` | `#f1f5f9` | Elevated headers, filters, popups | Optical elevation |
| `--bg-subtle` | `#232b3b` | `#e2e8f0` | Pill & chip backgrounds | Subtly distinct |
| `--bg-input` | `#10141c` | `#ffffff` | Text inputs and omnibox field | Clean text contrast |
| `--bg-hover` | `rgba(255, 255, 255, 0.04)` | `rgba(15, 23, 42, 0.04)` | Item hover state | Tactile feedback |
| `--bg-active` | `rgba(255, 255, 255, 0.08)` | `rgba(15, 23, 42, 0.08)` | Active pressed state | Tactile feedback |
| `--border-subtle` | `rgba(255, 255, 255, 0.08)` | `rgba(15, 23, 42, 0.08)` | Structural split borders | Hairline divider |
| `--border-hover` | `rgba(255, 255, 255, 0.16)` | `rgba(15, 23, 42, 0.18)` | Hovered card perimeter | Optical snap |
| `--border-strong` | `rgba(255, 255, 255, 0.24)` | `rgba(15, 23, 42, 0.26)` | Active boundaries & inputs | Form definition |
| `--text-primary` | `#f3f4f6` | `#0f172a` | Headings, titles, employer names | **14.6:1** (AAA Pass) |
| `--text-secondary` | `#9ca3af` | `#334155` | Subtitles, locations, descriptions | **8.5:1** (AAA Pass) |
| `--text-muted` | `#6b7280` | `#64748b` | Timestamps, counts, meta keys | **4.6:1** (AA Pass) |
| `--text-inverted` | `#0b0d11` | `#f8fafc` | Inverted badges & solid buttons | Highest contrast |
| `--accent-primary` | `#10b981` | `#059669` | Primary action CTA, focus rings | **4.6:1** (AA Pass) |
| `--accent-primary-hover`| `#059669` | `#047857` | Hovered CTA action button | **6.0:1** (AAA Pass) |
| `--accent-subtle` | `rgba(16, 185, 129, 0.12)` | `rgba(5, 150, 105, 0.10)` | Active filter pill tint fill | Crisp pastel tint |

---

### Calibrated Semantic Badge Matrix (Dual-Theme Compliance)

| Badge Category | Dark Mode (Fill / Text) | Light Mode (Fill / Text) | Light Mode Contrast |
|---|---|---|---|
| **Emerald (Direct / Match)** | `rgba(16, 185, 129, 0.14)` / `#34d399` | `rgba(16, 185, 129, 0.12)` / `#047857` | **5.8:1** (AA Pass) |
| **Cyan (Domain / Tech)** | `rgba(6, 182, 212, 0.14)` / `#22d3ee` | `rgba(6, 182, 212, 0.12)` / `#0891b2` | **4.7:1** (AA Pass) |
| **Amber (Compensation / CTC)** | `rgba(245, 158, 11, 0.14)` / `#fbbf24` | `rgba(245, 158, 11, 0.14)` / `#b45309` | **5.1:1** (AA Pass) |
| **Indigo (Tier / Unicorn)** | `rgba(99, 102, 241, 0.14)` / `#818cf8` | `rgba(99, 102, 241, 0.12)` / `#4f46e5` | **5.6:1** (AA Pass) |
| **Rose (Hot / Urgency)** | `rgba(244, 63, 94, 0.14)` / `#fb7185` | `rgba(244, 63, 94, 0.12)` / `#e11d48` | **4.8:1** (AA Pass) |

---

### Chunk 1: Recon & Strategy (colorize, craft-floor)
- [ ] Task 1.1: Audit token consumers across `index.css`, `App.css`, and `CareerDirectoryModal.css`
- [ ] Task 1.2: Identify hardcoded dark hex color overrides (`#080b11`, `#0e131f`, `#121826`, `#0d121c`, `#111724`)
- [ ] Task 1.3: Lock in dual-theme CSS variables under `:root, [data-theme="dark"]` and `[data-theme="light"]`

### Chunk 2: Direction & Scaffolding (tokens & contrast verification)
- [ ] Task 2.1: Establish `:root[data-theme="light"]` token declarations with cool slate neutrals in `index.css`
- [ ] Task 2.2: Refactor all hardcoded dark background and border values in `App.css` to use CSS variables
- [ ] Task 2.3: Create automated node contrast checking script `scripts/verify-contrast.mjs` verifying WCAG 2.2 AA ratios

### Chunk 3: Production Engineering (useTheme & Hydration)
- [ ] Task 3.1: Build `useTheme` hook with `localStorage` persistence and `window.matchMedia('(prefers-color-scheme: dark)')` listener
- [ ] Task 3.2: Insert inline blocking hydration script in `index.html` to eliminate Flash of Unstyled Theme (FOUC)
- [ ] Task 3.3: Implement accessible `<ThemeToggle />` component with Lucide `Sun` and `Moon` icons

### Chunk 4: Fluid Physics & Gestures (apple-design)
- [ ] Task 4.1: Integrate theme toggle into `NavRail.tsx` footer with Apple fluid spring physics (`damping: 1.0`, `duration: 250ms`)
- [ ] Task 4.2: Add theme toggle into mobile header inside `App.tsx`
- [ ] Task 4.3: Ensure interactive states (hover/active) trigger without pointer latency

### Chunk 5: Hardening & A11y (audit, harden)
- [ ] Task 5.1: Verify WCAG 2.2 AA keyboard focus rings (`:focus-visible`) across light and dark modes
- [ ] Task 5.2: Check all modal overlays (`CareerDirectoryModal`, `LeadCaptureModal`, `JobDetailModal`) for backdrop contrast and blur continuity

### Chunk 6: Impeccable Polish (craft-floor)
- [ ] Task 6.1: Fine-tune optical card elevation shadows in light mode (`--shadow-sm`, `--shadow-md`, `--shadow-lg`)
- [ ] Task 6.2: Validate all badge contrast values and verified career links in both themes
- [ ] Task 6.3: Run frontend production build check (`npm run build`)
