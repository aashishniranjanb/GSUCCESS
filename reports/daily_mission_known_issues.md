# Daily Mission Feature — Known Issues & Follow-Ups
**GPAT 2027 Learning OS | Phase 4**
**Date:** 2026-10-17

---

## 1. Known Behaviors & Edge Cases Documented

1. **Mid-Session Duration Adjustments:**
   - **Behavior:** The toggle to 5 minutes is only permitted if 0 questions in today's mission have been answered. Once a mission is started (`answered_count > 0`), the UI hides or disables the duration toggle to protect session consistency and avoid dropping questions midway through an active recall sequence.
   - **Recommendation:** Keep this constraint active as it protects retrieval momentum and data consistency.

2. **Offline Mode Switch:**
   - **Behavior:** When completely offline without network access, the PWA retrieves today's session from IndexedDB. If the learner switches duration while offline, the IndexedDB cache retains the previously downloaded session unless the student has previously cached both durations.
   - **Recommendation:** In an upcoming Phase 4 subtask, pre-cache both the 12m and 5m variations during initial online synchronization.

3. **Unicode Arrow Formatting in Windows Shells:**
   - **Behavior:** The primary button uses a Unicode right arrow (`→` / `\u2192`). In Windows consoles running legacy code pages (e.g. `cp1252`), direct stdout printing of button text without decoding can trigger an encoding exception.
   - **Resolution:** Python tests now safely parse button text or sanitize output. The HTML entity and browser rendering remain intact and visually clean.
