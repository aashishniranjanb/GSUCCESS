# GPAT Learning OS — Frontend Design System & Architecture Guide

**Date:** 2026-10-18  
**Scope:** Design Tokens, Typography, Layout Engine, Accessibility Standards, and Component Primitives  
**Project:** `C:\Users\Home\Downloads\PROJECTS\SRE_APP\web`

---

## 1. Design Token Architecture (Tailwind CSS v4)

The application shell and components strictly employ semantic dark tokens engineered for low eye strain, high contrast (WCAG 2.1 AA/AAA compliant), and long study sessions.

### Semantic Dark Palette:
- **Base Background:** `#0B1020` (OLED / Deep Navy)
- **Base Surface:** `#111A2E` (Panel cards, headers, containers)
- **Raised Surface:** `#17233B` (Elevated cards, active items, hover states)
- **Subtle Border:** `#293650` (Separators, card outlines, table borders)
- **Primary Text:** `#F4F7FB` (High contrast, crisp typography)
- **Secondary Text:** `#A9B6CA` (Meta descriptions, timestamps, subheaders)
- **Primary Action (Cyan):** `#22D3EE` (Interactive buttons, focus rings, progress)
- **Secondary Accent (Purple):** `#A78BFA` (FSRS spaced repetition, badges)
- **Status Success (Lime):** `#A3E635` (Official answer keys, completed cards)
- **Status Warning (Amber):** `#FBBF24` (Review due, streak counters, cautions)
- **Status Error (Rose):** `#FB7185` (Missed reviews, error banners, misconceptions)

---

## 2. Typography Rules

- **Interface & Content:** `Plus Jakarta Sans` via `next/font/google` (`--font-jakarta`).
- **Numbers, Metrics & Timers:** `JetBrains Mono` via `next/font/google` (`--font-jetbrains`).
- Numeric metrics (e.g. countdown timers, scores, stability scores, question counters) always render in JetBrains Mono with tabular numbers (`font-mono`) to prevent layout shifts.

---

## 3. Responsive Shell Architecture

The shell is optimized for the two target reference devices:
1. **Redmi Note 11 (Mobile Phone — 393px × 873px):**
   - Top lightweight bar displaying application branding and backend connection badge.
   - Sticky mobile bottom navigation bar (`h-16`) supporting thumb reachability for the primary tabs: Today, Study, PYQs, Review, and Progress.
   - Bottom padding (`pb-24`) on the main container ensuring content is never obscured by the mobile navigation bar.
2. **Dell Latitude 5430 (Laptop — 1366px to 1920px):**
   - Fixed desktop left sidebar (`w-64`) with persistent navigation, section badges, and real-time backend/engine telemetry.
   - Main content viewport centered with a maximum width (`max-w-5xl`) for optimal reading line length.

---

## 4. Accessibility & Motor Safety

- **Skip Navigation:** A visible skip-link (`#main-content`) is available on `Tab` focus.
- **Focus Rings:** High-visibility cyan focus outlines (`outline: 2px solid #22D3EE; outline-offset: 2px`) for keyboard accessibility.
- **Reduced Motion Support:** `@media (prefers-reduced-motion: reduce)` automatically sets animation and transition durations to `0.01ms` across all components.
- **Color Independence:** Badges and alerts always combine distinct icons and descriptive text alongside semantic colors (never communicating state by color alone).
