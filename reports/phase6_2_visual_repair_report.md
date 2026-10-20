# Phase 6.2 Visual PYQ Repair Report

**Date:** 2026-10-18  
**Status:** COMPLETE (Zero Fabrication / Zero AI-Regenerated Media)  
**Database Verified:** `data/gpat_baseline.db` & `gpat_knowledge.db`  

---

## 1. Executive Summary

During Phase 5 and Phase 6.1 content audits, five critical organic chemistry and pharmaceutical analysis PYQs were identified as having lost their structural option diagrams during PDF text extraction. Without their chemical formulas and structures, these questions were pedagogically defective and impossible for students to solve.

Under the Phase 6.2 mandate, zero AI hallucination or redrawn structures were permitted. Using PyMuPDF (`fitz`), the original examination PDF source pages were inspected and harvested. Exact bounding box coordinates were tuned to eliminate stem question header bleed while capturing all option letters `(a)`, `(b)`, `(c)`, and `(d)` and structural drawings at 300 DPI.

All 5 visual plates were verified on disk, cataloged with SHA-256 fingerprints, registered into the `baseline_media` table, linked to `baseline_questions.media_id`, and confirmed serving over HTTP with `Content-Type: image/png`.

---

## 2. Recovered Visual Assets Inventory

| Question ID | Media ID | Source PDF | Page | Dimensions (W x H) | File Size | SHA-256 Fingerprint |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| `pyq_gpat_2017_084` | `med_pyq_2017_084_dienes` | `GPAT_QPAK_2017.pdf` | 5 | 1481 x 590 px | 38,643 B | `d62bf8652ac63b20ee9e5b848957e165aae79c35c4c3fce8e92a0cd82642cd12` |
| `pyq_gpat_2017_087` | `med_pyq_2017_087_bromonitrotoluene` | `GPAT_QPAK_2017.pdf` | 6 | 1341 x 217 px | 13,278 B | `789e2f95116a22ae4336a90082460a110de27ccce16c98e2c807a8e50e280734` |
| `pyq_gpat_2014_103` | `med_pyq_2014_103_barbituric` | `GPAT_QPAK_2014-2.pdf` | 5 | 1422 x 330 px | 18,094 B | `7d6921acb6dbc8a38eded7758aabd23841070542a3de93ed89b9016365893ce9` |
| `pyq_gpat_2012_116` | `med_pyq_2012_116_dimethylcyclohexane` | `GPAT_QPAK_2012-2.pdf` | 9 | 1550 x 303 px | 17,465 B | `d1d0511fcf10503e6215506d983c2e69780d708c249185c5e9ff6b8b6df14ff4` |
| `pyq_gpat_2012_117` | `med_pyq_2012_117_aromatic` | `GPAT_QPAK_2012-2.pdf` | 9 | 1445 x 165 px | 9,315 B | `e44ecd5cd2bec6dca9c589cb03f064ab7a3daac7befcd7eea8829c0e800c7f31` |

---

## 3. Question Details & Pedagogical Validity

### 3.1 GPAT 2017 Q84: Diels-Alder Diene Reactivity
- **Stem:** *"Which of the following dienes can undergo Diels-Alder reaction most readily"*
- **Defect:** Options in raw text were blank or truncated.
- **Recovered Content:** Four diene structures illustrating s-cis vs s-trans conformations:
  - (a) (2E,4E)-hexa-2,4-diene
  - (b) Cyclohexa-1,3-diene (locked in mandatory s-cis conformation, reacting most readily)
  - (c) Cyclohexa-1,4-diene (non-conjugated)
  - (d) Bicyclic locked trans diene
- **Keyed Answer:** (b) Cyclohexa-1,3-diene.

### 3.2 GPAT 2017 Q87: Nitrotoluene Bromination
- **Stem:** *"In the reaction of 2-nitrotoluene with bromine in presence of iron, which of the product shown below is the most abundant (major) product"*
- **Defect:** Raw OCR rendered scrambled letters and stray characters (`O CH O CH 3 CH O CH 3 3 Br 3 N Br N N`).
- **Recovered Content:** Four clear chemical formulas showing positions of bromine substitution relative to the ortho-directing methyl group and meta-directing nitro group:
  - 4-bromo-2-nitrotoluene (para to -CH3, major steric preference).
- **Keyed Answer:** (b) 4-bromo-2-nitrotoluene.

### 3.3 GPAT 2014 Q103: Barbituric Acid Structure
- **Stem:** *"Identify the structure of barbituric acid"*
- **Defect:** Diagram stripped during text extraction; text contained only fragments `O NH`.
- **Recovered Content:** Four pyrimidine-2,4,6-trione and related piperidinedione isomer structures.
- **Keyed Answer:** Structure showing standard pyrimidine-2,4,6(1H,3H,5H)-trione core.

### 3.4 GPAT 2012 Q116: PMR & CMR Spectra of Dimethylcyclohexane
- **Stem:** *"Both of the CMI and PMR spectra of an unknown compound show four absorption peaks each. Identify the unknown compound"*
- **Defect:** Options rendered as repetitive plain string `CH 3 CH 3 CH 3 H 3 C CH 3 CH 3`.
- **Recovered Content:** Four distinct stereoisomers and positional isomers of dimethylcyclohexane (1,1-; 1,2-; 1,3-; 1,4-dimethylcyclohexane) allowing students to count magnetically non-equivalent carbon and proton environments.
- **Keyed Answer:** (c) 1,3-dimethylcyclohexane (cis).

### 3.5 GPAT 2012 Q117: Huckel Aromaticity
- **Stem:** *"Out of the four given compounds choose the one which is aromatic"*
- **Defect:** Option labels existed without the conjugated rings.
- **Recovered Content:** Four carbocycles: naphthalene (10 pi electrons, Huckel 4n+2), cyclooctatetraene (tub conformation, non-aromatic), cycloheptatriene, and bicyclic non-aromatic isomer.
- **Keyed Answer:** (a) Naphthalene.

---

## 4. Serving & PWA Integration Verification

1. **Static Files Directory:** All recovered assets reside in `baseline/media/mcqs/`.
2. **Mount Point:** Mounted in FastAPI (`backend/main.py`) at `/media` -> `ROOT_DIR / baseline / media`.
3. **PWA Normalization:** In `backend/repositories/sqlite_study_repository.py`, `media_url` resolves to `/media/mcqs/<filename>`.
4. **Automated Verification:** Verified via `test_media_static_endpoint_serving` in `tests/test_phase6_2_visual_and_explanations.py` returning HTTP 200 and image/png payload matching byte-for-byte checksums.
