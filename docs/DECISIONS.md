# GPAT Learning OS — Architectural Decision Records (ADR)

**Version:** 1.0.0  
**Status:** Approved  
**Last Updated:** 2026-10-20  

This document logs significant architectural decisions made during the design and evolution of GPAT Learning OS.

---

## ADR-001: Tri-Database SQLite Separation

### Context
Educational apps frequently mix dynamic student telemetry with static syllabus content, causing database bloat, backup overhead, and data corruption during content updates.

### Decision
Segregate persistence into three physically distinct SQLite databases:
1. `gpat_knowledge.db` — Dynamic learner state (attempts, FSRS memory cards, session items, rewards).
2. `data/gpat_baseline.db` — Frozen baseline content, syllabus taxonomy, vector embeddings, and verified PYQs.
3. `data/pyq_topic_staging.db` — Editorial review and staging sandbox.

### Consequences
- **Positive:** Zero risk of content updates wiping student history. Backups of learner progress remain lightweight.
- **Negative:** Cross-database joins require attaching databases or handling joins at the application layer.

---

## ADR-002: Adoption of FSRS 4.5 over SuperMemo SM-2

### Context
Legacy spaced repetition algorithms (such as SM-2 / Anki default) rely on rigid heuristics that fail to adapt well to complex multiple-choice pharmacy question sets and punish students harshly for missed days.

### Decision
Implement the Free Spaced Repetition Scheduler (FSRS 4.5), which calculates memory stability ($S$) and difficulty ($D$) using scientifically fitted power-law forgetting curves.

### Consequences
- **Positive:** More accurate interval prediction; flexible scheduling; avoids the "review tsunami" after a missed study day.
- **Negative:** Requires slightly more complex state tracking (stability, difficulty, elapsed days) per card.

---

## ADR-003: Prohibition of Synthetic Questions in Baseline

### Context
LLM hallucinations in pharmacy pharmacology and dosage calculations pose direct learning hazards for competitive GPAT aspirants.

### Decision
Strictly forbid synthetic or AI-generated questions in `data/gpat_baseline.db`. Only authentic questions sourced from official GPAT past papers (2010–2025) and verified question banks are permitted.

### Consequences
- **Positive:** Uncompromised clinical and academic accuracy.
- **Negative:** Slower content expansion requiring manual editorial review for new question batches.

---

## ADR-004: Next.js App Router with Tailwind CSS for Mobile-First Delivery

### Context
A mobile-first web app accessible on any mobile browser reduces install friction compared to requiring a native Android/iOS app store download during initial pilot testing.

### Decision
Build the learner frontend using Next.js 16 (App Router), React 19, TypeScript, and Tailwind CSS, styled with custom design tokens inspired by Duolingo and Swiggy.

### Consequences
- **Positive:** Fast development velocity, instant client routing, offline PWA capabilities, responsive mobile layouts.
- **Negative:** Must carefully manage safe-area insets and viewport scrolling across disparate mobile browsers.

---

## ADR-005: Idempotent Batch Synchronization Protocol

### Context
Learners frequently study in low-connectivity environments (trains, libraries, hostels). Network dropouts during attempt submission can produce duplicated attempts or lost progress.

### Decision
Equip each client event with a client-generated UUID (`client_event_id`). The server sync handler checks this ID before committing writes, ensuring identical payloads can be replayed safely without creating duplicate attempt records.

### Consequences
- **Positive:** Robust offline resilience and zero data loss.
- **Negative:** Client must maintain a persistent local queue until server confirmation is received.
