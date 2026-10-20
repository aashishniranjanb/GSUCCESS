# GPAT 2027 — Mobile-First Home UI Redesign Report

**Date:** 2026-10-19  
**Status:** Completed & Verified  
**Governing Objective:** Transform `/today` into an interactive, mobile-first learning experience inspired by the interaction clarity of Swiggy and Duolingo, maintaining a distinct pharmacy-learning identity.

---

## 1. Audit Findings & Solutions Summary

| Issue Identified in Audit | Root Cause | Solution Implemented |
| :--- | :--- | :--- |
| **Hero too tall / illustration tiny** | Fixed height ratio with excessive padding, forcing primary CTA below the fold on mobile. | Reduced hero padding (`p-4 sm:p-6`), prioritized text and CTA above the illustration on small screens, set container height to `h-36 sm:h-44 md:h-52`, and used `object-top` intentional crop keeping the student's face visible. |
| **Exam card cut off / clipped** | Insufficient bottom clearance (`pb-20`) for fixed mobile navigation bar on compact screens (360px–393px). | Expanded main viewport bottom clearance to `pb-24 md:pb-8`. Streamlined `ExamCountdownCard` padding (`p-3.5 sm:p-5`) and typography. |
| **Crowded navigation** | 6 destinations crammed into 360px viewport with small touch targets. | Streamlined mobile bar to **5 primary destinations** (Today, Study, PYQs, Review, Progress) with enlarged `>= 48px` touch targets (`h-16`, min-h 48px). Relocated **Settings** to a dedicated accessible icon in the mobile top header. |
| **Static subject discovery** | Vertical static cards consumed excessive vertical height. | Converted `SyllabusSubjectExplorerPreview` into a **horizontal swipeable rail** on mobile (`flex overflow-x-auto snap-x no-scrollbar`) that transitions to a 5-column grid on desktop. |
| **Isolated action** | Daily Mission button lacked immediate connection to session state. | Immediate feedback states: Start Daily Mission, Resume Mission (X/Y), Retake Mission, with instant active transition to interactive question mode. |

---

## 2. Interactions Implemented

1. **Compact Personalized Hero (`daily-hero-section.tsx`):**
   - Live time-aware greeting badge: *“Good morning, {firstName}”* / *“Good afternoon, {firstName}”* / *“Good evening, {firstName}”* / *“Welcome back”*.
   - Headline: *“Today, let's make [progress](#).”*
   - Supporting text: *“One focused session at a time.”*
   - Single dominant primary CTA: **“Start today's mission”** (`min-h-[48px]`, active press scaling `active:scale-[0.98]`, keyboard focus ring).
   - High-fidelity pharmacy student illustration with responsive intentional cropping.
2. **Horizontal Swipeable Subject Discovery (`syllabus-explorer-preview.tsx`):**
   - Horizontal snap rail on mobile (`snap-x snap-mandatory overflow-x-auto`).
   - Subject-specific cards with color coding (Green Pharmacology, Blue Pharmaceutics, Amber Chemistry, Violet Pharmacognosy, Teal Biotechnology).
   - Touch-manipulation optimized (`touch-manipulation`, `active:scale-[0.98]`).
3. **Exam Horizon Milestone Card (`exam-countdown-card.tsx`):**
   - Compact height, clear *“Learner Target”* badge with NBEMS unconfirmed notification.
   - Inline configuration modal (`Gear` icon trigger).
4. **Essential Review (`fsrs-review-summary-card.tsx`):**
   - Real FSRS `/api/review/queue` due counts with active decay messaging or consolidated celebration state.
   - Direct review launcher button (`min-h-[44px]`).
5. **Streamlined Mobile Bottom Navigation (`app-shell.tsx`):**
   - 5 clear destinations: Today, Study, PYQs, Review, Progress.
   - Dedicated active indicator pill and bold text hierarchy.
   - Settings easily reachable in mobile header.

---

## 3. Responsive Screenshot Verification

Captured across all target viewports via Playwright:

| Viewport | Dimensions | Screenshot Path |
| :--- | :--- | :--- |
| **Small Mobile** | 360 × 800 | `reports/screenshots/redesign_mobile_first_small_360.png` |
| **Standard Mobile** | 393 × 852 | `reports/screenshots/redesign_mobile_first_mobile_393.png` |
| **Tablet** | 768 × 1024 | `reports/screenshots/redesign_mobile_first_tablet_768.png` |
| **Desktop** | 1366 × 900 | `reports/screenshots/redesign_mobile_first_desktop_1366.png` |

---

## 4. Quality & Platform Integrity Gates

- **ESLint (`npm run lint`):** **0 errors, 0 warnings**
- **TypeScript Check (`npx tsc --noEmit`):** **0 errors** (clean exit)
- **Production Build (`npm run build`):** **11/11 routes successfully compiled and optimized**
- **Pytest Regression Suite:** **11 passed, 0 failed** in 11.43s
- **Database Safety Check:** All 3 SQLite databases returned `ok` (`gpat_knowledge.db`, `data/gpat_baseline.db`, `data/pyq_topic_staging.db`). Zero migrations or schema alterations.

---

## 5. Modified Files

1. `web/src/components/layout/app-shell.tsx` — Streamlined mobile bottom navigation to 5 destinations with >= 48px touch targets, expanded main bottom scroll clearance (`pb-24`), and added accessible Settings link in the mobile header.
2. `web/src/components/today/daily-hero-section.tsx` — Reduced vertical height, optimized mobile text & CTA stacking, and applied intentional image face cropping (`h-36 sm:h-44 md:h-52 object-top`).
3. `web/src/components/today/syllabus-explorer-preview.tsx` — Rebuilt as a horizontal swipeable discovery rail on mobile with snap-points, transitioning to grid on desktop.
4. `web/src/components/today/exam-countdown-card.tsx` — Streamlined padding, typography, and compact layout to prevent clipping on mobile.
5. `web/src/components/today/fsrs-review-summary-card.tsx` — Streamlined padding, typography, and touch target size for mobile screens.
