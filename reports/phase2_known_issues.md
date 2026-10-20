# Phase 2 — Known Issues and Quarantine Roadmap

**Date:** 2026-10-17  
**Workspace:** `C:\Users\Home\Downloads\PROJECTS\SRE_APP`  

---

## 1. Complex Layout & Layout Discontinuity Patterns

### A. Multi-Column Formatting in Pharmacy India PDFs (2020–2024)
- **Symptom:** In papers such as `GPAT_QPAK_2024.pdf`, the PDF generator rendered questions in two columns with question numbers placed in a vertical header block (`1. 11. 13. 14...`) preceding the question stems in the text stream.
- **Current Handling:** Direct sequential linear splitting works cleanly on 2026 and 2025 (`GPAT_QPAK_2026.pdf` and `GPAT_QPAK_2025.pdf`), but for 2024–2020, spatial column bounding via `pypdfium2.get_text_bounded()` is required.
- **Roadmap Resolution:** Incorporate the tested two-column bounded bounding box extractor into `PYQPipeline` prior to batch ingesting 2024–2020.

### B. Matching Questions & Sub-Tables
- **Symptom:** Questions like `pyq_gpat_2026_055` ("Match the given drugs and their major mechanism of action") contain multi-column table pairs (`1. Sumatriptan`, `2. Ketanserin`) before the multiple-choice option markers `(a), (b), (c), (d)`.
- **Current Handling:** The automated quality gate flagged `pyq_gpat_2026_055` as `MISSING_OPTION_A_MARKER` and routed it directly to `pyq_review_queue`.
- **Roadmap Resolution:** Build a specialized table-match sub-parser in `scripts/pyq_pipeline.py` that preserves column pairs in the question stem before capturing option choices.

### C. Dropped or Ambiguous Official Keys
- **Symptom:** Certain official question keys contain asterisks (e.g. `26-*` in GPAT 2024) signifying questions dropped by the examining authority, or multiple keys (e.g. `56-c & d`).
- **Current Handling:** Marked with `answer_status = 'CONFLICTING_OR_DROPPED'` and `quality_status = 'NEEDS_KEY_REVIEW'`, preventing them from being served as single-choice questions in active sessions.
- **Roadmap Resolution:** Support multiple-correct scoring or exclude dropped questions from active exam scoring.

---

## 2. Quarantined Questions List (GPAT 2026 Pilot)

| Question ID | Paper | Page | Issue | Status |
|---|---|---|---|---|
| `pyq_gpat_2026_035` | `GPAT_QPAK_2026` | 2 | `INVALID_OPTION_COUNT_6` | Quarantined in `pyq_review_queue` |
| `pyq_gpat_2026_055` | `GPAT_QPAK_2026` | 3 | `MISSING_OPTION_A_MARKER` | Quarantined in `pyq_review_queue` |
| `pyq_gpat_2026_058` | `GPAT_QPAK_2026` | 3 | `INVALID_OPTION_COUNT_12` | Quarantined in `pyq_review_queue` |
