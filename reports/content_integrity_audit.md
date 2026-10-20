# Gate 1: Question Content Integrity Audit

**Date:** 2026-10-17  
**Audited Target:** `data/gpat_baseline.db` (`baseline_questions`)  
**Total Questions Audited:** 2,063  
**Findings Catalog:** [`reports/content_integrity_findings.csv`](file:///c:/Users/Home/Downloads/PROJECTS/SRE_APP/reports/content_integrity_findings.csv)

---

## 1. Executive Summary

An independent, automated structural and provenance audit was executed across all 2,063 published questions in the baseline question bank:
- **Clean Structural Validity:** 2,050 / 2,063 questions (99.37%) possess complete question stems, exactly 4 non-empty options, a valid key index ($0 \le k \le 3$), and intact provenance.
- **Identified Integrity Findings:** 13 questions exhibited specific anomalies requiring quarantine or content repair:
  - **Empty Option / Diagrammatic Structure Loss (5 items):** `pyq_gpat_2017_084`, `pyq_gpat_2017_087`, `pyq_gpat_2014_103`, `pyq_gpat_2012_116`, `pyq_gpat_2012_117` contain visual chemical structure choices that were rendered as empty options during text-only PDF extraction.
  - **Short/Incomplete Stem (2 items):** `pyq_gpat_2022_092` ("Heme is") and `pyq_gpat_2015_071` ("Taxol is") contain concise telegraphic stems that need verification against the original PDF layout.
  - **Inter-Year Repetition / Duplicate Stems (6 items):** E.g. `pyq_gpat_2014_036` and `pyq_gpat_2016_037` ("The stability and shelf life of a suspension determined by"), `pyq_gpat_2011_042` and `pyq_gpat_2016_033`. These represent authentic historical re-appearances of questions across different GPAT exam years, but share normalized stem hashes.

---

## 2. Integrity Findings Detail

| Question ID | Year & Q# | Issue Detected | Details & Root Cause |
|---|---|---|---|
| `pyq_gpat_2017_084` | 2017 Q84 | `EMPTY_OPTION_FOUND` | Visual diene structures in options; text extraction yielded blank option strings. |
| `pyq_gpat_2017_087` | 2017 Q87 | `EMPTY_OPTION_FOUND` | Chemical reaction schemes with missing image/formula blocks. |
| `pyq_gpat_2014_103` | 2014 Q103 | `EMPTY_OPTION_FOUND` | Barbituric acid isomer structures missing visual raster block. |
| `pyq_gpat_2012_116` | 2012 Q116 | `EMPTY_OPTION_FOUND` | CMI/PMR spectral formula options omitted during text stripping. |
| `pyq_gpat_2012_117` | 2012 Q117 | `EMPTY_OPTION_FOUND` | Aromatic compound skeletal structures missing. |
| `pyq_gpat_2022_092` | 2022 Q92 | `STEM_TOO_SHORT` | Ultra-concise stem ("Heme is"). Needs check against full bounding box. |
| `pyq_gpat_2015_071` | 2015 Q71 | `STEM_TOO_SHORT` | Ultra-concise stem ("Taxol is"). |

---

## 3. Prioritized Quarantine Action

1. **Immediate Quarantine Action:** The 5 questions with missing chemical structures (`EMPTY_OPTION_FOUND`) must be staged in `pyq_review_queue` with issue `MISSING_VISUAL_OPTIONS` rather than served in mock exams where candidates see blank options.
2. **Preservation Principle:** Published questions in `data/gpat_baseline.db` remain untouched until editorial approval or OCR/diagram ingestion is completed.
