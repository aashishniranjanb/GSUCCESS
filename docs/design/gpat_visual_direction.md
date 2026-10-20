# GPAT Learning OS — Visual Direction

**Date:** 2026-10-19
**Basis:** [taste_audit.md](taste_audit.md), minimalist-ui protocol, redesign-existing-projects protocol
**Product context:** Dark-mode study interface for pharmacy graduates preparing GPAT 2027

---

## Design thesis

**"Scientific instrument, not gaming dashboard."**

The GPAT Learning OS should feel like a precision study tool: calm, focused, and credible. Every pixel should serve the student's concentration. No decoration, no gamification theater, no AI-gradient spectacle.

The visual language draws from three references:
- **Medical journal typography** — clean, authoritative, high information density
- **Dark IDE environments** — low-distraction surfaces with clear hierarchy through brightness, not color
- **Analog instrument panels** — monospace numerics, status indicators over decoration

---

## Color system

### Primary palette (dark mode)

| Token | Hex | Role |
|-------|-----|------|
| `--color-bg-base` | `#0C0E14` | Canvas / page background — slightly warm dark |
| `--color-surface-base` | `#13161E` | Card / panel surface |
| `--color-surface-raised` | `#1A1D27` | Elevated surface (hover, active) |
| `--color-border-subtle` | `#2A2D38` | Borders, dividers — warm gray |
| `--color-border-focus` | `#3A3D48` | Visible on hover |

### Text hierarchy

| Token | Hex | Role |
|-------|-----|------|
| `--color-text-primary` | `#EAECF0` | Primary body text — not pure white |
| `--color-text-secondary` | `#8B8FA3` | Secondary labels, metadata |
| `--color-text-tertiary` | `#5C5F72` | Disabled, placeholder, hint |

### Single primary accent

| Token | Hex | Role |
|-------|-----|------|
| `--color-accent` | `#60A5FA` | Primary interactive — desaturated sky blue |
| `--color-accent-muted` | `#60A5FA/15` | Background tint for active states |

### Semantic status (muted, not saturated)

| Token | Hex | Role |
|-------|-----|------|
| `--color-status-success` | `#86EFAC` | Completed, correct — muted green |
| `--color-status-warning` | `#FCD34D` | Due soon, needs attention — muted amber |
| `--color-status-error` | `#FCA5A5` | Incorrect, critical — muted rose |
| `--color-status-info` | `#93C5FD` | Informational — close to accent |

**Removed:** `#22D3EE` (saturated cyan), `#A78BFA` (purple co-primary), `#A3E635` (lime green), `#FBBF24` (bright amber), `#FB7185` (bright rose).

---

## Typography

### Font stack (unchanged)
- **Interface:** Plus Jakarta Sans (400, 500, 600, 700)
- **Numeric / technical:** JetBrains Mono (400, 500, 600)

### Hierarchy

| Role | Size | Weight | Tracking | Line height |
|------|------|--------|----------|-------------|
| Page heading | `text-xl` / `text-2xl` | 700 | `-0.025em` | 1.2 |
| Section heading | `text-lg` | 600 | `-0.015em` | 1.3 |
| Card title | `text-base` | 600 | `-0.01em` | 1.4 |
| Body | `text-sm` | 400 | Normal | 1.6 |
| Label / caption | `text-xs` | 500 | `0.02em` | 1.5 |
| Mono data | `text-sm` / `text-xs` | 500 | Normal | 1.4 |

### Numeric display
- All numeric values use JetBrains Mono with `font-variant-numeric: tabular-nums`
- Accuracy percentages, question counts, timer values always monospace

---

## Surfaces and depth

- **No gradients** — solid background colors only
- **No glow effects** — remove all `blur-3xl`, `shadow-lg shadow-color/opacity`
- **Borders:** `1px solid var(--color-border-subtle)` — single consistent rule
- **Card radius:** `8px` (crisp, not soft)
- **Shadows:** near-invisible (`0 1px 3px rgba(0,0,0,0.12)`) or none — shadows are tinted dark, never colored
- **Noise overlay:** subtle SVG noise at `opacity: 0.03` over `--color-bg-base` for analog texture

---

## Layout principles

- **Asymmetric grids** — no three-identical-card rows. Use 2:1 splits, single-column stacks, or varied heights
- **Generous spacing** — `space-y-8` between major sections, `gap-5` in grids
- **Content max-width** — `max-w-4xl` for text-heavy areas within the `max-w-5xl` main container
- **Mobile-first** — 393px (Redmi Note 11) as the primary design target, progressively enhanced to 1366px
- **Bottom nav height** — `h-14` with `pb-safe` for iOS safe area

---

## Component identity

### Buttons
- **Primary:** `bg-[accent]` with `text-[bg-base]`, radius `6px`, no shadow
- **Secondary:** `bg-transparent border border-[border-subtle]`, text-secondary
- **Active state:** `scale(0.98)` + `translateY(1px)` on press
- **Hover:** background shift only, no color theatrics

### Cards
- Flat surface, `border-1` only, no shadow default
- Hover: border brightens to `--color-border-focus`, no lift
- No decorative header borders — use spacing instead

### Badges
- Small, squared radius (`rounded-md`), not pill-shaped
- Background: very low opacity tint of semantic color
- Text: medium weight, slightly brighter version of semantic color

### Progress bars
- Height `3px` (thin, precise) not `8px`
- No border on track — just background color difference
- `rounded-sm` not `rounded-full`

---

## Iconography

**Replace Lucide with Phosphor Icons (Bold weight).**

Phosphor provides thicker, more distinctive strokes that read clearly at small sizes on AMOLED screens. Use consistent 20px / 16px sizing.

Key replacements:
| Current (Lucide) | New (Phosphor Bold) |
|---|---|
| `Sparkles` (logo) | Custom SVG mark or `Atom` |
| `CalendarDays` | `CalendarBlank` |
| `BookOpen` | `BookOpen` (same concept, thicker) |
| `History` | `ClockCounterClockwise` |
| `RotateCcw` | `ArrowsCounterClockwise` |
| `GraduationCap` | `Exam` |
| `TrendingUp` | `ChartLineUp` |
| `Settings` | `GearSix` |
| `Flame` | **Remove** — no gamification iconography |
| `Brain` | `Brain` (Phosphor version) |
| `AlertTriangle` | `Warning` |
| `Target` | `Crosshair` |

---

## Content policy

### During static/demo phase
- Label all non-API data as "Sample data — not connected to your study history"
- Use organic, non-round numbers when showing placeholder stats
- Never present fake streaks or achievements
- Use `EmptyState` component for features not yet connected

### After API integration
- Show `SkeletonLoader` while fetching
- Show `ErrorState` on connection failure
- Show `EmptyState` when no data exists (first-time user)
- Never show stale data without a "Last synced" timestamp

---

## Motion

- **Staggered entry:** `translateY(8px)` + `opacity: 0` → resolved over `400ms` with `cubic-bezier(0.16, 1, 0.3, 1)`
- **Delay cascade:** `animation-delay: calc(var(--index) * 60ms)`
- **Button press:** `scale(0.98)` on `:active` via `transition: transform 100ms`
- **Card hover:** border color transition `200ms`
- **Reduced motion:** all entry animations gated behind `@media (prefers-reduced-motion: no-preference)`
- **No ambient motion** — no floating blobs, no pulsing dots, no parallax

---

## Implementation order

1. Rewrite `globals.css` with new token palette
2. Update all UI primitives (`button`, `card`, `badge`, `progress`) to use CSS variables instead of hardcoded hex
3. Install `@phosphor-icons/react` — replace all Lucide imports
4. Rewrite `app-shell.tsx` — new sidebar/nav with updated tokens and Phosphor icons
5. Rewrite `today/page.tsx` — premium hero, honest content labels, asymmetric layout
6. Update remaining route pages incrementally
7. Add noise texture overlay
8. Add staggered entry animation utility
9. Verify at 360px, 768px, 1366px
10. Run lint, typecheck, build gates
