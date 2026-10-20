# GPAT 2027 Learning OS — Design System & Visual Specification

**Version:** 1.0.0  
**Design Philosophy:** Academic Excellence, Cognitive Calm, Zero Clutter  
**Inspiration:** Refined editorial typography, Nielsen Norman Group cognitive reduction principles, Swiss typographic clarity, and purposeful dark-mode contrast.

---

## 1. Core Principles

1. **Academic Authority, Not an Administrative Dashboard:**
   The interface feels like a precision medical/pharmaceutical instrument. Avoid neon gaming confetti or cheap gamification; celebrate demonstrated mastery through clear typographic contrast and calm evidence cards.
2. **One Primary Action per Viewport:**
   On the home screen, the Daily Mission is dominant and unmistakable. Secondary choices (such as 5-minute sessions or mock exams) are accessible but visually subordinate.
3. **No Streak Pressure or False Urgency:**
   Learning progress reflects demonstrated retention, spaced recall, and repaired misconceptions. Zero punitive counters or streak breaking.
4. **Readable & Zoomable Chemical Visuals:**
   Chemical formulas, NMR spectra, and figures are rendered in crisp, high-contrast containers with 1-click expand/zoom modals.
5. **Universal Accessibility (WCAG 2.1 AA Compliant):**
   Minimum 4.5:1 text-to-background contrast, visible focus rings on all interactive elements, keyboard operable, and full `prefers-reduced-motion` compliance.

---

## 2. Design Tokens

### 2.1 Color Palette

```css
:root {
  /* Surfaces */
  --color-bg-base: #090d16;          /* Deep void navy */
  --color-surface-1: #111827;        /* Elevated card background */
  --color-surface-2: #1e293b;        /* Secondary containers */
  --color-surface-glass: rgba(17, 24, 39, 0.85); /* Backdrop glass */
  --color-border-subtle: rgba(255, 255, 255, 0.08);
  --color-border-focus: #6366f1;

  /* Typography */
  --color-text-primary: #f8fafc;     /* 98% white for high legibility */
  --color-text-secondary: #94a3b8;   /* 60% slate for secondary descriptions */
  --color-text-muted: #64748b;       /* 40% slate for labels and timestamps */

  /* Academic Accents */
  --color-brand-primary: #6366f1;    /* Deep Indigo */
  --color-brand-gradient: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
  --color-brand-glow: rgba(99, 102, 241, 0.25);

  /* Pedagogical Feedback Semantic Tints */
  --color-semantic-success: #10b981; /* Solid mastery green */
  --color-semantic-warning: #f59e0b; /* Fragile guess amber */
  --color-semantic-danger: #f43f5e;  /* Overconfident misconception rose */
  --color-semantic-info: #38bdf8;    /* Discovery blue */
}
```

### 2.2 Typography Scale

- **Primary Typeface:** `Plus Jakarta Sans` (editorial clarity, geometric precision)
- **Monospace Code/Timer:** `JetBrains Mono` (tabular numbers, non-jumping countdowns)

| Level | Size | Weight | Line Height | Letter Spacing | Usage |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Display Header** | 28px | 800 | 1.2 | -0.03em | Daily Mission Headline, Mock Score |
| **Card Header** | 20px | 700 | 1.3 | -0.02em | Section Titles, Question Texts |
| **Body Primary** | 15px | 400 / 500 | 1.55 | 0.0em | Question Options, Mechanistic Rationales |
| **Body Secondary** | 13px | 400 | 1.5 | +0.01em | Citations, Explanations, Card Descriptions |
| **Metadata Label** | 11px | 700 | 1.0 | +0.08em | Category Pills, Status Badges (Uppercase) |

### 2.3 Spatial Scale & Radii

- **Base Spacing Unit:** 4px (`4px`, `8px`, `12px`, `16px`, `20px`, `24px`, `32px`)
- **Border Radii:**
  - Badges/Pills: `9999px` (Full pill)
  - Options/Inputs: `14px`
  - Cards: `22px`
  - Modals: `28px`
- **Elevation / Glass Shadows:**
  - Subtle: `0 4px 16px rgba(0, 0, 0, 0.25)`
  - Elevated Card: `0 10px 30px rgba(0, 0, 0, 0.45), 0 1px 1px rgba(255, 255, 255, 0.05) inset`

---

## 3. Core Screen Specifications

### 3.1 Screen 1: Daily Mission (Home)
- **Visual Dominance:** A single elevated hero card taking central focus.
- **Components:**
  1. Mission Type Pill: `"Personalized Revision · 12 min"`
  2. Headline: Evidence-grounded active directive (*"Build stronger recall."*)
  3. Description & Plan Summary: Concise list of tasks (*"Due reviews · Targeted practice · Recall check"*)
  4. Disclosure: *"Why this mission?"* expandable accordion explaining memory evidence.
  5. Dominant Action Button: 54px high Indigo gradient CTA (*"Start 12-minute mission →"*).
  6. Subordinate Link: *"Short on time? Try a 5-minute session"*.
  7. Non-Punitive Reassurance footer.

### 3.2 Screen 2: Active Question & Feedback Player
- **Question Stem:** Prominent 18px text with clear contrast.
- **Diagram Container:** If `media_url` is present, render high-definition image with zoom cursor and caption.
- **Options List:** Four distinct option buttons with letter badges `(A)`, `(B)`, `(C)`, `(D)` and comfortable 48px touch targets.
- **Confidence Calibration Selector:** Horizontal selector (1=Guess, 2=Low, 3=Medium, 4=High, 5=Certain) clearly distinguished from question options.
- **Immediate Mechanistic Feedback Box:**
  - Success (Green tint): Explains why the chosen option is chemically/biologically correct.
  - Misconception (Rose tint): Pinpoints why the selected distractor fails and quotes authoritative textbook provenance.

### 3.3 Screen 3: Spaced Repetition Calendar & Explorer
- Spaced review schedule showing upcoming due cards without punitive pressure.
- Searchable syllabus browser by 5 main subjects.

### 3.4 Screen 4: Mock Exam Workspace
- Clean, focused examination interface with top-bar timer (`JetBrains Mono`), question navigator grid, mark for review, and submit modal.
- Negative marking awareness (+4 / -1).

### 3.5 Screen 5: Progress & Meaningful Rewards
- Honest progress metrics: 4 key learning milestones (Missions completed, Delayed recall tests passed, Misconception traps repaired, Topics mastered).
- Flexible weekly study goal setting (3, 5, or 7 missions/week) with non-punitive adjustments.
