# Phase 5: Known Issues & Editorial Review Backlog

**Date:** 2026-10-17  
**Scope:** Content integrity, visual chemical structures, syllabus mapping granularity, and explanation grounding.

---

## 1. Visual Options in Chemical Questions (Gate 1 Backlog)

Five questions in `data/gpat_baseline.db` exhibit visual chemical diagrams that were stripped during standard text extraction, resulting in empty option strings:
1. `pyq_gpat_2017_084` (Diels-Alder diene skeletal structures)
2. `pyq_gpat_2017_087` (Bromination reaction products)
3. `pyq_gpat_2014_103` (Barbituric acid isomers)
4. `pyq_gpat_2012_116` (Spectroscopic CMI/PMR molecular structures)
5. `pyq_gpat_2012_117` (Aromatic ring structures)

**Recommended Resolution:**
- Extract cropped PNG bounding boxes from the respective PDF source pages using PyMuPDF / pypdfium2.
- Stage in `baseline_media` and link via `media_id` or LaTeX/SMILES representation.
- In the interim, keep these items quarantined from runtime mock pools to prevent user confusion.

---

## 2. Topic Mapping Fallback for Bulk PYQs (Gate 2 Backlog)

- 48 hand-crafted diagnostic items have rich, granular concept and topic associations across autonomic pharmacology, cardiovascular agents, and neuropharmacology.
- 2,015 ingested PYQs are currently associated with the fallback category `pharmacology__pk_absorption`.
- **Policy Standard:** The system displays `UNMAPPED_PYQ` rather than fabricating inaccurate subject-matter classifications until keyword/ontology classification is applied.

---

## 3. Explanations for Ingested PYQs (Gate 3 Backlog)

- Ingested PYQs from 2010–2026 carry official AICTE/NTA final answer keys and examination page provenance, but do not possess textbook citations.
- In strict adherence to our zero-fabrication policy, no LLM hallucinations or fabricated book page numbers were inserted.
- Explanations are marked as `OFFICIAL_KEY_ONLY / EXPLANATION_PENDING_REVIEW` in learner review screens until authoritative textbook citations are added.
