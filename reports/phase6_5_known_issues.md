# Phase 6.5 Known Issues & Risk Register

**Date:** 2026-10-18  
**Release Readiness Gate Status:** Approved to enter Phase 7  

---

## 1. Managed Scope Risks Prior to Phase 7

### 1.1 Staged vs Production Topic Mappings
- **Status:** All 137 high-confidence candidate mappings remain in `data/pyq_topic_staging.db` and are recorded in [`reports/phase6_3_mapping_promotion_proposal.csv`](file:///c:/Users/Home/Downloads/PROJECTS/SRE_APP/reports/phase6_3_mapping_promotion_proposal.csv).
- **Behavior:** In production, legacy bulk PYQs currently remain assigned to `pharmacology__pk_absorption`.
- **UI Implication for Phase 7:** The new frontend design must gracefully display an explicit *"Unmapped Question"* badge or topic name placeholder without breaking navigation or layout when browsing question banks.

### 1.2 Quarantined Question Pool (89 Items)
- **Status:** 89 OCR-damaged questions remain quarantined in `pyq_review_queue`.
- **Behavior:** These items are completely excluded from daily missions, practice sessions, and mock exams.
- **UI Implication for Phase 7:** The learner UI does not need to display quarantined items; only the administrative dashboard displays review queues.

---

## 2. Technical Stack Notes for Phase 7

1. **FastAPI & Static Serving:**
   - Frontend is served out of `frontend/public/` mounted in `backend/main.py`.
   - All REST APIs (`/api/study/today`, `/api/study/session/{id}`, `/api/evaluation/...`, `/api/progress/...`) are operational and covered by contract tests.
2. **PWA Architecture:**
   - Vanilla JS / Service Worker / IndexedDB setup in `frontend/public/` ensures zero build complexity and offline resilience.
   - Refactoring in Phase 7 should enhance HTML/CSS design tokens and responsive components without imposing heavyweight frameworks that might disrupt offline sync.
