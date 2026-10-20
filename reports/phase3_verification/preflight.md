# Phase 3 Preflight Integrity & Environmental Audit

**Generated:** 2026-10-17T01:33:30+05:30  
**Repository Working Directory:** `c:\Users\Home\Downloads\PROJECTS\SRE_APP`  
**Python Runtime:** Python 3.14.0 (Windows NT 10.0 x64) in `.venv`

---

## 1. Database PRAGMA Integrity & Provenance

### A. Learner Database (`gpat_knowledge.db`)
- **PRAGMA integrity_check:** `ok`
- **PRAGMA foreign_key_check:** `[]` (0 foreign key violations)
- **Learner Records Preserved:**
  - `student_attempts`: **7**
  - `fsrs_cards`: **11**
  - `learning_events`: **10**
  - `study_sessions`: **3**
  - `synced_client_events`: **3**

### B. Static Baseline Database (`data/gpat_baseline.db`)
- **PRAGMA integrity_check:** `ok`
- **PRAGMA foreign_key_check:** `[]` (0 foreign key violations)
- **Baseline Corpus Counts:**
  - `baseline_questions`: **229**
  - `baseline_chunks`: **505** (embeddings dimensionality: 384)
  - `baseline_topics`: **221**
  - `pyq_review_queue`: **3** quarantined items with review reasons

---

## 2. Open-Source Verification Tooling Manifest

| Tool | Version | Role in Verification Stack | Status |
|---|---|---|---|
| **pytest** | `9.1.1` | Core test runner & regression suite | Active |
| **pytest-cov** | `7.1.0` | Line and branch coverage analysis | Active (Coverage JSON exported) |
| **hypothesis** | `6.170.1` | Property-based invariant testing (bounds, diversity, idempotency) | Active |
| **schemathesis** | `4.31.1` | OpenAPI conformance & endpoint property testing | Active |
| **playwright** | `1.64.0` | Headless Chromium browser & offline PWA network emulation | Active (v1248 installed) |
