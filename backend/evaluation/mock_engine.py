"""
Mock Exam Engine for GPAT 2027.

Features:
- Initializes `mock_exams`, `mock_exam_items`, `mock_attempts` schema
- State Machine: CREATED -> READY -> STARTED -> IN_PROGRESS -> PAUSED -> SUBMITTED -> EVALUATED
- Server-authoritative timer: remaining_sec = duration_sec - elapsed_sec
- Controlled question selection: fixed blueprint, no adaptive bias, exposure windows, no duplicates
- Resumes cleanly after browser crash / refresh
- Integrates MockScorer for comprehensive diagnostics
- Feeds back into LearnerEngine by creating learning events without contaminating FSRS raw ratings
"""

import sqlite3
import json
import uuid
import datetime
from datetime import timezone
from typing import Dict, Any, List, Optional
from pathlib import Path

from backend.evaluation.mock_blueprint import MockBlueprint, BLUEPRINTS
from backend.evaluation.mock_scorer import MockScorer

DB_PATH = Path(__file__).resolve().parent.parent.parent / "gpat_knowledge.db"

class MockExamEngine:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = str(db_path)
        self._init_tables()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_tables(self):
        conn = self._get_connection()
        cur = conn.cursor()

        # 1. mock_exams table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS mock_exams (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            exam_version TEXT NOT NULL, -- PROVISIONAL_MOCK vs OFFICIAL_EXAM_SIMULATION
            title TEXT NOT NULL,
            blueprint_name TEXT NOT NULL,
            duration_seconds INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            marks_per_question REAL NOT NULL,
            negative_marks REAL NOT NULL,
            status TEXT NOT NULL, -- CREATED, READY, STARTED, IN_PROGRESS, PAUSED, SUBMITTED, EVALUATED
            started_at TIMESTAMP,
            paused_at TIMESTAMP,
            resumed_at TIMESTAMP,
            elapsed_seconds INTEGER DEFAULT 0,
            submitted_at TIMESTAMP,
            evaluated_at TIMESTAMP,
            score REAL,
            score_percent REAL,
            accuracy_percent REAL,
            config_json TEXT NOT NULL,
            result_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 2. mock_exam_items table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS mock_exam_items (
            id TEXT PRIMARY KEY,
            exam_id TEXT NOT NULL,
            question_id TEXT NOT NULL,
            position INTEGER NOT NULL,
            domain_id TEXT,
            concept_id TEXT,
            question_type TEXT,
            difficulty INTEGER,
            marks REAL NOT NULL,
            negative_marks REAL NOT NULL,
            FOREIGN KEY (exam_id) REFERENCES mock_exams(id),
            FOREIGN KEY (question_id) REFERENCES questions(id)
        );
        """)

        # 3. mock_attempts table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS mock_attempts (
            id TEXT PRIMARY KEY,
            exam_id TEXT NOT NULL,
            question_id TEXT NOT NULL,
            selected_option INTEGER,
            is_correct INTEGER,
            time_spent_ms REAL DEFAULT 0,
            confidence INTEGER DEFAULT 3,
            answered_at TIMESTAMP,
            FOREIGN KEY (exam_id) REFERENCES mock_exams(id),
            FOREIGN KEY (question_id) REFERENCES questions(id),
            UNIQUE(exam_id, question_id)
        );
        """)

        conn.commit()
        conn.close()

    def create_mock_exam(
        self,
        user_id: str,
        blueprint_name: str = "sprint_25",
        custom_blueprint: Optional[MockBlueprint] = None
    ) -> Dict[str, Any]:
        """
        Creates a new Mock Exam session adhering to the blueprint constraints.
        Supports official simulations, provisional mocks, and personalized mini mocks.
        Does NOT use adaptive scheduler so question selection remains uniform and unskewed.
        """
        blueprint = custom_blueprint or BLUEPRINTS.get(blueprint_name, BLUEPRINTS["default"])
        conn = self._get_connection()
        cur = conn.cursor()

        # Check exposure window: questions attempted in last N days
        now_dt = datetime.datetime.now(timezone.utc)
        avoid_date = (now_dt - datetime.timedelta(days=blueprint.exposure_avoid_last_n_days)).isoformat()

        cur.execute("""
        SELECT DISTINCT question_id FROM student_attempts
        WHERE student_id = ? AND created_at >= ?
        """, (user_id, avoid_date))
        recently_exposed = {r["question_id"] for r in cur.fetchall()}

        # Fetch candidate questions (optionally filtering by selected concepts/topics or subjects/domains)
        query = """
        SELECT q.id, q.concept_id, q.question_type, q.difficulty, q.source_page,
               c.name as concept_name, c.domain_id
        FROM questions q
        JOIN concepts c ON q.concept_id = c.id
        """
        params: List[Any] = []
        conditions = []

        if blueprint.selected_topic_ids:
            placeholders = ",".join("?" for _ in blueprint.selected_topic_ids)
            conditions.append(f"(q.concept_id IN ({placeholders}) OR c.domain_id IN ({placeholders}))")
            params.extend(blueprint.selected_topic_ids)
            params.extend(blueprint.selected_topic_ids)

        if blueprint.selected_subject_ids:
            placeholders = ",".join("?" for _ in blueprint.selected_subject_ids)
            conditions.append(f"c.domain_id IN ({placeholders})")
            params.extend(blueprint.selected_subject_ids)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY q.id ASC"
        cur.execute(query, tuple(params))
        all_questions = [dict(r) for r in cur.fetchall()]

        if not all_questions:
            conn.close()
            raise ValueError("No eligible questions found for the selected topics and criteria.")

        # Filter out recently exposed if sufficient pool exists
        unexposed_pool = [q for q in all_questions if q["id"] not in recently_exposed]
        candidate_pool = unexposed_pool if len(unexposed_pool) >= blueprint.total_questions else all_questions

        # Group by concept_id for balanced allocation across selected concepts/topics
        questions_by_concept: Dict[str, List[Dict[str, Any]]] = {}
        for q in candidate_pool:
            questions_by_concept.setdefault(q["concept_id"], []).append(q)

        # Round-robin balanced allocation across selected concepts
        selected: List[Dict[str, Any]] = []
        selected_ids = set()
        concept_keys = sorted(questions_by_concept.keys())

        # First pass: Allocate across concepts in balanced rounds
        while len(selected) < blueprint.total_questions and any(questions_by_concept[ck] for ck in concept_keys):
            added_in_round = False
            for ck in concept_keys:
                if len(selected) >= blueprint.total_questions:
                    break
                pool = questions_by_concept[ck]
                if pool:
                    # Pop a question from this concept
                    q = pool.pop(0)
                    if q["id"] not in selected_ids:
                        selected.append(q)
                        selected_ids.add(q["id"])
                        added_in_round = True
            if not added_in_round:
                break

        # Fallback backfill from candidate pool if needed
        for q in candidate_pool:
            if len(selected) >= blueprint.total_questions:
                break
            if q["id"] not in selected_ids:
                selected.append(q)
                selected_ids.add(q["id"])

        exam_id = f"mock_{uuid.uuid4().hex[:10]}"
        now_iso = now_dt.isoformat()

        cur.execute("""
        INSERT INTO mock_exams (
            id, user_id, exam_version, title, blueprint_name, duration_seconds,
            total_questions, marks_per_question, negative_marks, status, config_json, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'CREATED', ?, ?)
        """, (
            exam_id, user_id, blueprint.exam_version, blueprint.title, blueprint.name,
            blueprint.duration_minutes * 60, len(selected), blueprint.marks_per_question,
            blueprint.negative_marks, json.dumps(blueprint.to_dict()), now_iso
        ))

        # Insert items
        for pos, q in enumerate(selected, 1):
            item_id = f"mitem_{exam_id}_{pos:03d}"
            cur.execute("""
            INSERT INTO mock_exam_items (
                id, exam_id, question_id, position, domain_id, concept_id,
                question_type, difficulty, marks, negative_marks
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item_id, exam_id, q["id"], pos, q.get("domain_id"), q["concept_id"],
                q["question_type"], q["difficulty"], blueprint.marks_per_question, blueprint.negative_marks
            ))

        conn.commit()
        conn.close()

        return {
            "exam_id": exam_id,
            "title": blueprint.title,
            "exam_version": blueprint.exam_version,
            "status": "CREATED",
            "total_questions": len(selected),
            "duration_seconds": blueprint.duration_minutes * 60,
            "marks_per_question": blueprint.marks_per_question,
            "negative_marks": blueprint.negative_marks
        }

    def start_mock_exam(self, exam_id: str, user_id: str) -> Dict[str, Any]:
        """Transitions exam status to IN_PROGRESS and starts server timer."""
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute("SELECT status, started_at, duration_seconds FROM mock_exams WHERE id = ? AND user_id = ?", (exam_id, user_id))
        row = cur.fetchone()
        if not row:
            conn.close()
            raise ValueError(f"Mock exam {exam_id} not found.")

        now_iso = datetime.datetime.now(timezone.utc).isoformat()
        if row["status"] in ["CREATED", "READY"]:
            cur.execute("""
            UPDATE mock_exams
            SET status = 'IN_PROGRESS', started_at = ?
            WHERE id = ?
            """, (now_iso, exam_id))
            conn.commit()
            status = "IN_PROGRESS"
            started_at = now_iso
            elapsed = 0
        else:
            status = row["status"]
            started_at = row["started_at"]
            elapsed = self._compute_elapsed_seconds(exam_id, conn)

        conn.close()
        remaining = max(0, row["duration_seconds"] - elapsed)
        return {
            "exam_id": exam_id,
            "status": status,
            "started_at": started_at,
            "remaining_seconds": remaining
        }

    def _compute_elapsed_seconds(self, exam_id: str, conn = None) -> int:
        cur = conn.cursor() if conn else self._get_connection().cursor()
        cur.execute("""
        SELECT status, started_at, paused_at, resumed_at, elapsed_seconds, duration_seconds
        FROM mock_exams WHERE id = ?
        """, (exam_id,))
        row = cur.fetchone()
        if not row or not row["started_at"]:
            return 0

        if row["status"] == "PAUSED":
            return row["elapsed_seconds"]

        # Calculate time passed since last resume (or start)
        ref_time_str = row["resumed_at"] or row["started_at"]
        ref_dt = datetime.datetime.fromisoformat(ref_time_str)
        now_dt = datetime.datetime.now(timezone.utc)
        additional_sec = int((now_dt - ref_dt).total_seconds())
        total_elapsed = row["elapsed_seconds"] + additional_sec
        return min(total_elapsed, row["duration_seconds"])

    def get_mock_exam(self, exam_id: str, user_id: str) -> Dict[str, Any]:
        """
        Retrieves complete mock session with full recovery:
        questions, recorded answers, and server-authoritative timer remaining.
        """
        conn = self._get_connection()
        cur = conn.cursor()

        cur.execute("SELECT * FROM mock_exams WHERE id = ? AND user_id = ?", (exam_id, user_id))
        exam_row = cur.fetchone()
        if not exam_row:
            conn.close()
            raise ValueError(f"Mock exam {exam_id} not found.")

        elapsed = self._compute_elapsed_seconds(exam_id, conn)
        remaining = max(0, exam_row["duration_seconds"] - elapsed)

        # Auto-submit if timer expired and status is IN_PROGRESS
        if remaining == 0 and exam_row["status"] in ["IN_PROGRESS", "PAUSED"]:
            conn.close()
            return self.submit_mock_exam(exam_id, user_id)

        # Fetch items
        cur.execute("""
        SELECT i.position, i.marks, i.negative_marks,
               q.id as question_id, q.concept_id, q.question_type, q.difficulty,
               q.question_text, q.options_json, c.name as concept_name, c.domain_id
        FROM mock_exam_items i
        JOIN questions q ON i.question_id = q.id
        LEFT JOIN concepts c ON q.concept_id = c.id
        WHERE i.exam_id = ?
        ORDER BY i.position ASC
        """, (exam_id,))
        item_rows = cur.fetchall()

        # Fetch existing attempts
        cur.execute("""
        SELECT question_id, selected_option, is_correct, time_spent_ms, confidence, answered_at
        FROM mock_attempts WHERE exam_id = ?
        """, (exam_id,))
        attempts_map = {r["question_id"]: dict(r) for r in cur.fetchall()}

        questions = []
        for r in item_rows:
            qid = r["question_id"]
            user_attempt = attempts_map.get(qid)
            questions.append({
                "position": r["position"],
                "question_id": qid,
                "concept_id": r["concept_id"],
                "concept_name": r["concept_name"] or "Pharmacology Concept",
                "domain_id": r["domain_id"] or "general_pharmacology",
                "question_type": r["question_type"],
                "difficulty": r["difficulty"],
                "question_text": r["question_text"],
                "options": json.loads(r["options_json"]),
                "marks": r["marks"],
                "negative_marks": r["negative_marks"],
                "selected_option": user_attempt["selected_option"] if user_attempt else None,
                "confidence": user_attempt["confidence"] if user_attempt else None
            })

        result_data = json.loads(exam_row["result_json"]) if exam_row["result_json"] else None
        conn.close()

        return {
            "exam_id": exam_id,
            "title": exam_row["title"],
            "exam_version": exam_row["exam_version"],
            "status": exam_row["status"],
            "duration_seconds": exam_row["duration_seconds"],
            "elapsed_seconds": elapsed,
            "remaining_seconds": remaining,
            "total_questions": exam_row["total_questions"],
            "marks_per_question": exam_row["marks_per_question"],
            "negative_marks": exam_row["negative_marks"],
            "questions": questions,
            "result": result_data
        }

    def record_mock_answer(
        self,
        exam_id: str,
        user_id: str,
        question_id: str,
        selected_option: Optional[int],
        time_spent_ms: float = 0.0,
        confidence: int = 3
    ) -> Dict[str, Any]:
        """Records student answer for an item during the mock examination."""
        conn = self._get_connection()
        cur = conn.cursor()

        cur.execute("SELECT status, duration_seconds FROM mock_exams WHERE id = ? AND user_id = ?", (exam_id, user_id))
        exam_row = cur.fetchone()
        if not exam_row:
            conn.close()
            raise ValueError("Mock exam not found.")
        if exam_row["status"] not in ["IN_PROGRESS", "PAUSED", "CREATED"]:
            conn.close()
            raise ValueError(f"Cannot submit answer: Mock exam is in {exam_row['status']} state.")

        # Check correct option from questions table
        cur.execute("SELECT correct_option FROM questions WHERE id = ?", (question_id,))
        q_row = cur.fetchone()
        if not q_row:
            conn.close()
            raise ValueError(f"Question {question_id} not found.")

        is_correct = int(selected_option == q_row["correct_option"]) if selected_option is not None else None
        now_iso = datetime.datetime.now(timezone.utc).isoformat()
        att_id = f"matt_{exam_id}_{question_id}"

        cur.execute("""
        INSERT INTO mock_attempts (
            id, exam_id, question_id, selected_option, is_correct, time_spent_ms, confidence, answered_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(exam_id, question_id) DO UPDATE SET
            selected_option = excluded.selected_option,
            is_correct = excluded.is_correct,
            time_spent_ms = time_spent_ms + excluded.time_spent_ms,
            confidence = excluded.confidence,
            answered_at = excluded.answered_at
        """, (att_id, exam_id, question_id, selected_option, is_correct, time_spent_ms, confidence, now_iso))

        conn.commit()
        conn.close()
        return {
            "exam_id": exam_id,
            "question_id": question_id,
            "status": "saved",
            "answered_at": now_iso
        }

    def pause_mock_exam(self, exam_id: str, user_id: str) -> Dict[str, Any]:
        """Pauses timer and saves elapsed time."""
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute("SELECT status, started_at, elapsed_seconds FROM mock_exams WHERE id = ? AND user_id = ?", (exam_id, user_id))
        row = cur.fetchone()
        if not row or row["status"] != "IN_PROGRESS":
            conn.close()
            return {"status": row["status"] if row else "NOT_FOUND"}

        elapsed = self._compute_elapsed_seconds(exam_id, conn)
        now_iso = datetime.datetime.now(timezone.utc).isoformat()

        cur.execute("""
        UPDATE mock_exams
        SET status = 'PAUSED', paused_at = ?, elapsed_seconds = ?
        WHERE id = ?
        """, (now_iso, elapsed, exam_id))

        conn.commit()
        conn.close()
        return {"exam_id": exam_id, "status": "PAUSED", "elapsed_seconds": elapsed}

    def submit_mock_exam(self, exam_id: str, user_id: str) -> Dict[str, Any]:
        """Submits the exam, scores it, performs diagnostic evaluation, and logs feedback events."""
        conn = self._get_connection()
        cur = conn.cursor()

        cur.execute("SELECT * FROM mock_exams WHERE id = ? AND user_id = ?", (exam_id, user_id))
        exam_row = cur.fetchone()
        if not exam_row:
            conn.close()
            raise ValueError("Exam not found.")

        # Fetch questions and distractor reasons
        cur.execute("""
        SELECT i.position, i.marks, i.negative_marks,
               q.id as question_id, q.concept_id, q.question_type, q.difficulty,
               q.distractor_reasons_json, q.explanation, q.source_page,
               c.name as concept_name, c.domain_id
        FROM mock_exam_items i
        JOIN questions q ON i.question_id = q.id
        LEFT JOIN concepts c ON q.concept_id = c.id
        WHERE i.exam_id = ?
        ORDER BY i.position ASC
        """, (exam_id,))
        item_rows = cur.fetchall()

        items = []
        for r in item_rows:
            distractors = json.loads(r["distractor_reasons_json"]) if r["distractor_reasons_json"] else {}
            items.append({
                "position": r["position"],
                "question_id": r["question_id"],
                "concept_id": r["concept_id"],
                "concept_name": r["concept_name"],
                "domain_id": r["domain_id"],
                "question_type": r["question_type"],
                "difficulty": r["difficulty"],
                "marks": r["marks"],
                "negative_marks": r["negative_marks"],
                "distractor_reasons": distractors,
                "explanation": r["explanation"],
                "source_page": r["source_page"]
            })

        # Fetch student attempts
        cur.execute("SELECT * FROM mock_attempts WHERE exam_id = ?", (exam_id,))
        attempts = [dict(r) for r in cur.fetchall()]

        now_iso = datetime.datetime.now(timezone.utc).isoformat()
        blueprint_config = json.loads(exam_row["config_json"])

        # Run MockScorer
        eval_result = MockScorer.evaluate_mock_session(
            blueprint_config=blueprint_config,
            items=items,
            attempts=attempts,
            started_at=exam_row["started_at"] or now_iso,
            submitted_at=now_iso
        )

        raw_score = eval_result["summary"]["raw_score"]
        score_pct = eval_result["summary"]["score_percent"]
        accuracy = eval_result["summary"]["accuracy_percent"]

        # Update mock_exams row
        cur.execute("""
        UPDATE mock_exams
        SET status = 'EVALUATED', submitted_at = ?, evaluated_at = ?,
            score = ?, score_percent = ?, accuracy_percent = ?,
            result_json = ?
        WHERE id = ?
        """, (now_iso, now_iso, raw_score, score_pct, accuracy, json.dumps(eval_result), exam_id))

        # Log feedback into learning_events for adaptive scheduler connection
        event_id = f"evt_mock_{uuid.uuid4().hex[:10]}"
        cur.execute("""
        INSERT INTO learning_events (event_id, user_id, event_type, timestamp, payload_json)
        VALUES (?, ?, 'MOCK_EXAM_EVALUATED', ?, ?)
        """, (
            event_id, user_id, now_iso,
            json.dumps({
                "exam_id": exam_id,
                "raw_score": raw_score,
                "accuracy": accuracy,
                "recommended_repairs": eval_result["recommended_repairs"],
                "timing_quadrants": eval_result["timing_analysis"]["quadrants"]
            })
        ))

        conn.commit()
        conn.close()

        eval_result["exam_id"] = exam_id
        eval_result["status"] = "EVALUATED"
        return eval_result

    def list_mock_history(self, user_id: str) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute("""
        SELECT id, title, exam_version, blueprint_name, duration_seconds, total_questions,
               status, score, score_percent, accuracy_percent, started_at, submitted_at, created_at
        FROM mock_exams
        WHERE user_id = ?
        ORDER BY created_at DESC
        """, (user_id,))
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows
