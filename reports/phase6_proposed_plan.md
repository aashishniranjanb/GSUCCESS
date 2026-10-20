# Phase 6 Read-Only Audit & Proposed Implementation Plan

**Date:** 2026-10-17  
**Audited Target:** `data/gpat_baseline.db` & `gpat_knowledge.db`  
**Scope:** Topic classification repair, explanation pipeline, visual question defect resolution, and adaptive personalization validation.

---

## 1. Baseline Read-Only Audit Findings

### A. Topic Mapping Bottleneck
- **Total Published Questions:** 2,063 in `baseline_questions` and `questions`.
- **Accurately Mapped Diagnostic Items:** 48 questions mapped across granular pharmacology topics (`q_gpat_001` through `q_gpat_047`).
- **Fallback Assignment Bottleneck:** **2,015 questions** (97.67% of the bank) are currently assigned to the fallback category `pharmacology__pk_absorption`.
- **Target Official Taxonomy:** 5 core subjects, 221 topics, and 38 concepts defined in [`data/gpat_baseline.db`](file:///c:/Users/Home/Downloads/PROJECTS/SRE_APP/data/gpat_baseline.db).

### B. Explanation Coverage Bottleneck
- **Pedagogically Grounded Explanations:** 48 questions (2.33%) contain mechanistic explanations and option-by-option distractor analysis linked to textbook citations.
- **Official Provenance Placeholders:** 2,015 questions (97.67%) only state `Official GPAT <year> question from <paper_id>.` with empty distractor reasons (`{}`).
- **Zero-Fabrication Principle:** No unverified LLM hallucinations or fake book page numbers have been inserted.

### C. Visual Option & Stem Defects (Audit of Source PDFs)
Direct inspection of high-resolution rendered source PDF pages reveals:
1. **GPAT 2017 Q84 (Page 5):** "Which of the following dienes can undergo Diels-Alder reaction most readily" — Options (a), (b), (c), (d) are chemical skeletal structures of conjugated dienes.
2. **GPAT 2017 Q87 (Page 6):** "In the reaction of 2-nitrotoluene with bromine in presence of iron..." — Options (a), (b), (c), (d) are isomeric bromonitrotoluene structures.
3. **GPAT 2014 Q103 (Page 5):** "Identity the structure of barbituric acid" — Options (a), (b), (c), (d) are cyclic barbiturate tautomers.
4. **GPAT 2012 Q116 (Page 9):** "Both of the CMI and PMR spectra of an unknown compound show four absorption peaks each. Identify the unknown compound" — Options are dimethylcyclohexane isomers.
5. **GPAT 2012 Q117 (Page 9):** "Out of the four given compounds choose the one which is aromatic" — Options are annulenes and bicyclic conjugated rings.
6. **GPAT 2022 Q92 (Page 7) & GPAT 2015 Q71 (Page 4):** Both "Heme is" and "Taxol is" are authentic, verbatim question stems from the original official examination papers.

---

## 2. Proposed Implementation Plan & Acceptance Criteria

### Gate 6.1: Deterministic Topic Mapping Pipeline
- **Methodology:** Multi-factor ontology-driven rule engine combining:
  1. High-signal pharmacology, chemistry, pharmaceutics, and pharmacognosy domain terminology.
  2. B.Pharm / GPAT syllabus taxonomy keywords from `baseline_topics` (221 topics) and `gpat_ontology.yaml`.
  3. Exact term weighting (chemical names, drug suffixes e.g. `-olol`, `-pril`, `-dipine`, dosage forms, botanical families).
- **Quality States:**
  - `CONFIDENT_MATCH` (score $\ge 3$): Mapped to specific `subject_id` and `topic_id`.
  - `NEEDS_REVIEW` (score 1..2): Staged in `topic_mapping_review`.
  - `UNMAPPED_PYQ` (score 0): Explicit unmapped state; never falsely attributed to `pk_absorption`.
- **Validation:** Stratified review of 50 sampled questions (10 per subject) reporting precision, coverage, and confusion matrix.

### Gate 6.2: Explanation Retrieval & Staging Pipeline
- **Policy:** Explicit separation of answer-key provenance (`OFFICIAL_KEY_VERIFIED`) from explanatory evidence (`AI_GENERATED_NEEDS_REVIEW` vs `AUTHORITATIVE_VERIFIED`).
- **Priority:** High-yield topics (autonomic nervous system, cardiovascular, antibiotics, dosage forms, crude drugs) and frequently encountered question traps.
- **Grounding:** Extract genuine conceptual rationale and distractor explanations with verified concept linking. Never fabricate external textbook page numbers.

### Gate 6.3: Visual Question Repair & Defect Staging
- Extract cropped SVG/PNG option plates for the 5 visual chemical questions (`2017 Q84`, `2017 Q87`, `2014 Q103`, `2012 Q116`, `2012 Q117`).
- Keep these 5 items quarantined in `pyq_review_queue` until visual assets are validated.
- Mark `2022 Q92` and `2015 Q71` as verified verbatim stems with provenance notes.

### Gate 6.4: Personalization & Closed-Loop Verification
- Test 5 synthetic learner profiles against the repaired topic mappings:
  1. Overdue FSRS cards across varied subjects.
  2. Active misconceptions in specific newly mapped topics (e.g. tablet defects vs anticholinergics).
  3. Overconfident errors.
  4. Low-confidence correct answers.
  5. Unassessed learner.
- Confirm that the Daily Mission adaptively recommends targeted review tasks without false mastery claims.

### Gate 6.5: Release Sign-Off
- Database integrity checks (`PRAGMA integrity_check`, `PRAGMA foreign_key_check`).
- Protected learner table checksum verification.
- Complete regression suite (71 tests passing).
- Deliver 5 comprehensive Phase 6 markdown reports.
