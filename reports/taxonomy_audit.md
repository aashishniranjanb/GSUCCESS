# Phase A: Syllabus Taxonomy & Content Registry Audit

**Date:** 2026-10-18  
**Scope:** Canonical Syllabus Taxonomy, Baseline Registries, Content Chunks, and Source Provenance  
**Target Project:** GPAT 2027 Learning OS (`C:\Users\Home\Downloads\PROJECTS\SRE_APP`)

---

## 1. Executive Summary

This audit independently validates the existing syllabus taxonomy, source documents, chunk storage, and content relationships across [`baseline/subjects.json`](file:///c:/Users/Home/Downloads/PROJECTS/SRE_APP/baseline/subjects.json), [`baseline/topics.json`](file:///c:/Users/Home/Downloads/PROJECTS/SRE_APP/baseline/topics.json), [`data/gpat_baseline.db`](file:///c:/Users/Home/Downloads/PROJECTS/SRE_APP/data/gpat_baseline.db), and [`gpat_knowledge.db`](file:///c:/Users/Home/Downloads/PROJECTS/SRE_APP/gpat_knowledge.db).

### Key Audit Findings:
1. **Level 1 (Exam Groups) vs Level 2 (Curriculum Subjects) Conflation:**
   - The current baseline defines 5 broad subject areas corresponding to the NBEMS indicative exam blueprint:
     - `pharmaceutical_chemistry` (43 topics in earlier text, currently 58 topics in `baseline/topics.json`)
     - `pharmaceutics` (67 topics in earlier text, currently 65 topics in `baseline/topics.json`)
     - `pharmacology` (59 topics in earlier text, currently 39 topics in `baseline/topics.json`)
     - `pharmacognosy` (14 topics in earlier text, currently 27 topics in `baseline/topics.json`)
     - `other_subjects` (38 topics in earlier text, currently 32 topics in `baseline/topics.json`)
   - **Critical Architecture Flaw:** In the existing 221-topic registry, Level 2 curriculum subjects (such as *Physical Pharmacy*, *Pharmaceutical Engineering*, *Biochemistry*, *Microbiology*, *Biotechnology*, *Pathophysiology*) were flattened directly into Level 3 `unit_id` fields (e.g. `pharmaceutics__physical_pharmacy`, `pharmaceutical_chemistry__biochemistry`).
2. **Missing Hierarchy Depth (Level 4 & 5 Absence):**
   - In `baseline_topics`, all 221 entries have `parent_topic_id = NULL`.
   - Granular subtopics (e.g., *Phase Rule: One, two & three component systems*, *USP Dissolution Apparatus types*) and explicit learning objectives are absent from the structural database.
3. **Lexical Duplicates:**
   - Two exact topic name collisions exist across different curriculum contexts:
     - `enzymes`: present under `pharmacognosy__pharmacognosy` and `pharmaceutical_chemistry__biochemistry`.
     - `carbohydrates`: present under `pharmaceutical_chemistry__organic_chemistry` and `pharmaceutical_chemistry__biochemistry`.
   - While distinct scientifically, they lack disambiguated learning objectives.
4. **Third-Party vs Official Origin:**
   - All 221 topics were originally parsed from a coaching tracker PDF (`GPAT-SYLLABUS-TRACKER-2027-1.pdf`), marking all 221 topics with `extraction_status = 'SOURCE_DERIVED'` and `verification_status = 'UNVERIFIED'`.
   - The official PCI B.Pharm curriculum and NBEMS 2025 bulletin citations were not structurally separated from coaching-specific notes.
5. **Content Chunk Integrity:**
   - `baseline_chunks` contains 505 chunks with 384-dimensional dense vectors across 6 source files, with cryptographic SHA-256 hashes recorded.

---

## 2. Quantitative Baseline Breakdown

| Exam Group (Level 1) | Canonical Curriculum Subjects (Level 2) | Current Unit Count | Current Topic Count in DB | NBEMS 2025 Indicative Questions |
| :--- | :--- | :---: | :---: | :---: |
| **Pharmaceutics & Allied** | Pharmaceutics, Physical Pharmacy, Biopharmaceutics & Pharmacokinetics, Dispensing & Hospital Pharmacy, Pharmaceutical Engineering | 5 | 65 | 38 (152 marks) |
| **Pharmaceutical Chemistry & Allied** | Physical Chemistry, Organic Chemistry, Pharmaceutical Chemistry, Pharmaceutical Analysis, Biochemistry | 5 | 58 | 38 (152 marks) |
| **Pharmacology & Allied** | Pharmacology, Anatomy & Physiology, Pathophysiology, Clinical Pharmacy & Therapeutics | 4 | 39 | 28 (112 marks) |
| **Pharmacognosy & Allied** | Pharmacognosy, Natural Products | 1 | 27 | 10 (40 marks) |
| **Other B.Pharm Subjects** | Microbiology, Biotechnology, Pharmaceutical Jurisprudence, Pharmaceutical Management | 4 | 32 | 11 (44 marks) |
| **TOTAL** | **19 Curriculum Disciplines** | **19** | **221** | **125 Questions (500 marks)** |

---

## 3. Structural Deficiencies & Risks

1. **Risk of False Topic Aggregation:**
   - Because `baseline_questions` had 2,015 of 2,063 items initially pointing to `pharmacology__pk_absorption`, reporting subject readiness without a verified canonical hierarchy produced misleading coverage metrics.
2. **Inconsistent Unit Boundaries:**
   - *Physical Chemistry* and *Biochemistry* are distinct university disciplines in the PCI regulations, but were forced under `pharmaceutical_chemistry` purely to align with NBEMS exam scoring buckets.
   - *Solution:* Keep `exam_group_id` (NBEMS 5 groups) and `curriculum_subject_id` (PCI 19 disciplines) as distinct orthogonal dimensions.
3. **No Support for Multi-Topic Content Assets:**
   - In `baseline_chunks`, topics were encoded as serialized JSON strings (`topic_ids_json`). A proper relational content catalog requires normalized many-to-many associations (`topic_content_links`) so a single book chapter can be referenced across multiple topics.

---

## 4. Audit Conclusion & Recommendations

The existing 221 topics provide an effective vocabulary, but lack the structural depth required for multi-modal learning assets (flashcards, concept nodes, reference book page references, and PYQ linking). 

The system must adopt a **5-tier canonical hierarchy** (Exam Area $\rightarrow$ Curriculum Subject $\rightarrow$ Unit $\rightarrow$ Topic $\rightarrow$ Subtopic / Learning Objective) while preserving 100% backward compatibility with all active question and session references.
