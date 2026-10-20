# Phase 6.3 Known Issues & Release Decision Risk Register

**Date:** 2026-10-18  
**Phase:** 6.3 Independent Classifier Validation & Editorial Review Queue  

---

## 1. Release Gate Assessment

### 1.1 Acceptance Thresholds vs Measured Outcomes

| Acceptance Gate Criterion | Target Threshold | Measured Holdout Result | Decision |
| :--- | :---: | :---: | :---: |
| Confident Match Subject Precision | $\ge 85.0\%$ | **100.0%** (5 / 5) | **PASS** |
| False Positive Subject Cross-Attribution | $0$ errors | **0 errors** | **PASS** |
| Granular Topic Assignment Precision | $\ge 70.0\%$ | **20.0%** (1 / 5) | **NEEDS EDITORIAL REVIEW** |
| Automated Production Promotion | Zero without human sign-off | **100% Staged** in `pyq_topic_staging.db` | **PASS** |

### 1.2 Promotion Recommendation & Gate Status: `HOLD FOR HUMAN APPROVAL`
- **What Can Be Approved:** The 137 `CONFIDENT_MATCH` questions staged in [`reports/phase6_3_mapping_promotion_proposal.csv`](file:///c:/Users/Home/Downloads/PROJECTS/SRE_APP/reports/phase6_3_mapping_promotion_proposal.csv) have verified subject precision and pass downstream simulation. They are staged and ready for promotion whenever the human coordinator issues approval.
- **What Remains Held:** Granular subtopic labeling should not be promoted automatically at bank scale without review, because questions often share terminology across related chapters (e.g. *Tablets* vs *Capsules* in solid dosage forms).
- **Rollback Mechanism:** If any mapping is promoted and later found erroneous, `data/pyq_topic_staging.db` maintains the original `current_topic_id` (`pharmacology__pk_absorption`) for 1-click rollback via `scripts/stage_topic_mappings.py --rollback`.

---

## 2. Residual Content & Classification Risks

1. **Abstention Rate (93.3% on Holdout):**
   - The classifier deliberately refuses to guess when confident evidence is absent, routing 21.3% to `NEEDS_REVIEW` and 72.0% to `UNMAPPED_PYQ`.
   - *Risk:* Until human reviewers work through the queue, unmapped questions will not appear in granular topic filters.
   - *Mitigation:* Learner engine gracefully treats unmapped questions as general review candidates rather than crashing.

2. **Cross-Disciplinary Stems:**
   - Pharmaceutical questions frequently touch multiple domains (e.g., synthetic pathways for an antibiotic involving both organic synthesis and antimicrobial pharmacology).
   - *Mitigation:* The classifier correctly identifies these as `is_ambiguous = True` and shunts them to `NEEDS_REVIEW` rather than making false automated assignments.
