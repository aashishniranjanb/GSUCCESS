# Gate 6: Mock Exam Integrity & Official Simulation Report

**Date:** 2026-10-17  
**Engines Audited:** [`backend/evaluation/mock_engine.py`](file:///c:/Users/Home/Downloads/PROJECTS\SRE_APP\backend\evaluation\mock_engine.py), [`backend/evaluation/mock_scorer.py`](file:///c:/Users/Home/Downloads/PROJECTS\SRE_APP\backend\evaluation\mock_scorer.py), [`backend/evaluation/mock_blueprint.py`](file:///c:/Users/Home/Downloads/PROJECTS\SRE_APP\backend\evaluation\mock_blueprint.py)  
**Automated Tests:** [`tests/verification/test_official_125_mock.py`](file:///c:/Users/Home/Downloads/PROJECTS\SRE_APP\tests\verification\test_official_125_mock.py), [`tests/evaluation/test_mock_engine.py`](file:///c:/Users/Home/Downloads/PROJECTS\SRE_APP\tests\evaluation\test_mock_engine.py)

---

## 1. Exam Blueprint & Regulatory Compliance

The mock exam simulation engine strictly models the official National Testing Agency (NTA) GPAT examination structure:

| Blueprint Parameter | Official Specification | System Implementation | Verification Status |
|---|---|---|---|
| Blueprint Name | `OFFICIAL_GPAT_125` | `OFFICIAL_GPAT_125` | VERIFIED |
| Exam Version | `OFFICIAL_EXAM_SIMULATION` | `OFFICIAL_EXAM_SIMULATION` | VERIFIED |
| Total Questions | 125 MCQs | 125 MCQs | VERIFIED |
| Duration | 180 Minutes (3.0 Hours) | 10,800 Seconds | VERIFIED |
| Correct Answer Marks | +4.0 Marks | +4.0 Marks | VERIFIED |
| Negative Marking | -1.0 Marks | -1.0 Marks | VERIFIED |
| Maximum Raw Score | 500.0 Marks | 500.0 Marks | VERIFIED |
| Unanswered Penalty | 0 Marks | 0 Marks | VERIFIED |

---

## 2. State Machine & Integrity Verification

The mock session executes a deterministic, authoritative lifecycle:
$$\text{CREATED} \longrightarrow \text{STARTED} \longrightarrow \text{IN\_PROGRESS} \longleftrightarrow \text{PAUSED} \longrightarrow \text{SUBMITTED} \longrightarrow \text{EVALUATED}$$

### Key Invariants Tested:
1. **Server-Authoritative Timer:** Remaining time is tracked on the server based on elapsed execution timestamps ($t_{\text{remaining}} = t_{\text{duration}} - t_{\text{elapsed}}$). Pausing freezes the elapsed accumulator cleanly.
2. **Duplicate-Free Item Selection:** All 125 questions selected for an official mock session are guaranteed distinct. Quarantined questions (`pyq_review_queue`) are completely excluded.
3. **Resumption & Reload Safety:** Persisted in `mock_exams` and `mock_exam_items`, allowing safe recovery after browser reloads or network interruptions.
4. **Scoring Correctness:** Tested with deliberate answer vectors:
   - 3 Correct, 2 Incorrect $\to 3 \times (+4.0) + 2 \times (-1.0) = +10.0$ marks out of 500.0 (100% accurate).
5. **No FSRS Schedule Pollution:** Mock exam attempts populate `mock_attempts` and generate feedback logs in `learning_events` without mutating raw FSRS interval state prematurely.

---

## 3. Real-World Execution Verdict

Full 125-question simulation verified via automated tests (`test_official_125_mock.py`) and browser workflows.
Result: **PASSED (100% Compliance).**
