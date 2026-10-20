# GPAT Learning OS — Phase 5C: Production Question Player Specification

## Overview

The Production Question Player is the single canonical assessment interface for the GPAT Learning OS. It eliminates interface fragmentation between Daily Mission study sessions, PYQ past-paper exploration, and Topic Explorer practice drills.

## Architecture & Design Decisions

### 1. Unified Player Component (`UniversalQuestionPlayer`)
- **Location:** `web/src/components/study/universal-question-player.tsx`
- **Replaces & Consolidates:** Fragmented inline logic previously split between `web/src/components/study/question-card.tsx` and `web/src/components/pyqs/pyq-practice-workspace.tsx`.
- **Modes Supported:**
  - `Daily Mission`: Timed, spaced-repetition questions synchronized with session timeline and FSRS engine.
  - `PYQ Practice`: Official historical questions with official answer-key badge, question provenance, and distractor rationale.
  - `Topic Drill`: Direct practice from Level 4 syllabus topics in the Syllabus Explorer.

### 2. Multimodal Diagram & Chemical Structure Support
- Diagram-backed questions link directly to `baseline_media` via `media_id` (e.g. DRC curves, Diels-Alder diene candidates, bromonitrotoluene reaction isomers).
- Rendered with accessible alt text, academic captioning, and image zoom state.
- Served through backend static media mount `/media/` preserving file SHA-256 integrity.

### 3. Pre-Submission Confidence Calibration
- Prior to submitting an answer, the student selects a 1–5 confidence rating:
  - 1: Guess / Unsure
  - 2: Low Confidence
  - 3: Moderate
  - 4: Confident
  - 5: Certain
- Transmitted to `/api/study/attempt` to feed `learner_engine.py` calibration taxonomy:
  - `SOLID_MASTERY`: Correct answer + High Confidence (4–5)
  - `FRAGILE_KNOWLEDGE`: Correct answer + Low Confidence (1–3)
  - `OVERCONFIDENT_MISCONCEPTION`: Incorrect choice + High Confidence (4–5)
  - `KNOWLEDGE_GAP`: Incorrect choice + Low Confidence (1–3)

### 4. Post-Submission Feedback & Evidence Provenance
- Clear distinction between official answer key vs. candidate choice.
- Misconception explanation tailored to the specific selected distractor option.
- Full scientific explanation and source citation page numbers.
- Memory recall cue for active retention.
- FSRS rating badge (`Again`, `Hard`, `Good`, `Easy`) and next scheduled review date.

### 5. Session State & Protection
- LocalStorage caching for session progress and question index resumption.
- Duplicate submission prevention.
- Seamless offline error capture and notice.
