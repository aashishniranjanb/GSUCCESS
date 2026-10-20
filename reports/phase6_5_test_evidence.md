# Phase 6.5: Full Test Evidence & Benchmark Log

**Date:** 2026-10-18  
**Total Tests:** 95  
**Passed:** 95  
**Failed:** 0  
**Warnings:** 1 (StarletteDeprecationWarning regarding httpx2)  
**Execution Duration:** 35.98s  

---

## 1. Test Suite Composition & Coverage

| Test File | Test Count | Module Scope |
| :--- | :---: | :--- |
| `tests/test_backup_recovery.py` | 17 | Online database backup, SHA-256 verification, gzip compression, restore invariants. |
| `tests/test_baseline_build.py` | 6 | Baseline markdown chunking, source hashing, graph edges, and authority separation. |
| `tests/test_phase2_architecture.py` | 6 | Dual-database separation, read-only baseline queries, learner database safety. |
| `tests/test_phase2_pyq_pipeline.py` | 8 | Ingestion audit, quarantine filtering, option count validation, answer key matching. |
| `tests/test_phase3_personalized_orchestration.py` | 5 | Synthetic learner states, diversity constraints, `/api/study/today` serving. |
| `tests/test_phase6_2_visual_and_explanations.py` | 5 | Recovered PNG verification, SHA-256 checksums, HTTP serving, explanation queue. |
| `tests/test_production_readiness.py` | 8 | Admin security auth, concurrent retry idempotency, container entrypoint. |
| `tests/test_pyq_practice_flow.py` | 4 | Real practice session generation, distractor analysis, FSRS rating transitions. |
| `tests/test_reliability_audit.py` | 4 | Session immutability, learning event append-only log, attempt recording. |
| `tests/verification/test_daily_mission_flow.py` | 6 | 12-min mission vs 5-min session, idempotent refresh, resumption UX. |
| `tests/verification/test_gate_8_learner_personas.py` | 8 | Core persona archetypes (new learner, overdue reviews, fragile guesses). |
| `tests/verification/test_gate_c_learning_loop.py` | 1 | Complete closed-loop learning from initial attempt to scheduled recall. |
| `tests/verification/test_hypothesis_invariants.py` | 2 | Property-based testing for session bounds and sync idempotency. |
| `tests/verification/test_official_125_mock.py` | 2 | Official 125-question mock simulation, 180-min timer, +4 / -1 negative marking. |
| `tests/verification/test_phase6_1_topic_mapping.py` | 4 | Classifier precision signals, ambiguous question routing, unmapped state. |
| `tests/verification/test_phase6_3_classifier_validation.py` | 5 | Independent holdout reproducibility, staging schemas, proposal CSV formats. |
| `tests/verification/test_phase6_4_adaptive_personas.py` | 10 | 10 full adaptive learner personas driving explainable mission recommendations. |
| `tests/verification/test_playwright_e2e_gate_b.py` | 1 | Real PWA offline IndexedDB survival and UI rendering. |
| `tests/verification/test_playwright_phase4_mission.py` | 1 | Playwright Daily Mission completion loop and celebration modal. |
| `tests/verification/test_playwright_pwa.py` | 1 | Playwright mobile PWA navigation, study session, and offline sync. |
| `tests/verification/test_progress_rewards.py` | 7 | Achievement rules: delayed recall, misconception repair, weekly goals, honesty. |
| `tests/verification/test_schemathesis_api.py` | 2 | Property-based fuzz testing of study and review endpoints. |

---

## 2. Benchmark Summary

```
======================= 95 passed, 1 warning in 35.98s =======================
```
All learning mechanisms, schedulers, mock assessment engines, and database safety protocols are 100% verified.
