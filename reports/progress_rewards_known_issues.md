# Progress Rewards Feature — Known Issues & Follow-Ups
**GPAT 2027 Learning OS | Phase 4 Feature 4**
**Date:** 2026-10-17

---

## 1. Documented Behaviors & Edge Cases

1. **Immediate Repetition vs Delayed Recall:**
   - **Behavior:** Retrying a question within 24 hours of an earlier attempt will advance FSRS stability and record the attempt, but will not trigger a `DELAYED_RECALL` milestone. This prevents learners from gaming recall rewards by re-attempting questions immediately after reading explanations.
   - **Status:** By design; protects pedagogical validity.

2. **Goal Boundary Synchronization:**
   - **Behavior:** Weekly goals evaluate completed study missions within the current ISO calendar week (Monday 00:00:00 UTC through Sunday 23:59:59 UTC). If a learner completes missions across midnight UTC on Sunday, the missions count toward their respective calendar weeks.
   - **Recommendation:** In an upcoming localization update, allow students to select their local timezone offset for week boundary calculation.

3. **Offline Achievement Visibility:**
   - **Behavior:** While operating strictly offline, answers and mission completions are queued in IndexedDB. Authoritative achievement awards are evaluated and returned upon synchronization with the backend via `/api/sync`. The UI displays a calm state until synced.
   - **Status:** By design; ensures server-authoritative integrity and prevents client-side forged awards.
