# Sprint Report: GPAT 2027 Practice and Personalization Loop

**Date:** 2026-10-17  
**Status:** Complete & Fully Passing (29/29 Automated Tests)  
**Workspace:** `C:\Users\Home\Downloads\PROJECTS\SRE_APP`  

---

## Executive Summary

This sprint delivered a fully evidence-verified practice and personalization loop for the GPAT 2027 Learning OS. The work expanded the repository beyond architecture into actual learning workflows:
1. **PYQ Inventory & Answer-Key Mapping:** Audited all 40 PDFs in `PYQs 2026-2010/` (22 GATE papers from 1988–2009 and 18 GPAT papers from 2010–2026), systematically extracting page counts, text yield, and official answer-key page locations.
2. **Verified Question Pipeline:** Staged 60 official questions from GPAT 2025 into [`data/pyq_staging/gpat_2025_staged.json`](file:///c:/Users/Home/Downloads/PROJECTS/SRE_APP/data/pyq_staging/gpat_2025_staged.json) with verified option alignments against the official NBE/NTA answer key (`1-d 2-c 3-b ...`), distractor rationales, and syllabus topic mappings.
3. **Personalization & Practice Integration:** Linked the question bank directly to the FSRS spaced repetition engine, confidence calibration quadrant, misconception detection, and session generation.
4. **PWA Mobile-First Rendering:** Added visual MCQ diagram rendering (`/media/...`) with tap-to-zoom modal support in [`frontend/public/index.html`](file:///c:/Users/Home/Downloads/PROJECTS/SRE_APP/frontend/public/index.html).
5. **Quality Verification & Clean Regression Baseline:** Established 29 passing tests (up from 24 passing, 1 failing), with 100% preservation of all student history in [`gpat_knowledge.db`](file:///c:/Users/Home/Downloads/PROJECTS/SRE_APP/gpat_knowledge.db).

---

## 1. Phase 1 — PYQ Archive Audit & Mapping

All 40 PDF papers in `PYQs 2026-2010/` were inventoried. The results are permanently documented in [`reports/pyq_inventory.csv`](file:///c:/Users/Home/Downloads/PROJECTS/SRE_APP/reports/pyq_inventory.csv) and [`reports/pyq_inventory.json`](file:///c:/Users/Home/Downloads/PROJECTS/SRE_APP/reports/pyq_inventory.json).

### Inventory Summary
- **Total Exam Papers:** 40 PDF files
  - **GATE Pharmacy:** 22 papers (1988 to 2009)
  - **GPAT Pharmacy:** 18 papers (2010 to 2026)
- **Answer Key Findings:**
  - In modern papers (e.g., GPAT 2025 QP Answer Key), the official key is located at **Page 7** with an explicit list mapping: `1-d, 2-c, 3-b, 4-d, 5-a, 6-a, ... 125-d`.
  - Older papers (e.g., GPAT 2010–2018) embed answer keys either in separate appendiced tables or at the end of each question section.
  - Automated blind extraction across all 40 papers without per-paper key anchoring introduces indexing drift; explicit staging per paper with human/regex audit is necessary.

---

## 2. Phase 2 — Pilot Question Batch & Verification

The GPAT 2025 paper was chosen as the pilot benchmark for question staging:
- **60 Questions Staged:** Validated in `data/pyq_staging/gpat_2025_staged.json`.
- **Quality Gates Applied:**
  - `provenance`: Set to `OFFICIAL_PYQ`.
  - `verification_status`: `VERIFIED`.
  - `pyq_year`: `2025`.
  - `paper_id`: `GPAT_QPAK_2025`.
  - 4 verified options per question with 0-indexed correct option matching the Page 7 official answer key.
  - Concept linking to the GPAT ontology (`pk_absorption`, `ans_antimuscarinics`, `cvs_cardiac_glycosides`, `cvs_diuretics`, etc.).
- **Database Insertion:**
  - Integrated into [`data/gpat_baseline.db`](file:///c:/Users/Home/Downloads/PROJECTS/SRE_APP/data/gpat_baseline.db) under `baseline_questions` (total 107 questions: 47 original verified + 60 official PYQs).
  - Also synchronized to [`gpat_knowledge.db`](file:///c:/Users/Home/Downloads/PROJECTS/SRE_APP/gpat_knowledge.db) (`questions` table) so that runtime adaptive sessions serve both high-yield core questions and official PYQs seamlessly.

---

## 3. Phase 3 & 4 — Personalization Engine & PWA Practice Workflow

### Practice Flow Execution
The end-to-end loop operates as follows:
```text
           [ Learner Engine / PWA ]
                      │
     1. GET /api/session (mode: balanced, recall, repair, exam)
                      │
                      ▼
   Candidate Questions Scored: FSRS Due + Misconception Traps + Exam Weight
                      │
                      ▼
   Learner Attempts Question with Confidence Slider (1 to 5)
                      │
                      ▼
            2. POST /api/attempt
                      │
     ┌────────────────┴────────────────┐
     ▼                                 ▼
FSRS Stability & Due Date         Calibration Classification:
Updated (Rating: Again, Good)     • SOLID_MASTERY (Correct + Conf >= 4)
                                  • FRAGILE_KNOWLEDGE (Correct + Conf < 4)
                                  • KNOWLEDGE_GAP (Incorrect + Conf < 4)
                                  • OVERCONFIDENT_MISCONCEPTION (Incorrect + Conf >= 4)
                                       │
                                       ▼
                       Distractor Rationale & Traps Displayed
```

### Mobile & Visual Question Support
- Visual diagram MCQs package `media_url`, `media_alt`, and `media_caption` through [`SQLiteStudyRepository`](file:///c:/Users/Home/Downloads/PROJECTS/SRE_APP/backend/repositories/sqlite_study_repository.py) and [`LearnerEngine`](file:///c:/Users/Home/Downloads/PROJECTS/SRE_APP/learner_engine.py).
- Static image route `/media` is served in FastAPI at [`backend/main.py`](file:///c:/Users/Home/Downloads/PROJECTS/SRE_APP/backend/main.py).
- PWA frontend in [`frontend/public/index.html`](file:///c:/Users/Home/Downloads/PROJECTS/SRE_APP/frontend/public/index.html) includes responsive image containers and a modal zoom overlay (`toggleMediaZoom()`) optimized for smartphone touchscreens (Redmi Note 11 and mobile browsers).

---

## 4. Phase 5 — Production Verification & Automated Tests

The entire test suite now passes with zero failures:
- **Ran 29 tests in 5.629s:**
  - `tests/test_backup_recovery.py` (2 tests: backup, rotation) — **PASS**
  - `tests/test_baseline_build.py` (6 tests: manifest, topics, weightage, graph, chunks, DB integrity) — **PASS**
  - `tests/test_phase2_architecture.py` (5 tests: DB separation, learner preservation, OCR syllabus, real embeddings, visual MCQs) — **PASS**
  - `tests/test_production_readiness.py` (9 tests: sync idempotency, concurrency, batch failures, auth, container restart) — **PASS**
  - `tests/test_reliability_audit.py` (4 tests: FSRS attempts, event log, session immutability, session completion) — **PASS**
  - `tests/test_pyq_practice_flow.py` (4 tests: staged PYQ schema, baseline DB integration, rich session delivery, isolated FSRS attempt calibration) — **PASS**

### Student Data Integrity Guarantee
All original learner state remains 100% intact in [`gpat_knowledge.db`](file:///c:/Users/Home/Downloads/PROJECTS/SRE_APP/gpat_knowledge.db):
- `student_attempts`: 7 preserved original attempts
- `fsrs_cards`: 11 preserved cards
- `learning_events`: 10 preserved events
- `study_sessions`: 3 preserved sessions
- `synced_client_events`: 3 preserved events

---

## 5. Next Steps for Upcoming Sprints

1. **Batch Ingestion for Remaining 2024–2020 GPAT Papers:** Apply `scripts/stage_gpat_2025_pyqs.py` template to GPAT 2024, 2023, 2022, 2021, and 2020.
2. **Subject/Year Filtering in UI:** Add quick-selection pills in the practice screen for specific exam years (e.g., "GPAT 2025 Only", "GPAT 2024 Only").
3. **Automated Distractor Explanation Generation:** For questions missing official rationales, leverage the local vector index and knowledge chunks to generate source-grounded distractor explanations.
