# Gate 2: Syllabus & Topic Taxonomy Quality Report

**Date:** 2026-10-17  
**Database Audited:** `data/gpat_baseline.db`  
**Official Taxonomy Targets:** 5 Subjects, 221 Topics, 17 Weightage Evidence Records

---

## 1. Syllabus Structure Verification

The baseline database contains a verified hierarchical taxonomy constructed from official GPAT/NTA syllabus brochures and AICTE guidelines:
- **5 Core Subjects:**
  1. `pharmaceutical_chemistry`: Pharmaceutical Chemistry and Allied Subjects (58 topics)
  2. `pharmaceutics`: Pharmaceutics and Allied Subjects (65 topics)
  3. `pharmacology`: Pharmacology and Allied Subjects (39 topics)
  4. `pharmacognosy`: Pharmacognosy and Allied Subjects (27 topics)
  5. `other_subjects`: Other B.Pharm Subjects (Clinical, Jurisprudence, Biochemistry, Microbiology) (32 topics)
- **Total Topics:** 221 officially defined topics.

---

## 2. Weightage Evidence Separation

The database strictly separates official facts from third-party and model-derived estimates in `baseline_weightage_evidence`:
- **Official Exam Blueprint (`OFFICIAL_HISTORICAL`):**
  - Marks per correct: `+4.0`
  - Marks per incorrect: `-1.0`
  - Subject question distribution:
    - Pharmaceutical Chemistry: 38 questions (152 marks)
    - Pharmaceutics: 38 questions (152 marks)
    - Pharmacology: 28 questions (112 marks)
    - Pharmacognosy: 10 questions (40 marks)
    - Other Subjects: 11 questions (44 marks)
    - **Total: 125 questions (500 marks)**
- **Third-Party Topic Weightage (`THIRD_PARTY_ESTIMATE`):**
  - Stored with provenance (`dr_pk_classes_brochure`) and marked distinct from official exam notices.

---

## 3. Question Mapping Analysis & Gap Identification

- **Current State:**
  - 48 hand-crafted diagnostic questions have high-granularity concept/topic mappings (e.g., `pharmacology__ans__cvs_diuretics`, `pharmacology__ans__cns_antiepileptics`).
  - The bulk 2,015 ingested PYQs currently point to the fallback topic `pharmacology__pk_absorption` with default concept `pk_absorption`.
- **Quality Assessment & Policy Decision:**
  - In compliance with the Gate 2 mandate: *"Allow an explicit `UNMAPPED` or `NEEDS_REVIEW` state. Do not invent official topic weights or infer that a topic has zero importance."*
  - The 2,015 bulk questions should be transitioned from false specificity (`pk_absorption`) to `UNMAPPED_PYQ` status until NLP keyword classification maps them to their respective 221 syllabus topics.
