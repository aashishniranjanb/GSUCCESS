# Phase 6.2 Known Issues & Risk Register

**Date:** 2026-10-18  
**Phase:** 6.2 Visual PYQ Repair & Explanation Pipeline Pilot  

---

## 1. Residual Content Risks

### 1.1 Non-Promoted Status of Phase 6.1 Topic Mappings
- **Observation:** In Phase 6.1, 1,770 of 2,015 questions were mapped to specific syllabus topics with 90.9% holdout precision in staging. However, per the Phase 6.2 safety contract, topic mappings have **not** been promoted to `data/gpat_baseline.db` or `gpat_knowledge.db` to prevent untested downstream side-effects.
- **Risk:** Until Phase 6.3 topic mapping promotion is formally approved, live adaptive planning and mock domain breakdowns still fall back to `pharmacology__pk_absorption` for bulk legacy PYQs.
- **Mitigation:** Promotion is isolated in `scripts/stage_topic_mappings.py` and ready for activation after Phase 6.2 verification.

### 1.2 Scale of Ingested Explanations
- **Observation:** 25 explanations are fully curated and staged in `reports/phase6_2_review_queue.csv`. The remaining 1,990 legacy PYQs currently present official exam provenance only (*"Official GPAT <year> question from <paper_id>"*) with empty distractor reasons.
- **Risk:** Students reviewing uncurated PYQs will only see the correct answer key without detailed mechanistic explanations.
- **Mitigation:** The 4-state workflow (`OFFICIAL_KEY_VERIFIED`, `AUTHORITATIVE_VERIFIED`, `AI_GENERATED_NEEDS_REVIEW`, `INSUFFICIENT_EVIDENCE`) is operational. Bulk batch curation can proceed using the review queue format established in Phase 6.2.

---

## 2. Technical & Data Observations

### 2.1 Database Separation & Synchronization
- **Observation:** `data/gpat_baseline.db` holds the canonical published question bank (2,063 items) and media assets (7 items). `gpat_knowledge.db` holds mutable learner state plus a localized mirror of baseline tables for offline-first queries.
- **Mitigation:** Both databases were updated to register the 5 recovered media items in `baseline_media` and `baseline_questions.media_id`. Any future baseline updates must continue using `scripts/sync_media_to_learner_db.py` to prevent desynchronization.

### 2.2 Starlette Deprecation Warning in TestClient
- **Observation:** Pytest outputs a minor warning:
  `StarletteDeprecationWarning: Using httpx with starlette.testclient is deprecated; install httpx2 instead.`
- **Impact:** Zero functional impact; all 80 tests execute and pass cleanly.
- **Mitigation:** Schedule dependency update to `httpx2` during routine environment maintenance.
