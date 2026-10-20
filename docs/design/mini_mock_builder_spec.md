# Phase 5D: Personalized Mini Mock Builder Specification

## 1. Overview & Purpose
The Personalized Mini Mock Builder enables GPAT aspirants to configure, inspect, and practice targeted mock examinations derived from their specific study progress (subjects, units, and high-yield concepts). This removes the cognitive overhead and discouragement of facing 125-question full-syllabus simulations prematurely, while strictly maintaining official NBEMS exam standards (+4 for correct, -1 for incorrect, 0 for unattempted) and zero synthetic or deceptive scoring.

## 2. Core Principles & Non-Negotiables
1. **Server-Authoritative Lifecycle:**
   - Timing, session states, deterministic question sequences, and scoring are managed exclusively by the FastAPI backend (`MockExamEngine`, `MockScorer`).
   - The browser never scores answers or predicts performance.
2. **Deterministic Round-Robin Allocation:**
   - Candidate questions are partitioned by concept/domain to prevent topic monopoly.
   - Questions are distributed evenly across learner-selected topics until the target paper size is satisfied.
3. **Transparent Audit & Zero Fabricated Questions:**
   - Real-time pre-flight coverage audits (`POST /api/mock/mini-mock-coverage`) inspect the active database for eligible, non-quarantined questions.
   - If selected topics contain fewer eligible questions than the requested size (e.g., requesting 50 questions when only 12 exist), the system displays an explicit shortfall notice. It never hallucinates filler questions or quietly shrinks the exam without transparency.
4. **Preservation of Official Simulations:**
   - The standard 125-question / 180-minute official GPAT simulation remains completely intact and undisturbed.
   - Mini mocks are explicitly branded as targeted diagnostics. The UI never falsely claims that a high score on a 15-question mini mock equates to official GPAT qualification.

## 3. Architecture & Data Flow

```mermaid
flowchart TD
    UI[Next.js Mini Mock Builder Modal] -->|1. Select Scope: Subjects/Topics| CovAPI["POST /api/mock/mini-mock-coverage"]
    CovAPI -->|2. Return Counts & Warnings| UI
    UI -->|3. Configure: Preset (15/25/50/custom) + Title| CreateAPI["POST /api/mock/create (blueprint_type='mini_mock')"]
    CreateAPI --> Engine["MockExamEngine.create_mock_exam(custom_blueprint)"]
    Engine -->|4. Round-Robin Allocation & DB Write| DB[(gpat_knowledge.db)]
    CreateAPI -->|5. Return Mock Session Info| UI
    UI --> Player["/mocks/[id] (Authoritative Mock Player)"]
    Player --> Scorer["MockScorer.submit_and_score()"]
```

## 4. API Contracts

### A. Coverage Audit Endpoint
- **Route:** `POST /api/mock/mini-mock-coverage`
- **Request Body:**
  ```json
  {
    "topic_ids": ["pharmacology_ans", "pharmaceutics_tablets"],
    "subject_ids": ["pharmacology"],
    "desired_question_count": 25
  }
  ```
- **Response:**
  ```json
  {
    "total_eligible_questions": 34,
    "concepts_covered": 8,
    "concept_breakdown": [
      { "concept_id": "pharmacology_ans", "concept_name": "Autonomic Nervous System", "domain_id": "pharmacology", "question_count": 14 }
    ],
    "domains_covered": [
      { "domain_id": "pharmacology", "domain_name": "Pharmacology", "question_count": 28, "concept_count": 6 }
    ],
    "sufficient_questions": true,
    "shortfall": 0,
    "warning": null,
    "available_domains": [...],
    "available_concepts": [...]
  }
  ```

### B. Mock Creation Endpoint
- **Route:** `POST /api/mock/create`
- **Request Body:**
  ```json
  {
    "learner_id": "student_01",
    "blueprint_type": "mini_mock",
    "custom_title": "ANS & Tablet Technology Sprint",
    "question_count": 25,
    "duration_minutes": 45,
    "topic_ids": ["pharmacology_ans"],
    "subject_ids": ["pharmaceutics"]
  }
  ```
- **Response:** Standard `MockExamResponse` with `exam_id`, deterministic `items`, `duration_minutes`, and `state="in_progress"`.

## 5. UI/UX Interaction Design
- **Step 1: Scope Selection:** Filterable hierarchy displaying subject domains and specific concepts with live question counts. Clear indicators show how many questions are currently available.
- **Step 2: Paper Size & Timing:** Preset cards (15 Qs / 25 Min, 25 Qs / 45 Min, 50 Qs / 90 Min, or Custom). Live warning badges inform the learner if the selected pool has fewer questions than the target size.
- **Step 3: Allocation Review:** Live breakdown displaying exact concept distribution, negative marking rules (+4 / -1), and transparent confirmation before launching.
