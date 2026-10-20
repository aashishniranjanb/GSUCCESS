"""
SQLite Implementation of StudyRepository.
Encapsulates all interaction with study_sessions, study_session_items, and learning_events.
"""

import sqlite3
import json
import uuid
import datetime
from datetime import timezone
from typing import Dict, Any, List, Optional
from pathlib import Path

from backend.repositories.study_repository import StudyRepository

DB_PATH = str(Path(__file__).resolve().parent.parent.parent / "gpat_knowledge.db")

class SQLiteStudyRepository(StudyRepository):
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_or_create_daily_session(self, user_id: str, session_date: str, target_minutes: int) -> Optional[Dict[str, Any]]:
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
        
        # Check if baseline tables exist in this database
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='baseline_questions'")
        has_bq = bool(cur.fetchone())
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='baseline_media'")
        has_bm = bool(cur.fetchone())

        # Check if study_session_items has candidate_type column
        cur.execute("PRAGMA table_info(study_session_items)")
        item_cols = [c["name"] for c in cur.fetchall()]
        has_cand_type = "candidate_type" in item_cols

        cand_type_select = "i.candidate_type, i.reason_codes, i.estimated_seconds," if has_cand_type else "i.source_type as candidate_type, '[]' as reason_codes, 150 as estimated_seconds,"

        if has_bq and has_bm:
            query = f"""
            SELECT i.id, i.question_id, i.concept_id, i.sequence, i.source_type, i.status,
                   i.presented_at, i.answered_at, i.is_correct,
                   {cand_type_select}
                   q.question_text, q.options_json, q.correct_option, q.distractor_reasons_json,
                   q.explanation, q.source_page, q.cue,
                   c.name as concept_name, c.importance_score,
                   m.relative_file_path, m.alt_text, m.caption
            FROM study_session_items i
            JOIN questions q ON i.question_id = q.id
            LEFT JOIN concepts c ON i.concept_id = c.id
            LEFT JOIN baseline_questions bq ON bq.id = q.id
            LEFT JOIN baseline_media m ON bq.media_id = m.media_id
            WHERE i.session_id = ?
            ORDER BY i.sequence ASC
            """
        else:
            query = f"""
            SELECT i.id, i.question_id, i.concept_id, i.sequence, i.source_type, i.status,
                   i.presented_at, i.answered_at, i.is_correct,
                   {cand_type_select}
                   q.question_text, q.options_json, q.correct_option, q.distractor_reasons_json,
                   q.explanation, q.source_page, q.cue,
                   c.name as concept_name, c.importance_score,
                   NULL as relative_file_path, NULL as alt_text, NULL as caption
            FROM study_session_items i
            JOIN questions q ON i.question_id = q.id
            LEFT JOIN concepts c ON i.concept_id = c.id
            WHERE i.session_id = ?
            ORDER BY i.sequence ASC
            """
        cur.execute(query, (session_id,))
        
        item_rows = cur.fetchall()
        questions = []
        for r in item_rows:
            m_path = r["relative_file_path"] if "relative_file_path" in r.keys() else None
            media_url = None
            if m_path:
                norm_p = m_path.replace("\\", "/")
                media_url = "/" + norm_p.replace("baseline/", "") if norm_p.startswith("baseline/") else "/" + norm_p

            raw_reasons = r["reason_codes"] if "reason_codes" in r.keys() else "[]"
            try:
                parsed_reasons = json.loads(raw_reasons) if isinstance(raw_reasons, str) and raw_reasons.startswith("[") else [raw_reasons]
            except Exception:
                parsed_reasons = [raw_reasons]

            questions.append({
                "item_id": r["id"],
                "question_id": r["question_id"],
                "concept_id": r["concept_id"],
                "concept_name": r["concept_name"] or "Pharmacology Concept",
                "importance": r["importance_score"] or 10,
                "sequence": r["sequence"],
                "source_type": r["source_type"],
                "candidate_type": r["candidate_type"] if "candidate_type" in r.keys() else r["source_type"],
                "reason_codes": parsed_reasons,
                "estimated_seconds": r["estimated_seconds"] if "estimated_seconds" in r.keys() else 150,
                "item_status": r["status"],
                "is_correct": bool(r["is_correct"]) if r["is_correct"] is not None else None,
                "question_text": r["question_text"],
                "options": json.loads(r["options_json"]),
                "correct_option": r["correct_option"],
                "explanation": r["explanation"],
                "distractor_reasons": json.loads(r["distractor_reasons_json"]) if r["distractor_reasons_json"] else {},
                "source_page": r["source_page"],
                "cue": r["cue"],
                "media_url": media_url,
                "media_alt": r["alt_text"] if "alt_text" in r.keys() else None,
                "media_caption": r["caption"] if "caption" in r.keys() else None
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
        
        # Check if table has Phase 3 columns
        cur.execute("PRAGMA table_info(study_session_items)")
        cols = [c["name"] for c in cur.fetchall()]
        has_cand_type = "candidate_type" in cols

        # Remove existing items for this session_id to allow clean duration resizing
        cur.execute("DELETE FROM study_session_items WHERE session_id = ?", (session_id,))

        for seq, q in enumerate(questions, 1):
            item_id = f"item_{session_id}_{seq:02d}"
            cand_type = q.get("candidate_type", q.get("source_type", "NEW_LEARNING"))
            reasons = json.dumps(q.get("reason_codes", ["HIGH_YIELD_CONCEPT"])) if isinstance(q.get("reason_codes"), list) else q.get("reason_codes", "HIGH_YIELD_CONCEPT")
            est_sec = q.get("estimated_seconds", 150)
            
            if has_cand_type:
                cur.execute("""
                INSERT OR REPLACE INTO study_session_items 
                (id, session_id, question_id, concept_id, sequence, source_type, status, candidate_type, reason_codes, estimated_seconds)
                VALUES (?, ?, ?, ?, ?, ?, 'pending', ?, ?, ?)
                """, (
                    item_id,
                    session_id,
                    q.get("question_id", q.get("id")),
                    q.get("concept_id"),
                    seq,
                    q.get("source_type", "high_yield"),
                    cand_type,
                    reasons,
                    est_sec
                ))
            else:
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

    def update_session_item_result(self, user_id: str, question_id: str, is_correct: bool, cur: Optional[sqlite3.Cursor] = None, session_date: Optional[str] = None):
        target_date = session_date or datetime.date.today().isoformat()
        session_id = f"sess_{target_date}_{user_id}"
        now_iso = datetime.datetime.now(timezone.utc).isoformat()
        
        own_conn = False
        if cur is None:
            conn = self._get_connection()
            cur = conn.cursor()
            own_conn = True
        else:
            conn = cur.connection
            
        cur.execute("""
        UPDATE study_session_items
        SET status = 'answered', answered_at = ?, is_correct = ?
        WHERE (session_id = ? OR question_id = ?) AND question_id = ?
        """, (now_iso, 1 if is_correct else 0, session_id, question_id, question_id))
        
        # Look up session_id of the item to update parent session properly
        cur.execute("SELECT session_id FROM study_session_items WHERE question_id = ? ORDER BY id DESC LIMIT 1", (question_id,))
        actual_session_row = cur.fetchone()
        actual_session_id = actual_session_row[0] if actual_session_row else session_id

        cur.execute("""
        SELECT COUNT(*) FROM study_session_items WHERE session_id = ? AND status != 'answered'
        """, (actual_session_id,))
        remaining = cur.fetchone()[0]
        if remaining == 0:
            cur.execute("UPDATE study_sessions SET status = 'completed', completed_at = ? WHERE id = ?", (now_iso, actual_session_id))
            
        if own_conn:
            conn.commit()
            conn.close()

    def log_learning_event(self, user_id: str, event_type: str, question_id: Optional[str] = None,
                           concept_id: Optional[str] = None, payload: Optional[Dict[str, Any]] = None,
                           cur: Optional[sqlite3.Cursor] = None) -> str:
        event_id = f"evt_{uuid.uuid4().hex[:12]}"
        now_iso = datetime.datetime.now(timezone.utc).isoformat()
        payload_str = json.dumps(payload or {})
        
        own_conn = False
        if cur is None:
            conn = self._get_connection()
            cur = conn.cursor()
            own_conn = True
        else:
            conn = cur.connection
            
        cur.execute("""
        INSERT INTO learning_events (event_id, user_id, event_type, question_id, concept_id, timestamp, payload_json)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (event_id, user_id, event_type, question_id, concept_id, now_iso, payload_str))
        
        if own_conn:
            conn.commit()
            conn.close()
        return event_id
