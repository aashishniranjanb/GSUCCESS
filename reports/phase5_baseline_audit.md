# Gate 0: Release Baseline & Database Safety Audit

**Date:** 2026-10-17  
**Execution Command:** `.venv\Scripts\pytest tests/ -v`  
**Execution Time:** 109.24s (0:01:49)  
**Total Tests:** 71 passed, 0 failed, 0 skipped, 1 warning (Starlette deprecation)  
**Target Databases Audited:**
- Static Baseline: [`data/gpat_baseline.db`](file:///c:/Users/Home/Downloads/PROJECTS/SRE_APP/data/gpat_baseline.db)
- Learner Execution DB: [`gpat_knowledge.db`](file:///c:/Users/Home/Downloads/PROJECTS/SRE_APP/gpat_knowledge.db)

---

## 1. Test Suite Reconciliation (69 vs 71 Tests)

In the previous Phase 4 completion report, **69 tests** were reported.
In the current baseline, **71 tests** are executed and passing:
- The 2 additional tests were introduced in [`tests/verification/test_official_125_mock.py`](file:///c:/Users/Home/Downloads/PROJECTS/SRE_APP/tests/verification/test_official_125_mock.py):
  1. `test_official_125_blueprint_parameters`: Verifies parameters (125Q, 180m, +4/-1, OFFICIAL_EXAM_SIMULATION).
  2. `test_create_and_run_official_125_mock`: Tests end-to-end creation, question retrieval, answering with negative marking verification, and final evaluated submission state.

All 71 tests execute successfully across the repository.

---

## 2. Database Backup Verification

Verified pre-migration backups created via SQLite online backup API:
- `data/gpat_baseline.db`:
  - Path: `backups/gpat_baseline_20261017_234124.db`
  - Size: 6,172,672 bytes
  - SHA-256: `3da255bc63919f5209556a8f13b09031db465d97991ae1b39e448558a192f1f8`
- `gpat_knowledge.db`:
  - Path: `backups/gpat_knowledge_20261017_234124.db`
  - Size: 4,468,736 bytes
  - SHA-256: `0967699f375feaf85b82955c1a1a7af6023b5511070229f51fefab9fa241f983`

---

## 3. SQLite Integrity and Foreign Key Checks

### Baseline Database (`data/gpat_baseline.db`)
- `PRAGMA integrity_check`: `ok`
- `PRAGMA foreign_key_check`: `0` violations
- Total Tables: 20
- Key Table Counts:
  - `baseline_questions`: 2,063
  - `pyq_review_queue`: 89
  - `baseline_topics`: 221
  - `baseline_subjects`: 5
  - `candidate_claims`: 704

### Learner Database (`gpat_knowledge.db`)
- `PRAGMA integrity_check`: `ok`
- `PRAGMA foreign_key_check`: `0` violations
- Total Tables: 35
- Key Table Counts:
  - `questions`: 2,063
  - `concepts`: 38
  - `mock_exams`: 8
  - `mock_exam_items`: 200
  - `mock_attempts`: 7

---

## 4. Protected Learner State Cryptographic Fingerprints

To ensure complete non-contamination and preservation of historical learner activity, cryptographic SHA-256 checksums were captured across all learner tables prior to Gate 1 execution:

| Table Name | Record Count | Pre-Change SHA-256 Checksum |
|---|---|---|
| `student_attempts` | 7 | `c9fdba5fb7ee545fe3c3463c71c061e3ef5d34005b301bf05317cf95006e17bc` |
| `fsrs_cards` | 11 | `a64684220eb093af9cfd8c58b5502abb457ce2a3f09a8fe64c149a01dbe9e2f5` |
| `learning_events` | 10 | `303d3b573c9c2a79cb90af29507a5295954dd55ba68563fa061ddb2be518ae32` |
| `study_sessions` | 3 | `252386f646633a27f1c0149ad4ed90b216fb08e7ebe1f015f7a099176b8abee1` |
| `study_session_items` | 32 | `cb4d08ee20e1e879297faad7753445a4c19cf5cab8a82dddd9221299c33c60a3` |
| `synced_client_events` | 3 | `2bba67a04b6ae15afc5b8ff00eaa624bb49fe268311fceb752d0959f817ceb69` |
| `learner_achievements` | 4 | `7e033b93bda403efc0cf92a8466c1ae5099b487d15c34fa12ce293967f73574f` |
| `learner_goals` | 0 | `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` |

**Gate 0 Status:** COMPLETE & VERIFIED.
