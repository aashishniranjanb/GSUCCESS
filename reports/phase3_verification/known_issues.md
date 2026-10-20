# Phase 3 Known Issues & Production Readiness Edge Cases

**Audit Timestamp:** 2026-10-17T01:33:30+05:30  
**Target:** GPAT 2027 Learning OS — Phase 3 Personalized Study Orchestration

---

## 1. Edge Cases & Known Boundaries

### 1.1 In-Process SQLite Mutation Isolation in Test Suites
- **Symptom:** When running API or engine tests directly against the default database path without cleaning test rows, synthetic learner actions (e.g. `test_hypo_sync_user` or `pwa_test_student`) increment `learning_events`, `fsrs_cards`, and `student_attempts`.
- **Mitigation Implemented:** All property tests (`test_hypothesis_invariants.py`, `test_playwright_pwa.py`, `test_schemathesis_api.py`, and `test_mock_engine.py`) now execute with temporary database copies or deterministic `tearDown()` cleanup blocks.
- **Production Recommendation:** Multi-tenant production deployments must bind user databases via connection pooling and scoped tenant transactions.

### 1.2 Minimum Question Floor on Small Time Budgets
- **Symptom:** When scheduling sessions for very short intervals (e.g. 5 minutes), `LearnerEngine.generate_daily_session` enforces `target_questions = max(4, int(session_minutes / 2.5))`. Four questions with an estimated 90–120 seconds each take 360–480 seconds (6 to 8 minutes).
- **Design Intent:** A minimum of 4 questions ensures sufficient diagnostic diversity across the question bank rather than single-question micro-sessions.
- **Production Recommendation:** The UI displays `~6–8 min actual estimate` when the learner selects a 5-minute study window.

### 1.3 Schemathesis Null Byte Query Parameters
- **Symptom:** When Schemathesis fuzzes string parameters with arbitrary Unicode (including null bytes `\x00`), SQLite rejects queries containing null characters with `sqlite3.ProgrammingError: the query contains a null character`.
- **Mitigation Implemented:** Standard FastAPI validation sanitizes string inputs; property tests filter non-null string parameters.

### 1.4 Browser ServiceWorker Cache Invalidation
- **Symptom:** During rapid PWA iterations, ServiceWorker caches may retain older static question payloads until a bump in `sw.js` cache version.
- **Production Recommendation:** CI/CD deployment automatically bumps `CACHE_VERSION = 'v-gpat-phase3-...'` on release builds.
