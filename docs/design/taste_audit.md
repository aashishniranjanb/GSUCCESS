# GPAT Learning OS — Taste Design Audit

**Date:** 2026-10-19
**Auditor:** Frontend Architect (automated + manual code review)
**Scope:** `web/src/` — all 7 route pages, 5 UI primitives, app shell, root layout, `globals.css`
**Audit protocol:** [minimalist-ui](../../.agents/skills/minimalist-ui/SKILL.md) + [redesign-existing-projects](../../.agents/skills/redesign-existing-projects/SKILL.md)

---

## Executive summary

The Phase 1 foundation is structurally sound: semantic HTML, accessible focus rings, `prefers-reduced-motion`, skip-to-content link, proper ARIA roles, and a clean component-primitive architecture. However, the visual design carries **14 major generic-AI fingerprints** that prevent the interface from looking like a premium learning product.

The most damaging issues are:
1. **All data is fabricated** — hardcoded fake statistics presented as real learner state
2. **Cyan/purple AI-gradient aesthetic** — the most common AI design cliché
3. **Lucide icons everywhere** — explicitly banned by the minimalist-ui skill
4. **Three-identical-card layouts** on nearly every page
5. **Decorative glow effects** masking absence of real content

---

## Finding severity

| Severity | Count | Description |
|----------|-------|-------------|
| Critical | 3 | Fake data as real state, gradient glow decoration, Lucide icons |
| High | 5 | Color over-saturation, uniform card grids, missing hover/active, no loading states, hardcoded pixel colors |
| Medium | 4 | Typography lacks weight contrast, missing noise/texture, `animate-pulse` without reduced-motion gate, no staggered entry |
| Low | 2 | Badge pill shapes on containers, sidebar footer status fiction |

---

## Detailed findings

### 1. Typography

| Issue | Location | Fix priority |
|-------|----------|-------------|
| Only Regular (400) and Bold (700) weights used | All pages | High |
| No negative letter-spacing on large headings | `h1` elements across routes | Medium |
| Missing `font-variant-numeric: tabular-nums` on data displays | Progress page stats, Today page counters | Medium |
| All-caps labels used with Lucide icons as decoration | Hero mission card, sidebar footer | Low |
| Body text `text-xs` / `text-[11px]` too small on mobile 393px viewport | All secondary text | Medium |
| **Plus Jakarta Sans is acceptable** (not Inter/Roboto/Open Sans) | `layout.tsx` | — pass |
| **JetBrains Mono for numeric/technical** | `layout.tsx` | — pass |

### 2. Color and surfaces

| Issue | Location | Severity |
|-------|----------|----------|
| **Cyan + purple dual accent** — classic AI-gradient fingerprint | `globals.css`, all pages | Critical |
| `bg-gradient-to-br` on hero cards | `today/page.tsx:50`, `review/page.tsx:24` | Critical |
| Decorative `blur-3xl` glow circle | `today/page.tsx:51` | Critical |
| `shadow-lg shadow-[#22D3EE]/5` colored shadow on hero | `today/page.tsx:50` | High |
| **5 accent colors** (`#22D3EE`, `#A78BFA`, `#A3E635`, `#FBBF24`, `#FB7185`) — should be 1 primary + semantic status | All primitives | High |
| Over-saturated primary `#22D3EE` (100% saturation cyan) | Everywhere | High |
| No noise/grain texture on any surface | All backgrounds | Medium |
| `#0B1020` is acceptably off-black (not pure `#000`) | `globals.css` | — pass |
| Gray family is consistently cool-tinted | Token layer | — pass |

### 3. Layout

| Issue | Location | Severity |
|-------|----------|----------|
| **Three-equal-card columns** on Progress page | `progress/page.tsx:23` — `grid-cols-3` | High |
| **Two-equal-card columns** repeated on Study, Mocks, Today | Every route | High |
| **Four-equal-card columns** on PYQs page | `pyqs/page.tsx:35` | Medium |
| No max-width constraints on card groups (only main has `max-w-5xl`) | Card grids stretch full | Medium |
| Missing whitespace between sections | `space-y-6` is adequate for density, but no breathing room between major zones | Medium |
| `h-16` mobile bottom nav overlaps content on short viewports | `app-shell.tsx:147` | Medium |
| Desktop sidebar `w-64` fixed — no opt-in icon-rail collapse | `app-shell.tsx:52` | Low |

### 4. Interactivity and states

| Issue | Location | Severity |
|-------|----------|----------|
| **No `active:scale(0.98)` or `translateY(1px)` on buttons** | `button.tsx` has `active:bg-*` but no physical press feedback | High |
| **No loading/skeleton states** | No page fetches data, so no loading UI exists | High |
| **No empty states for pages with no data** | Review, Progress — what if queue is empty? | High |
| `hover:border-[#22D3EE]/50` is the only card hover — no shadow shift or lift | Study, Mocks, PYQs cards | Medium |
| `animate-pulse` on mission dot not gated behind `prefers-reduced-motion: no-preference` | `today/page.tsx:56` | Medium |
| No `scroll-behavior: smooth` set | `globals.css` | Low |
| Focus ring present and correct | All interactive elements | — pass |

### 5. Content integrity

| Issue | Location | Severity |
|-------|----------|----------|
| **All statistics are hardcoded fakes** presented as live data | Every page | Critical |
| "3-Day Streak" — fabricated | `today/page.tsx:38` | Critical |
| "8 / 32 Completed (25%)" — fabricated | `today/page.tsx:75` | Critical |
| "78.4% Accuracy" — fabricated | `progress/page.tsx:27` | Critical |
| "42% Acc", "58% Acc" — fabricated | `today/page.tsx:201,216` | Critical |
| Fake FSRS card names with fake stability values | `today/page.tsx:153-156,166-170` | Critical |
| "FastAPI Online" / "FSRS Engine Connected" — fictional system status | `app-shell.tsx:111,117` | High |
| "Sunday, 19 October 2026" — hardcoded date that will immediately be wrong | `today/page.tsx:31` | High |

### 6. Iconography

| Issue | Location | Severity |
|-------|----------|----------|
| **Lucide icons used exclusively** — 14 distinct icons across codebase | All files | Critical |
| `Sparkles` for logo — generic AI cliché | `app-shell.tsx:58,128` | High |
| `Flame` for streak — cliché gamification metaphor | `today/page.tsx:37` | Medium |

### 7. Component patterns

| Issue | Location | Severity |
|-------|----------|----------|
| **Generic card look: border + background + shadow** on every Card | `card.tsx:12` | Medium |
| Badge `rounded-full` pill shape on all badges | `badge.tsx:6` | Low |
| Progress bar `rounded-full` with border | `progress.tsx:33` | Low |
| Every page header is identical pattern (h1 + Badge right-aligned) | All 7 routes | Medium |

### 8. Code quality

| Issue | Location | Severity |
|-------|----------|----------|
| Hardcoded hex colors instead of CSS custom properties in JSX | All files (50+ instances of `text-[#...]`, `bg-[#...]`) | High |
| No semantic HTML `<section>` usage — everything is `<div>` | All pages | Medium |
| Missing `<title>` per-page (only root metadata exists) | Route pages | Medium |
| No `og:image` or social meta | `layout.tsx` | Low |

---

## What passes the audit

- Plus Jakarta Sans + JetBrains Mono font pairing
- Dark color scheme with off-black background
- Consistent cool gray tinting
- Skip-to-content link
- `prefers-reduced-motion: reduce` global rule
- Focus-visible outline styling
- Mobile + desktop responsive shell
- Component composition via CVA variants
- Proper `aria-current` on navigation
- `role="progressbar"` with `aria-valuenow`
- No `window.alert()` or `console.log` in UI code

---

## Recommended fix priority

Following the redesign skill's priority order:

1. **Color palette cleanup** — single primary accent (desaturated cyan), remove purple co-primary, reduce to 1 accent + 3 semantic status colors
2. **Remove gradients and glow effects** — strip `bg-gradient-to-br`, `blur-3xl` circles, `shadow-lg`
3. **Mark all fake data clearly** — replace hardcoded stats with placeholder-labeled states or remove until API integration
4. **Hover and active states** — add `active:scale-[0.98]` on buttons, card hover lift with tinted shadow
5. **Layout and spacing** — break symmetric card grids, add asymmetry, increase section spacing
6. **Replace Lucide** — switch to Phosphor Icons (Bold weight) for differentiation
7. **Add loading, empty, and error states** — skeleton loaders, composed empty views
8. **Typography refinement** — weight contrast (500, 600), negative tracking on headings, tabular nums
9. **Add subtle noise texture** — CSS noise overlay on background surfaces
10. **Staggered entry animation** — gate behind `prefers-reduced-motion: no-preference`

---

## Safety blockers

**None.** No database access, no API integration, no learner data exposure. All changes are purely visual. Implementation can proceed.
