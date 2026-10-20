# GPAT & GATE Question Paper Ingestion Audit & Inventory

**Date:** 2026-10-17  
**Pipeline:** [scripts/pyq_pipeline.py](file:///c:/Users/Home/Downloads/PROJECTS/SRE_APP/scripts/pyq_pipeline.py)  
**Corpus Directory:** `PYQs 2026-2010/`  
**Database Targets:**
- Static Baseline: [`data/gpat_baseline.db`](file:///c:/Users/Home/Downloads/PROJECTS/SRE_APP/data/gpat_baseline.db)
- Learner Execution DB: [`gpat_knowledge.db`](file:///c:/Users/Home/Downloads/PROJECTS/SRE_APP/gpat_knowledge.db)

---

## 1. Executive Summary & Inventory Overview

A total of **40 PDF question papers** spanning **GATE (1988–2009)** and **GPAT (2010–2026)** were audited and fingerprinted via SHA-256. 

All 40 documents contain selectable text (no pure image scans), with answer keys located in the final pages of each paper.

The complete inventory has been persisted in:
- CSV: [`reports/pyq_inventory.csv`](file:///c:/Users/Home/Downloads/PROJECTS/SRE_APP/reports/pyq_inventory.csv)
- JSON: [`reports/pyq_inventory.json`](file:///c:/Users/Home/Downloads/PROJECTS/SRE_APP/reports/pyq_inventory.json)

### Summary Metrics:
- **Total PDF Papers:** 40
- **GATE Papers (1988–2009):** 22 papers (6–12 pages each)
- **GPAT Papers (2010–2026):** 18 papers (8–16 pages each, including shift I & II for 2023)
- **Selectable Text Rate:** 100% (40/40)
- **Answer Key Detection:** Verified across all GPAT papers on the rear pages (e.g. Page 7 for 2026, Page 7 for 2025, Page 6 for 2024, Page 12 for 2012).

---

## 2. Ingestion Pipeline & Layout Geometry

### Two-Column Layout Reconstruction
GPAT exam papers (2010–2025) use a dense two-column newspaper layout with headers, footers, and varying column split coordinates (nominal split boundary $x \approx 306$ pt).

The parser in [`scripts/pyq_pipeline.py`](file:///c:/Users/Home/Downloads/PROJECTS/SRE_APP/scripts/pyq_pipeline.py):
1. Filters out headers (`y < 50`) and footers (`y > 740`).
2. Partitions text bounding rects into left column (`x < 306`) and right column (`x >= 306`).
3. Reassembles reading lines by clustering vertically within $\Delta y \le 4.0$ pt, sorting horizontally by $x$-coordinate.
4. Serializes left column then right column with page marker delimiters (`--- [PAGE_N] ---`).
5. Tracks source page numbers for every question via character offset boundaries.

### Answer Key Reconciliation (Zero-Guessing Policy)
- Answer keys are extracted directly from the official answer key table on the designated key page.
- Keys containing asterisks (`*`) or `dropped` are marked `QUESTION_DROPPED_OR_AMBIGUOUS_IN_OFFICIAL_KEY` and flagged as `CONFLICTING_OR_DROPPED`.
- Ambiguous multi-key entries (e.g. `c & d`) are flagged as `MULTIPLE_CORRECT_KEYS`.
- **Under no circumstances does the pipeline fabricate or guess answers with LLMs.** Questions with ambiguous or missing keys are strictly quarantined.

---

## 3. Database State & Separation Verification

### Baseline DB (`data/gpat_baseline.db`)
- `baseline_questions`: **2,063 verified questions**
  - All 2,063 marked `quality_status = 'PUBLISHED'` and `answer_status = 'VERIFIED'`.
  - Content fingerprinted with SHA-256 for idempotent re-imports.
- `pyq_review_queue`: **89 quarantined items**
  - Preserved for manual editorial inspection and resolution.

### Learner Runtime DB (`gpat_knowledge.db`)
- `questions`: **2,063 questions** accessible for active retrieval and mock exams.
- Canonical Learner Progress (Untouched & Intact):
  - `student_attempts`: 7
  - `fsrs_cards`: 11
  - `learning_events`: 10
  - `study_sessions`: 3
  - `synced_client_events`: 3
  - `learner_achievements`: 0 fake entries

---

## 4. Quarantined Review Items Analysis

The 89 quarantined items across 2010–2026 fall into clean deterministic failure classes:
- **`MISSING_OPTION_A_MARKER` (34 items):** Questions formatted with Roman numeral matches (e.g. `Match Column A with Column B`, `I, II, III`) where options are numbered `(1), (2), (3), (4)` or unlabelled.
- **`INVALID_OPTION_COUNT_*` (44 items):** Questions with tables, chemical structures, or multi-statement assertions where non-standard bulleting produced fewer or more than 4 option blocks.
- **`QUESTION_DROPPED_OR_AMBIGUOUS_IN_OFFICIAL_KEY` (8 items):** Official NTA/AICTE dropped questions (e.g., 2024 Q12, Q26, Q47). Correctly quarantined to prevent penalizing candidates.
- **`MULTIPLE_CORRECT_KEYS` (1 item):** Questions where official conducting body accepted multiple answers (e.g., `c & d`).
- **`QUESTION_STEM_NOT_FOUND` (2 items):** Page boundary anomalies during multi-column breaks.

---

## 5. Rollback & Idempotency Procedure

1. **Idempotent Re-Import:** Running `ingest_pyq_batch()` utilizes SQLite `INSERT OR REPLACE` with deterministic primary keys (`pyq_gpat_<year>_<qnum:03d>`) and SHA-256 duplicate fingerprinting. Re-running on existing data produces 0 duplicate records.
2. **Quarantine Isolation:** Quarantined items enter `pyq_review_queue` in `data/gpat_baseline.db` and are **never** published to runtime questions.
3. **Rollback Command:** In the event of an erroneous batch, execution can be reverted safely without affecting learner data:
   ```sql
   -- From data/gpat_baseline.db
   DELETE FROM baseline_questions WHERE pyq_year = <target_year>;
   DELETE FROM pyq_review_queue WHERE pyq_year = <target_year>;
   -- From gpat_knowledge.db (runtime question cache only)
   DELETE FROM questions WHERE id LIKE 'pyq_gpat_<target_year>_%';
   ```
   Learner tables (`student_attempts`, `fsrs_cards`, `learning_events`) remain completely insulated.
