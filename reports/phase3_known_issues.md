# Phase 3 — Known Issues & Runtime Observation Log

**Date:** 2026-10-17  
**Workspace:** `C:\Users\Home\Downloads\PROJECTS\SRE_APP`  

---

## 1. Observations & Runtime Nuances

### A. SQLite Connection Lifecycles in Fast Sequential Unit Tests
- **Symptom:** In rapid multi-test execution on Windows, Python's SQLite connection garbage collection occasionally triggers `ResourceWarning: unclosed database`.
- **Mitigation:** Unit tests use explicit `with` blocks or `conn.close()` inside `finally` clauses. For production operation under ASGI/Uvicorn, connection lifetimes are managed cleanly by FastAPI dependency injection.

### B. Long-Term Concept Mastery Balancing
- **Symptom:** As the question bank grew to 229 questions across 38 concepts, high-importance concepts with active misconceptions (e.g. `ans_antimuscarinics`, `cvs_cardiac_glycosides`) naturally take top priority in balanced daily missions.
- **Handling:** The diversity constraint (max 2 consecutive concept items) successfully interleaves questions across different subjects, preventing single-concept domination while ensuring weak concepts receive repair.

### C. Client-Side Offline Session Cache
- **Symptom:** When learners go offline in the PWA, IndexedDB must cache not only the question stems but also `media_url` and `reason_codes` for proper rendering.
- **Handling:** The `/api/study/today` response includes complete question payloads (`options`, `cue`, `concept_name`, `reason_codes`, `media_url`), enabling complete local execution without network calls until reconnection.
