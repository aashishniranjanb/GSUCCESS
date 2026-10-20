"""
Repository Layer for GPAT 2027 Learning Operating System.
Provides a clean, decoupled abstraction over SQLite so the rest of the application
calls repository methods instead of raw database queries.
Can later be swapped to PostgresRepository without changing business logic.
"""

import sqlite3
import json
import uuid
import datetime
from datetime import timezone
from typing import Dict, Any, List, Optional
from pathlib import Path

DB_PATH = str(Path(__file__).resolve().parent.parent.parent / "gpat_knowledge.db")

class GPATRepository:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    # --- SESSIONS & DETERMINISTIC RECALL ---

    def get_or_create_daily_session(self, user_id: str, session_date: str, target_minutes: int) -> Dict[str, Any]:
        """
        Ensures a single canonical session per student per day.
        If a session already exists for today, returns it with its saved question sequence.
        If not, returns None to signal that the scheduler should build and persist one.
        """
        conn = self._get_connection()
        cur = conn.cursor()
        
        cur.execute("""
        SELECT id, user_id, session_date, target_minutes, status, started_at, completed_at, created_at
        FROM study_sessions
        WHERE user_id = ? AND session_date = ?
        """, (user_id, session_date))
        
        row = cur.fetchone()
        if not row:
            conn.close()
            return None

        session_id = row["id"]
        
        # Fetch items
        cur.execute("""
        SELECT i.id, i.question_id, i.concept_id, i.sequence, i.source_type, i.status,
               i.presented_at, i.answered_at, i.is_correct,
               q.question_text, q.options_json, q.correct_option, q.distractor_reasons_json,
               q.explanation, q.source_page, q.cue,
               c.name as concept_name, c.importance_score
        FROM study_session_items i
        JOIN questions q ON i.question_id = q.id
        LEFT JOIN concepts c ON i.concept_id = c.id
        WHERE i.session_id = ?
        ORDER BY i.sequence ASC
        """, (session_id,))
        
        item_rows = cur.fetchall()
        questions = []
        for r in item_rows:
            questions.append({
                "item_id": r["id"],
                "question_id": r["question_id"],
                "concept_id": r["concept_id"],
                "concept_name": r["concept_name"] or "Pharmacology Concept",
                "importance": r["importance_score"] or 10,
                "sequence": r["sequence"],
                "source_type": r["source_type"],
                "item_status": r["status"],
                "is_correct": bool(r["is_correct"]) if r["is_correct"] is not None else None,
                "question_text": r["question_text"],
                "options": json.loads(r["options_json"]),
                "correct_option": r["correct_option"],
                "source_page": r["source_page"],
                "cue": r["cue"]
            })
            
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "session_date": session_date,
            "session_time_minutes": row["target_minutes"],
            "target_question_count": len(questions),
            "status": row["status"],
            "started_at": row["started_at"],
            "completed_at": row["completed_at"],
            "questions": questions
        }
        conn.close()
        return session_data

    def persist_daily_session(self, user_id: str, session_date: str, target_minutes: int, questions: List[Dict[str, Any]]) -> str:
        """Saves newly scheduled questions as the canonical session for session_date."""
        conn = self._get_connection()
        cur = conn.cursor()
        
        session_id = f"sess_{session_date}_{user_id}"
        now_iso = datetime.datetime.now(timezone.utc).isoformat()
        
        cur.execute("""
        INSERT INTO study_sessions (id, user_id, session_date, target_minutes, status, started_at, created_at)
        VALUES (?, ?, ?, ?, 'active', ?, ?)
        ON CONFLICT(user_id, session_date) DO UPDATE SET
            target_minutes = excluded.target_minutes
        """, (session_id, user_id, session_date, target_minutes, now_iso, now_iso))
        
        # Insert items
        for seq, q in enumerate(questions, 1):
            item_id = f"item_{session_id}_{seq:02d}"
            cur.execute("""
            INSERT OR REPLACE INTO study_session_items 
            (id, session_id, question_id, concept_id, sequence, source_type, status)
            VALUES (?, ?, ?, ?, ?, ?, 'pending')
            """, (
                item_id,
                session_id,
                q.get("question_id", q.get("id")),
                q.get("concept_id"),
                seq,
                q.get("source_type", "high_yield")
            ))
            
        conn.commit()
        conn.close()
        return session_id

    def update_session_item_result(self, user_id: str, question_id: str, is_correct: bool):
        """Updates today's session item status upon submission."""
        today_date = datetime.date.today().isoformat()
        session_id = f"sess_{today_date}_{user_id}"
        now_iso = datetime.datetime.now(timezone.utc).isoformat()
        
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute("""
        UPDATE study_session_items
        SET status = 'answered', answered_at = ?, is_correct = ?
        WHERE session_id = ? AND question_id = ?
        """, (now_iso, 1 if is_correct else 0, session_id, question_id))
        
        # Check if all items in session are completed
        cur.execute("""
        SELECT COUNT(*) FROM study_session_items WHERE session_id = ? AND status != 'answered'
        """, (session_id,))
        remaining = cur.fetchone()[0]
        if remaining == 0:
            cur.execute("UPDATE study_sessions SET status = 'completed', completed_at = ? WHERE id = ?", (now_iso, session_id))
            
        conn.commit()
        conn.close()

    # --- LEARNING EVENTS (TELEMETRY) ---

    def log_learning_event(self, user_id: str, event_type: str, question_id: Optional[str] = None,
                           concept_id: Optional[str] = None, payload: Optional[Dict[str, Any]] = None):
        """Appends an event to learning_events audit log."""
        event_id = f"evt_{uuid.uuid4().hex[:12]}"
        now_iso = datetime.datetime.now(timezone.utc).isoformat()
        payload_str = json.dumps(payload or {})
        
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO learning_events (event_id, user_id, event_type, question_id, concept_id, timestamp, payload_json)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (event_id, user_id, event_type, question_id, concept_id, now_iso, payload_str))
        conn.commit()
        conn.close()
        return event_id
