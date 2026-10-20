# Phase 4 Known Issues, Limitations & Deferred Items

**Project:** GPAT 2027 AI Learning OS / PWA  
**Workspace:** `C:\Users\Home\Downloads\PROJECTS\SRE_APP`  
**Phase:** Phase 4  
**Date:** 2026-10-17  

---

## 1. Resolved Issues During Phase 4
1. **Empty Candidate Pool Crash in Specialized Session Modes:**  
   *Problem:* When generating sessions with strict filters (e.g. `TARGETED_REPAIR` only) for students with zero misconceptions, the generator raised an unhandled `IndexError` or produced empty candidate lists.  
   *Resolution:* Implemented fallback to available syllabus topics or standard due review in [`learner_engine.py`](file:///c:/Users/Home/Downloads/PROJECTS/SRE_APP/learner_engine.py).

2. **IndexedDB Event Result Access Error:**  
   *Problem:* In Chromium browser sessions, accessing `event.target.result` directly caused occasional unhandled exceptions if the transaction event signature varied.  
   *Resolution:* Safe access via `req.result || (e && e.target && e.target.result)` in [`frontend/public/index.html`](file:///c:/Users/Home/Downloads/PROJECTS/SRE_APP/frontend/public/index.html).

3. **Global `user-select: none` Usability Defect:**  
   *Problem:* Mobile styles disabled user text selection globally, preventing learners from copying or selecting textbook references and pharmacological citations.  
   *Resolution:* Removed global `user-select: none`, allowing standard text selection across question stems and feedback panels.

4. **Test Database Contamination Guard:**  
   *Problem:* Early test scripts executed directly against `gpat_knowledge.db`.  
   *Resolution:* All automated tests and persona evaluations now create isolated temporary database clones using `tempfile.NamedTemporaryFile`, guaranteeing zero data loss or test residue in the production database.

---

## 2. Deferred & Future Enhancements (Phase 5+)
1. **Interactive Drug Structure Diagrams:**  
   Currently, chemistry structures are provided via static textbook figures and SVGs. Interactive MolView / SMILES rendering can be integrated in future phases for medicinal chemistry synthesis pathways.
2. **Push Notifications for Scheduled Study Times:**  
   Web Push API service worker subscription endpoints are scaffolded in `sw.js` but will require backend VAPID key configuration and user opt-in prompt design that strictly complies with the anti-urgency policy (never sending late-night or guilt-inducing notifications).
3. **Multi-device Sync Backend:**  
   Currently, IndexedDB syncs with the local FastAPI backend instance. For multi-device cloud synchronization, JWT-based user authentication and remote session handshakes will be introduced in subsequent production deployments.
