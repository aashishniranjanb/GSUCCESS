# GPAT Learning OS — Phase 5A: Daily Home Screen Specification

**Document Version:** 1.0.0  
**Date:** 2026-10-19  
**Status:** Canonical Implementation Specification  
**Route:** `/today`  
**Application:** Next.js App Router (`web/src/app/today/`)

---

## 1. Executive Concept & Information Architecture

The Daily Home screen transforms the raw practice engine into a focused, interactive **study-planning instrument**. It is engineered to eliminate decision fatigue by answering four questions within 5 seconds of load:

1. **What should I study today?** (Headline calibrated from real active retention and recall gaps)
2. **Which of these two topics should I start with?** (Option A vs. Option B recommendation cards based on FSRS due status, misconceptions, and high-yield GPAT syllabus weightage)
3. **How much time remains until GPAT?** (Timezone-safe countdown with user-configurable target exam date; no synthetic official dates)
4. **What have I studied today, and what do I plan to study next?** (Evidence-grounded history of completed tasks alongside a resilient local study queue with duration tracking)

---

## 2. Component Hierarchy & Wireframe

```
AppShell (/today)
├── HomeHeader
│   ├── Greeting ("Good morning" / "Good afternoon" / "Good evening")
│   ├── Study Context ("Calibrated for GPAT 2027 curriculum benchmarks")
│   └── Profile/Settings Link & Offline Badge
│
├── Top Metric Cards (Grid: 1 col on mobile, 3 cols on desktop)
│   ├── ExamCountdownCard
│   │   ├── Days Remaining Counter (JetBrains Mono tabular numerals)
│   │   ├── Target Date Configuration Modal/Popover
│   │   └── Unconfigured State Handling (Honest prompt to configure)
│   ├── FSRSReviewQuickCard
│   │   ├── Due Card Count (Live from GET /api/study/review-queue)
│   │   ├── Direct "Start Due Review" Action (Links to /review)
│   │   └── Zero Due State (Clear positive reinforcement)
│   └── TodayStudiedSummaryCard
│       ├── Completed Today Tasks Counter
│       └── Accuracy Breakdown from persisted events
│
├── RecommendedStudySection
│   ├── Section Header ("Choose today's focus • 12-minute mission")
│   └── Two Choice Cards (Option A vs Option B)
│       ├── Subject & Unit Tag with Subject Color Badge
│       ├── Topic Title & Estimated Duration
│       ├── Evidence Reason ("Why this is recommended")
│       └── "Start Mission" CTA & "Inspect Syllabus" Link
│
├── PlanningAndHistorySection (2 Columns on Desktop)
│   ├── Left Column: PlannedStudyQueue
│   │   ├── Active Study Plan Checklist
│   │   ├── Add Topic from Syllabus Action
│   │   ├── Duration & Completion Status
│   │   └── Safe Local Persistence indicator
│   └── Right Column: StudiedTodayLog
│       ├── Chronological Events Logged Today
│       ├── Verification Badge (Answered vs Completed)
│       └── Accuracy & Time Spent per Item
│
├── SubjectExplorerPreview
│   ├── 5-Domain Subject Grid (Pharmacology, Pharmaceutics, Chem, Pharmacognosy, Other)
│   ├── Monochromatic Color Palette & Icons
│   └── Direct Link to /study Explorer
│
└── ActiveLearningModal / In-Page Runner (Preserved from Phase 2)
    └── QuestionCard Loop (Exit to overview, attempt submission, instant feedback)
```

---

## 3. Subject & Unit Color Token System

The color token system assigns one consistent base hue per GPAT examination domain, utilizing monochromatic tint scales for units, chapters, and badges. Contrast ratios strictly exceed WCAG AAA/AA requirements on `#0C0E14` (base) and `#13161E` (surface):

| Exam Subject Domain | Domain ID / Key | Primary Hue | Tint / Background | Border Token | Phosphor Icon |
|---|---|---|---|---|---|
| **Pharmacology** | `pharmacology` | Forest Green (`#4ADE80` / `#22C55E`) | `rgba(74, 222, 128, 0.08)` | `rgba(74, 222, 128, 0.25)` | `Pill` |
| **Pharmaceutics** | `pharmaceutics` | Sky Blue (`#60A5FA` / `#3B82F6`) | `rgba(96, 165, 250, 0.08)` | `rgba(96, 165, 250, 0.25)` | `Flask` |
| **Pharmaceutical Chemistry** | `pharmaceutical_chemistry` | Amber / Gold (`#FBBF24` / `#F59E0B`) | `rgba(251, 191, 36, 0.08)` | `rgba(251, 191, 36, 0.25)` | `Atom` |
| **Pharmacognosy** | `pharmacognosy` | Violet / Purple (`#C084FC` / `#A855F7`) | `rgba(192, 132, 252, 0.08)` | `rgba(192, 132, 252, 0.25)` | `Plant` |
| **Other B.Pharm Subjects (Biotech, Jurisprudence, Microbiology)** | `other_subjects` | Teal / Cyan (`#2DD4BF` / `#14B8A6`) | `rgba(45, 212, 191, 0.08)` | `rgba(45, 212, 191, 0.25)` | `Dna` |

*Accessibility Rule:* Color is strictly a secondary cue. Every domain display includes its human-readable title and distinct iconography.

---

## 4. Data Contracts & State Management

### 4.1 Exam Countdown
- **Source:** `LearnerLocalPreferences.targetExamDate` stored via `lib/preferences.ts`.
- **Calculation:** `Math.ceil((targetDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24))`.
- **Validation:** Handles null (unconfigured), past dates ("Exam date passed"), and invalid date strings gracefully. Timezone offset differences are neutralized by using UTC midnight normalization.

### 4.2 Two Recommended Study Choices
- **Authoritative Provider:** `GET /api/study/today?student_id={id}&minutes={min}&mode={mode}`.
- **Option A (Primary Active Focus):** The primary sequence generated by `LearnerEngine` (incorporating scheduled due reviews and active misconception repair).
- **Option B (Alternate Curriculum Track):** Drawn from the highest-priority unassessed topic from the syllabus tree or complementary curriculum subject (e.g. Pharmaceutics formulations when Option A is Pharmacology receptors).
- **Start Interaction:** Clicking "Start Option A" or "Start Option B" initiates the verified interactive `QuestionCard` mission loop.

### 4.3 Studied Today vs Plan to Study
- **State Separation Rule:** An item is only marked as "Studied Today" if an authoritative `QUESTION_ANSWERED` or `OFFLINE_SYNC_ANSWERED` learning event exists for today's date. Opening a topic or planning a topic does not alter study history.
- **Plan to Study:** Stored in durable local storage (`gpat_study_plan_{student_id}`) with clear labeling that it is a personal learner draft. Users can add topics directly from the syllabus explorer preview.

---

## 5. Responsive Layout Specifications

- **Mobile (Redmi Note 11 — 393 × 851px):**
  - Single-column flow with full-width cards.
  - Minimum touch targets of 44 × 44 CSS px for all buttons, inputs, and toggles.
  - Option A and Option B stacked vertically with prominent thumb-accessible CTAs.
  - Bottom navigation bar preserved with active indicator on "Today".
- **Desktop (Dell Latitude 5430 — 1366 × 768px):**
  - Multi-column bento grid. Top metrics in a 3-column row.
  - Recommended Study Choices presented side-by-side as two balanced columns.
  - Study Plan and Studied Today presented side-by-side.
