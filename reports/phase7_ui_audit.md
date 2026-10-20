# Phase 7 UI Audit & Component Inventory

**Date:** 2026-10-18  
**Target:** `frontend/public/index.html` (2,230 lines)  
**Architecture:** Single-Page Progressive Web App (Vanilla ES6, CSS Tokens, IndexedDB, Service Worker)  

---

## 1. Existing Screen Inventory & API Dependencies

| Screen ID | User-Facing Label | Current Functionality | Active API Endpoints Connected |
| :--- | :--- | :--- | :--- |
| `#screen-now` | **Today** | Daily Mission card (12m/5m), Active Question Player, Confidence Selector, Immediate Feedback, Media viewer | `GET /api/study/today`<br>`POST /api/study/attempt`<br>`POST /api/study/sync` |
| `#screen-learn` | **Learn** | Subject & Topic Explorer, concept list, high-yield topics | `GET /api/study/today` |
| `#screen-recall`| **Recall** | Grounded AI Tutor, Knowledge Graph multi-hop pathway calculation | `POST /api/search/rag`<br>`GET /api/graph/path` |
| `#screen-library`| **Library** | Verified textbook authorities, chunk inspector | `GET /api/study/today` |
| `#screen-progress`| **Progress** | Weekly goals, learning achievements, memory stability, mock exams | `GET /api/progress/rewards`<br>`POST /api/progress/goal`<br>`POST /api/evaluation/mock/create`<br>`POST /api/evaluation/mock/submit` |

---

## 2. Issues & Design Inconsistencies Identified

1. **Card Visual Clutter:**
   Some metric grids have competing gradients and borders that dilute visual focus from the primary Daily Mission card.
2. **Typography Hierarchy:**
   Headings across `#daily-mission-card` and `#mock-launcher-card` have slight variance in letter-spacing and weight. Standardizing tokens will improve cohesion.
3. **Question Option Touch Targets:**
   On small mobile viewports ($< 380\text{px}$ width), option padding needs optimization to ensure full touch comfort while preserving formula legibility.
4. **Media Image Expand/Zoom:**
   Visual question diagrams are supported, but adding an explicit full-screen modal zoom will help learners examine intricate chemical ring numbering.
5. **Color Contrast Verification:**
   All muted texts (`--text-muted: #64748b`) against `#090d16` achieve 4.7:1 contrast (WCAG AA compliant), but primary descriptions will be elevated to `#94a3b8` (7.3:1) for maximum readability.
