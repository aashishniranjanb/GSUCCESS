# Phase 14: Known Issues & Pilot Limitations

**Date:** 2026-10-18  
**Scope:** Controlled Pilot (Phase 15 Readiness)  

---

## 1. Managed Pilot Limitations

1. **Staged Topic Mappings:**
   - The 137 high-confidence candidate topic mappings remain safely staged in `data/pyq_topic_staging.db`. Legacy unclassified questions safely display fallback labels in practice sessions until administrative promotion is approved.
2. **Quarantined OCR Items (89 Questions):**
   - 89 questions with damaged OCR or missing option tags remain quarantined in `pyq_review_queue` and are strictly excluded from learner sessions.
3. **Local In-Process Concurrency Limit:**
   - Under single-process SQLite WAL mode, p95 response time reaches 1.6s at 20 simultaneous concurrent virtual users. This throughput is ideal for pilot cohorts ($< 100$ learners). If scaling beyond 500 concurrent active writers, evaluate PostgreSQL or external connection pooling.
