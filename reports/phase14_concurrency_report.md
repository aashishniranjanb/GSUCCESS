# Phase 14: Synthetic Real-User & Concurrency Simulation Report

**Date:** 2026-10-18  
**Tested Environment:** Local Development Staging (FastAPI on Windows, SQLite WAL mode)  
**Simulation Tooling:** ThreadPool Concurrency Runner & [`tests/load/locustfile.py`](file:///c:/Users/Home/Downloads/PROJECTS/SRE_APP/tests/load/locustfile.py)  

---

## 1. Concurrency Benchmark Results

Staged concurrency was simulated using independent synthetic learner accounts (`synth_concurrency_u{i}_*`) to ensure data isolation:

| Concurrency Tier | Virtual Learners | Total Requests | Completed Duration | Error Rate | p50 Latency | p95 Latency | p99 Latency | Lock Contention |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Tier 1 (Baseline)** | 1 user | 3 requests | 0.08s | 0.0% | 24.2ms | 35.1ms | 35.1ms | None |
| **Tier 2 (Moderate)** | 5 users | 15 requests | 0.48s | 0.0% | 105.1ms | 333.0ms | 333.0ms | None |
| **Tier 3 (Peak Study)** | 20 users | 60 requests | 1.82s | 0.0% | 160.5ms | 1,621.6ms | 1,750.4ms | None (Zero DB Lock Timeouts) |

---

## 2. Cross-User Data Isolation Findings

1. **Memory Isolation:** Answers submitted by one virtual user never contaminated the FSRS cards, misconception traps, or session items of any other user.
2. **Weekly Goal Integrity:** Weekly targets and completed mission counts remained isolated per `student_id`.
3. **Database Concurrency Invariant:** SQLite WAL mode handled concurrent write transactions (attempt recording + learning event logging) cleanly with zero `sqlite3.OperationalError: database is locked` exceptions.
