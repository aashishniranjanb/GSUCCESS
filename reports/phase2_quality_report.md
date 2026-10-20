# Phase 2 — Quality Gate and Pilot Ingestion Report

**Date:** 2026-10-17  
**Scope:** GPAT PYQ Ingestion, Answer-Key Mapping, Quality Gates & Learner Safety  
**Status:** COMPLETE (32 / 32 Automated Unit Tests Passing)  
**Workspace:** `C:\Users\Home\Downloads\PROJECTS\SRE_APP`  

---

## 1. Executive Summary

This report establishes the Phase 2 implementation of the **GPAT PYQ Ingestion Pipeline and Quality Gate Engine**. The pipeline ingests source PDFs from `PYQs 2026-2010`, extracts question stems, option sets, official answer key mappings, computes SHA-256 content hashes, and enforces a strict quality quarantine before publishing records to the learning engine.

### Key Milestones Achieved
1. **Schema Extension & Contract Migration:**
   - Non-breaking extension of `baseline_questions` across `data/gpat_baseline.db` and `gpat_knowledge.db` with contract fields: `quality_status`, `raw_text`, `original_q_number`, `answer_status`, `answer_source_page`, and `rights_status`.
   - Created `pyq_review_queue` table in `data/gpat_baseline.db` to quarantine ambiguous or malformed questions without blocking batch processing.
2. **Deterministic Extraction & Key Reconciliation:**
   - Built `scripts/pyq_pipeline.py` implementing `PYQPipeline` and `ingest_pyq_batch`.
   - Page-level provenance tracking links every question to its exact PDF page.
   - Answer keys are extracted directly from official key pages (e.g. Page 7 for GPAT 2026), matching options without heuristic guessing.
3. **Controlled Pilot (GPAT 2026 — 125 Questions):**
   - **Total Questions Discovered:** 125
   - **Published (`PUBLISHED`):** 122 questions (97.6% clean pass rate).
   - **Quarantined (`NEEDS_CONTENT_REVIEW`):** 3 questions safely routed to `pyq_review_queue` due to option irregularities or multi-column layout challenges.
4. **Idempotency & Database Safety Verification:**
   - Re-running the pipeline multiple times results in exactly 0 duplicate questions and 0 duplicate review items.
   - All runtime learner history in `gpat_knowledge.db` (`student_attempts: 7`, `fsrs_cards: 11`, `learning_events: 10`, `study_sessions: 3`) remains 100% intact.
5. **Regression Test Suite:**
   - Expanded from 29 to **32 tests**; all passing in 5.41s (`Ran 32 tests in 5.415s: OK`).

---

## 2. Source Inventory & Key Location Mapping

All 18 GPAT papers in `PYQs 2026-2010` were audited for exact answer-key anchors:

| File Name | Year | Total Pages | Answer Key Page | Key Format / Count |
|---|---|---|---|---|
| `GPAT_QPAK_2026.pdf` | 2026 | 8 | Page 7 | Explicit list `1-a ... 125-a` (125 keys) |
| `GPAT_QPAK_2025.pdf` | 2025 | 11 | Page 7 | Explicit list `1-d ... 125-d` (125 keys) |
| `GPAT_QPAK_2024.pdf` | 2024 | 10 | Page 6 | Two-column list `1-c ... 125-c` (125 keys) |
| `GPAT_QPAK_2023-I-3.pdf` | 2023 | 13 | Page 9 | Explicit list (125 keys) |
| `GPAT_QPAK_2023-II-2.pdf` | 2023 | 12 | Page 8 | Explicit list (125 keys) |
| `GPAT_QPAK_2022-1.pdf` | 2022 | 14 | Page 10 | Explicit list (125 keys) |
| `GPAT_QPAK_2021-1.pdf` | 2021 | 12 | Page 8 | Explicit list (125 keys) |
| `GPAT_QPAK_2020.pdf` | 2020 | 11 | Page 7 | Explicit list (125 keys) |
| `GPAT_QPAK_2019.pdf` | 2019 | 11 | Page 7 | Explicit list (125 keys) |
| `GPAT_QPAK_2018.pdf` | 2018 | 11 | Page 7 | Explicit list (125 keys) |
| `GPAT_QPAK_2017.pdf` | 2017 | 12 | Page 8 | Explicit list (125 keys) |
| `GPAT_QPAK_2016.pdf` | 2016 | 11 | Page 7 | Explicit list (125 keys) |
| `GPAT_QPAK_2015.pdf` | 2015 | 10 | Page 6 | Explicit list (125 keys) |
| `GPAT_QPAK_2014-2.pdf` | 2014 | 10 | Page 6 | Explicit list (125 keys) |
| `GPAT_QPAK_2013-2.pdf` | 2013 | 10 | Page 6 | Explicit list (125 keys) |
| `GPAT_QPAK_2012-2.pdf` | 2012 | 16 | Page 12 | Explicit list (150 keys) |
| `GPAT_QPAK_2011-2.pdf` | 2011 | 10 | Page 6 | Explicit list (150 keys) |
| `GPAT_QPAK_2010-2.pdf` | 2010 | 9 | Page 5 | Explicit list (100 keys) |

---

## 3. Controlled Pilot Results: GPAT 2026

The pilot run was performed on `GPAT_QPAK_2026.pdf`:
- **Questions Extracted:** 125
- **Questions Published:** 122 (`baseline_questions` total count increased from 107 to 229)
- **Questions Quarantined to Review Queue:** 3

### Quarantined Questions Breakdown
1. `pyq_gpat_2026_035`:
   - **Issue:** `INVALID_OPTION_COUNT_6` (Contains sub-options (b) & (c) in stem text alongside option choices).
   - **Action:** Held in `pyq_review_queue` for manual option delimitation.
2. `pyq_gpat_2026_055`:
   - **Issue:** `MISSING_OPTION_A_MARKER` (Matching table question where column definitions precede option letters).
   - **Action:** Held in `pyq_review_queue` for table extraction review.
3. `pyq_gpat_2026_058`:
   - **Issue:** `INVALID_OPTION_COUNT_12` (Contains section break and multiple embedded Roman numeral matches).
   - **Action:** Held in `pyq_review_queue` for section boundary normalization.

---

## 4. Verification Checklist Status

| Gate | Requirement | Status | Evidence |
|---|---|---|---|
| **1. Source Inventory** | Complete SHA-256 hash & key location for all PDFs | **PASS** | `reports/pyq_inventory.csv`, `reports/pyq_inventory.json` |
| **2. Question Provenance** | Every question links to source PDF, year, and page | **PASS** | Verified in `baseline_questions.source_page` & `paper_id` |
| **3. Answer Integrity** | Official key matched without AI guessing | **PASS** | Regex matched against Page 7 official key entries |
| **4. Idempotency** | Re-import creates 0 duplicates | **PASS** | `test_02_idempotent_reimport` in `test_phase2_pyq_pipeline.py` |
| **5. Database Safety** | Learner progress preserved 100% | **PASS** | Attempts: 7, FSRS: 11, Events: 10, Sessions: 3 |
| **6. Quality Quarantine** | Malformed questions isolated in review queue | **PASS** | 3 quarantined items in `pyq_review_queue` |
| **7. Automated Tests** | All 32 unit tests passing | **PASS** | `Ran 32 tests in 5.415s: OK` |
