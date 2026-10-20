# GPAT Learning OS — Next-Phase Implementation Brief: Phase 5B

**Phase:** Phase 5B — Syllabus Explorer & Topic Workspace  
**Document Date:** 2026-10-19  
**Status:** READY FOR IMPLEMENTATION (PENDING USER APPROVAL)  
**Governing Specification:** [`BEST_GPAT_UX.md`](file:///c:/Users/Home/Downloads/PROJECTS/SRE_APP/BEST_GPAT_UX.md) (Section 6.2 & 6.3)  
**Target Route:** `/study` and `/study?topic={topicId}`  
**Project Directory:** `c:\Users\Home\Downloads\PROJECTS\SRE_APP\web`

---

## 1. Selected Phase & Architectural Rationale

### **Recommendation: Phase 5B — Syllabus Explorer & Topic Workspace**

### Why Phase 5B Must Precede Phase 5C & 5D:
1. **The Core User Problem:**  
   The GPAT syllabus contains **221 topics across 19 PCI curriculum subjects and 5 NBEMS exam disciplines**. Currently, `/study` displays a raw expandable tree with basic text chunks, but:
   - Learners cannot filter topics by their actual learning status (*Not Assessed*, *Learning*, *Needs Repair*, *Provisional Mastery*).
   - Learners cannot see verified eligible question availability per topic before committing to study.
   - Topics lack an actionable "Study this topic" or "Add to today's plan" bridge into the Daily Home screen.
2. **Structural Dependency for Mini Mocks:**  
   The requested **Mini Mock Builder (Phase 5D)** requires learners to select units they have studied. Without a structured, domain-coded syllabus taxonomy that clearly indexes units and question eligibility, the mock builder would have no clean data model to query or display.
3. **Preserving Trust Before Breadth:**  
   Phase 5B establishes clear badges for verified baseline mappings vs. unverified/staged mappings, ensuring learners never mistake draft curriculum notes for authoritative textbook citations.

---

## 2. Scope & Key Deliverables

1. **Enhanced Syllabus Navigation (`/study`):**
   - Clean, searchable 4-tier hierarchy: **Exam Subject &rarr; Curriculum Subject &rarr; Unit/Chapter &rarr; Topic**.
   - Uniform application of the 5 subject monochromatic theme tokens established in Phase 5A ([`web/src/lib/colors.ts`](file:///c:/Users/Home/Downloads/PROJECTS/SRE_APP/web/src/lib/colors.ts)).
   - Multi-facet status filter pills:
     - **All Topics**
     - **Not Assessed** (0 recorded attempts in SQLite)
     - **Needs Repair** (Active misconceptions or <60% accuracy)
     - **Provisional Mastery** (&ge;3 attempts, &ge;80% accuracy, stability &ge;7 days)
2. **Comprehensive Topic Workspace (`TopicDetailPanel`):**
   - Answers the learner's four essential questions:
     1. *What should I learn?* &rarr; Bloom's Level 5 Learning Objectives & Clinical Pearls.
     2. *Which resource comes first?* &rarr; Linked reference textbook excerpts with page citations and provenance.
     3. *Can I practise it?* &rarr; Breakdown of available questions (PYQs vs. Practice Items).
     4. *How will I know I understand it?* &rarr; Topic diagnostic state and direct **"Add to Study Plan"** button (syncing to `gpat_learner_study_plan_v1`).
3. **Pre-Assessment Availability Counter:**
   - Clearly states how many eligible questions exist in each unit/topic so learners can gauge whether enough material exists for a unit check.

---

## 3. Data Contracts & Existing Backend APIs to Reuse

The implementation will strictly consume existing FastAPI endpoints without creating database migrations or synthetic state stores:

| Endpoint | Method | Purpose in Phase 5B |
|---|---|---|
| `/api/syllabus/tree` | `GET` | Returns 5 exam groups, 19 curriculum subjects, 221 topics, and question counts. |
| `/api/syllabus/topic/{topic_id}` | `GET` | Returns full topic metadata, textbook chunks, learning objectives, flashcards, and verified questions. |
| `/api/progress?student_id={id}` | `GET` | Supplies concept memory state and mastery transitions to badge topics as *Not Assessed*, *Needs Repair*, or *Provisional Mastery*. |

---

## 4. UX States & Quality Requirements

- **Loading State:** Skeleton cards for both the syllabus sidebar and topic detail panel.
- **Empty State:** Honest fallback when search queries yield zero matching topics or when a newly added topic has no reference excerpts.
- **Error & Offline State:** Graceful error banner with retry action; cached tree browsing when offline.
- **Responsive Layout:**
  - **Mobile (<768px):** Clean list of subjects/units. Selecting a topic opens a focused full-screen detail view with a back button.
  - **Desktop (&ge;768px):** Two-pane layout: sticky searchable syllabus tree on the left (w-80), expansive topic workspace on the right.
- **Accessibility:** Full keyboard arrow navigation across tree nodes, visible focus outlines, WCAG 2.2 AA contrast compliance.

---

## 5. Explicit Out-of-Scope Constraints for Phase 5B

- Do NOT implement the multi-question mock exam builder (deferred to Phase 5D).
- Do NOT rewrite or modify backend SQLite database tables.
- Do NOT promote draft syllabus staging mappings to published tables.
- Do NOT alter Supabase authentication settings.

---

## 6. Acceptance Criteria for Phase 5B Release Gate

1. Learner can search across all 221 topics by title, keyword, or PCI course code.
2. Learner can filter topics by mastery state (*Not Assessed*, *Needs Repair*, *Mastered*) computed from real SQLite records.
3. Every topic displays its verified question count split by PYQ vs. standard practice.
4. Clicking "Add to Study Plan" seamlessly appends the topic to the Daily Home screen plan queue.
5. `npm run lint` and `npx tsc --noEmit` pass with **0 errors and 0 warnings**.
6. `npm run build` compiles cleanly.
7. Existing learner database fingerprints remain completely untouched.
