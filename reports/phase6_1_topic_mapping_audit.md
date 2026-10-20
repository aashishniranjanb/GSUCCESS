# Phase 6.1: Topic Mapping Preflight & Architecture Audit

**Date:** 2026-10-18  
**Scope:** Preflight schema audit, topic consumer mapping, protected learner fingerprints, and taxonomy verification.  
**Databases Inspected:** [`data/gpat_baseline.db`](file:///c:/Users/Home/Downloads/PROJECTS/SRE_APP/data/gpat_baseline.db) and [`gpat_knowledge.db`](file:///c:/Users/Home/Downloads/PROJECTS/SRE_APP/gpat_knowledge.db).

---

## 1. Executive Summary & Problem Scope

The Phase 5 audit revealed that **2,015 of 2,063 published questions (97.67%)** were improperly assigned to the fallback category `pharmacology__pk_absorption` with generic concept `pk_absorption`.

### Primary Risks of Fallback Over-Concentration:
1. **Distorted Diagnostics:** Learner progress dashboards display an overwhelmingly skewed emphasis on pharmacokinetics, despite candidates answering questions across medicinal chemistry, pharmacognosy, and jurisprudence.
2. **Personalized Mission Bias:** The Daily Mission scheduler calculates topic diversity based on concept ID. When thousands of diverse questions share the same concept tag, consecutive diversity constraints are triggered erroneously, starving the candidate of balanced practice.
3. **Mock Exam Breakdown:** Topic performance reports group organic reactions, tablet technology, and crude drug evaluations under one incorrect pharmacology label.

---

## 2. Consumer & Schema Mapping

### A. Database Consumers
- `data/gpat_baseline.db` -> `baseline_questions.topic_id`
  - References `baseline_topics.topic_id` (221 defined syllabus topics).
  - Subject field is derived from `baseline_topics.subject_id` (5 canonical subjects).
- `gpat_knowledge.db` -> `questions.concept_id`
  - References `concepts.id` (38 high-yield concepts).
  - Consumed by `LearnerEngine`, `MockScorer`, and `AchievementService`.

### B. Application Code Consumers
- [`learner_engine.py`](file:///c:/Users/Home/Downloads/PROJECTS/SRE_APP/learner_engine.py): Consumes `concept_id` for concept memory state tracking, retrievability decay, and diversity constraints.
- [`backend/evaluation/mock_scorer.py`](file:///c:/Users/Home/Downloads/PROJECTS/SRE_APP/backend/evaluation/mock_scorer.py): Consumes `concept_id` and `domain_id` to compute subject and topic-level accuracy.
- [`backend/achievement_service.py`](file:///c:/Users/Home/Downloads/PROJECTS/SRE_APP/backend/achievement_service.py): Evaluates topic mastery awards using `concept_id`.

---

## 3. Data Safety & Integrity Baseline

- **Baseline Database:** `PRAGMA integrity_check` = `ok`, `PRAGMA foreign_key_check` = `0` violations.
- **Learner Database:** `PRAGMA integrity_check` = `ok`, `PRAGMA foreign_key_check` = `0` violations.
- **Protected Table Invariant:** Pre-migration SHA-256 fingerprints recorded for `student_attempts`, `fsrs_cards`, `learning_events`, `study_sessions`, `synced_client_events`, and `learner_achievements`.
- **Pre-Migration Backups:** Staged in `backups/gpat_baseline_20261017_235955.db` and `backups/gpat_knowledge_20261017_235955.db`.
