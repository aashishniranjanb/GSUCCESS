# Phase 15: Baseline Metrics & Operational Standards

**Date:** 2026-10-18  
**Scope:** Pre-pilot system baseline measurements and target operational thresholds

---

## 1. Pre-Pilot System Baseline Measurements

The following baseline metrics reflect the verified state of the system prior to enrolling any external pilot learners:

| Measurement Category | Baseline Metric | Observed Value | Verification Source |
| :--- | :--- | :---: | :--- |
| **Question Bank Scale** | Total verified baseline questions | **2,063** | `data/gpat_baseline.db` (`baseline_questions`) |
| **Quarantined OCR Items** | Damaged / incomplete questions | **89** | `data/gpat_baseline.db` (`pyq_review_queue`) |
| **Visual Media Provenance** | Authentic plate images served | **7 records / 5 plates** | `baseline/media/` (SHA-256 verified) |
| **Protected Learner State** | Historical student attempt records | **7** | `gpat_knowledge.db` (`student_attempts`) |
| **FSRS Card Stability** | Spaced repetition cards tracked | **11** | `gpat_knowledge.db` (`fsrs_cards`) |
| **Learner Milestones** | Initial unlocked achievements | **4** | `gpat_knowledge.db` (`learner_achievements`) |
| **Test Suite Pass Rate** | Automated regression pass rate | **100% (107/107)** | `pytest tests/` |
| **5-User Concurrency Latency** | Median response latency | **151.7 ms** | `scripts/run_concurrency_benchmark.py` |
| **20-User Concurrency Latency**| p95 response latency | **1,621.6 ms** | `scripts/run_concurrency_benchmark.py` |
| **Concurrent Error Rate** | Request failure rate under load | **0.00%** | Zero 5xx errors recorded |

---

## 2. Operational Thresholds for Controlled Pilot

The controlled pilot will monitor the following operational and learning indicators against target performance bands:

| Operational Indicator | Target Standard | Circuit Breaker (Immediate Pause) |
| :--- | :---: | :---: |
| **Cohort Size** | $5 \le N \le 10$ learners | $> 10$ learners attempted |
| **API Error Rate (5xx)** | $< 0.1\%$ | $\ge 1.0\%$ over 50 consecutive requests |
| **Median Response Latency (p50)** | $< 250\text{ ms}$ | $> 1,000\text{ ms}$ sustained for 10 minutes |
| **Tail Response Latency (p95)** | $< 1,500\text{ ms}$ | $> 3,000\text{ ms}$ sustained for 10 minutes |
| **Daily Mission Completion Rate** | $\ge 70\%$ | $< 30\%$ completion |
| **Offline Sync Success Rate** | $\ge 99\%$ | $< 95\%$ |
| **Duplicate Sync Rejections** | 100% deduplicated | Any duplicate count recorded in attempts |
| **Cross-User Isolation** | Zero cross-talk | Any unauthorized user state returned |
| **Verified Answer Key Errors** | Zero errors | $\ge 2$ confirmed answer key errors |

---

## 3. Learning Evaluation Framework

To evaluate whether the adaptive learning OS aids knowledge consolidation without making invalid causal claims:

1. **Baseline Assessment:**
   - 25-question sprint diagnostic at Day 0 (`GPAT_PROVISIONAL_MOCK_25`).
   - Mean baseline accuracy and confidence-accuracy calibration recorded.
2. **Delayed Assessment:**
   - Matched 25-question test at Day 5–7 containing concept variants of studied items.
3. **Descriptive Reporting Standard:**
   - Report changes as descriptive percent delta ($\Delta \text{accuracy}$) alongside confidence intervals.
   - Do not claim statistical causality given the small pilot sample size ($N \le 10$).
