import os
import json
import sqlite3
import datetime
from datetime import timezone
from typing import Dict, Any, List, Optional
from pathlib import Path

class AchievementEngine:
    """
    Deterministic, explainable progress rewards evaluator.
    Evaluates learning evidence committed to SQLite and transactionally awards
    deduplicated achievements.
    
    Zero probabilistic models / LLM dependency.
    Zero streak anxiety / No loss threats / No punitive resets.
    """
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or os.environ.get("GPAT_DB_PATH", "gpat_knowledge.db")
        self._ensure_tables()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_tables(self):
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS learner_achievements (
            id TEXT PRIMARY KEY,
            student_id TEXT NOT NULL,
            achievement_type TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            evidence_type TEXT NOT NULL,
            evidence_id TEXT NOT NULL,
            evidence_metadata_json TEXT,
            awarded_at TEXT NOT NULL,
            rule_version TEXT NOT NULL DEFAULT '1.0.0',
            UNIQUE(student_id, achievement_type, evidence_id)
        )
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS learner_goals (
            id TEXT PRIMARY KEY,
            student_id TEXT NOT NULL,
            goal_type TEXT NOT NULL,
            target_count INTEGER NOT NULL DEFAULT 5,
            status TEXT NOT NULL DEFAULT 'active',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            UNIQUE(student_id, goal_type)
        )
        """)
        conn.commit()
        conn.close()

    def get_or_create_goal(self, student_id: str, goal_type: str = "completed_missions", cur: Optional[sqlite3.Cursor] = None) -> Dict[str, Any]:
        """Retrieves or creates a default non-punitive weekly goal (e.g. 5 missions/week)."""
        own_conn = False
        if cur is None:
            conn = self._get_connection()
            cur = conn.cursor()
            own_conn = True
        else:
            conn = cur.connection

        cur.execute("""
        SELECT id, student_id, goal_type, target_count, status, created_at, updated_at
        FROM learner_goals
        WHERE student_id = ? AND goal_type = ?
        """, (student_id, goal_type))
        row = cur.fetchone()
        now_iso = datetime.datetime.now(timezone.utc).isoformat()
        if not row:
            goal_id = f"goal_{student_id}_{goal_type}"
            cur.execute("""
            INSERT OR IGNORE INTO learner_goals (id, student_id, goal_type, target_count, status, created_at, updated_at)
            VALUES (?, ?, ?, 5, 'active', ?, ?)
            """, (goal_id, student_id, goal_type, now_iso, now_iso))
            if own_conn:
                conn.commit()
            goal_data = {
                "id": goal_id,
                "student_id": student_id,
                "goal_type": goal_type,
                "target_count": 5,
                "status": "active",
                "created_at": now_iso,
                "updated_at": now_iso
            }
        else:
            goal_data = {
                "id": row[0] if not hasattr(row, "keys") else row["id"],
                "student_id": row[1] if not hasattr(row, "keys") else row["student_id"],
                "goal_type": row[2] if not hasattr(row, "keys") else row["goal_type"],
                "target_count": row[3] if not hasattr(row, "keys") else row["target_count"],
                "status": row[4] if not hasattr(row, "keys") else row["status"],
                "created_at": row[5] if not hasattr(row, "keys") else row["created_at"],
                "updated_at": row[6] if not hasattr(row, "keys") else row["updated_at"]
            }
        if own_conn:
            conn.close()
        return goal_data

    def update_goal(self, student_id: str, target_count: int, status: str = "active", goal_type: str = "completed_missions") -> Dict[str, Any]:
        """Updates user-configurable goal without erasing history or punishing changes."""
        target_count = max(1, min(20, target_count))
        if status not in ("active", "paused"):
            status = "active"
        conn = self._get_connection()
        cur = conn.cursor()
        now_iso = datetime.datetime.now(timezone.utc).isoformat()
        goal_id = f"goal_{student_id}_{goal_type}"
        cur.execute("""
        INSERT INTO learner_goals (id, student_id, goal_type, target_count, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(student_id, goal_type) DO UPDATE SET
            target_count = excluded.target_count,
            status = excluded.status,
            updated_at = excluded.updated_at
        """, (goal_id, student_id, goal_type, target_count, status, now_iso, now_iso))
        conn.commit()
        conn.close()
        return {
            "id": goal_id,
            "student_id": student_id,
            "goal_type": goal_type,
            "target_count": target_count,
            "status": status,
            "updated_at": now_iso
        }

    def evaluate_mission_completion(self, student_id: str, session_id: str, cur: Optional[sqlite3.Cursor] = None) -> List[Dict[str, Any]]:
        """
        Evaluates Rule A: Meaningful Mission Completion.
        Awards achievement only if all items in session are answered.
        """
        own_conn = False
        if cur is None:
            conn = self._get_connection()
            cur = conn.cursor()
            own_conn = True
        else:
            conn = cur.connection

        def _val(row, col_name, idx):
            if row is None:
                return None
            if isinstance(row, sqlite3.Row) or hasattr(row, "keys"):
                return row[col_name]
            return row[idx]

        newly_awarded = []
        cur.execute("SELECT id, user_id, session_date, target_minutes, status FROM study_sessions WHERE id = ?", (session_id,))
        sess_row = cur.fetchone()
        if not sess_row or _val(sess_row, "user_id", 1) != student_id or _val(sess_row, "status", 4) != "completed":
            if own_conn:
                conn.close()
            return newly_awarded

        # Check all items answered
        cur.execute("SELECT count(*), sum(case when status = 'answered' then 1 else 0 end) FROM study_session_items WHERE session_id = ?", (session_id,))
        item_stats = cur.fetchone()
        total_items = item_stats[0] or 0
        answered_items = item_stats[1] or 0

        if total_items > 0 and answered_items >= total_items:
            # Award MISSION_COMPLETION
            now_iso = datetime.datetime.now(timezone.utc).isoformat()
            ach_id = f"ach_{student_id}_MISSION_COMPLETION_{session_id}"
            meta = json.dumps({"session_id": session_id, "questions_count": total_items, "session_date": _val(sess_row, "session_date", 2)})
            try:
                cur.execute("""
                INSERT OR IGNORE INTO learner_achievements 
                (id, student_id, achievement_type, title, description, evidence_type, evidence_id, evidence_metadata_json, awarded_at, rule_version)
                VALUES (?, ?, 'MISSION_COMPLETION', 'Mission Accomplished', 'Completed all personalized retrieval tasks in today''s mission.', 'session_id', ?, ?, ?, '1.0.0')
                """, (ach_id, student_id, session_id, meta, now_iso))
                if cur.rowcount > 0:
                    newly_awarded.append({
                        "id": ach_id,
                        "achievement_type": "MISSION_COMPLETION",
                        "title": "Mission Accomplished",
                        "description": "Completed all personalized retrieval tasks in today's mission.",
                        "evidence_id": session_id,
                        "awarded_at": now_iso
                    })
            except Exception:
                pass

        # Check Rule E: Personal Best for this session
        cur.execute("""
        SELECT i.session_id, count(*) as total, sum(case when a.is_correct = 1 then 1 else 0 end) as correct
        FROM study_session_items i
        JOIN student_attempts a ON a.student_id = ? AND a.question_id = i.question_id
        WHERE i.session_id = ?
        """, (student_id, session_id))
        cur_perf = cur.fetchone()
        tot_cnt = _val(cur_perf, "total", 1)
        cor_cnt = _val(cur_perf, "correct", 2)
        if cur_perf and tot_cnt and tot_cnt >= 5:
            cur_acc = round((cor_cnt / tot_cnt) * 100, 1)
            # Find best prior session accuracy
            cur.execute("""
            SELECT max(round((cast(s.correct as real) / s.total) * 100, 1))
            FROM (
                SELECT i.session_id, count(*) as total, sum(case when a.is_correct = 1 then 1 else 0 end) as correct
                FROM study_session_items i
                JOIN student_attempts a ON a.student_id = ? AND a.question_id = i.question_id
                WHERE i.session_id != ?
                GROUP BY i.session_id
                HAVING total >= 5
            ) s
            """, (student_id, session_id))
            prior_best_row = cur.fetchone()
            prior_best = prior_best_row[0] if (prior_best_row and prior_best_row[0] is not None) else None
            
            if prior_best is None or cur_acc > prior_best:
                pb_id = f"ach_{student_id}_PERSONAL_BEST_{session_id}"
                now_iso = datetime.datetime.now(timezone.utc).isoformat()
                meta = json.dumps({"session_id": session_id, "previous_best": prior_best, "current_accuracy": cur_acc, "questions_count": cur_perf["total"]})
                try:
                    cur.execute("""
                    INSERT OR IGNORE INTO learner_achievements 
                    (id, student_id, achievement_type, title, description, evidence_type, evidence_id, evidence_metadata_json, awarded_at, rule_version)
                    VALUES (?, ?, 'PERSONAL_BEST', 'Personal Best Accuracy', 'Achieved highest retrieval accuracy across a full study mission.', 'session_id', ?, ?, ?, '1.0.0')
                    """, (pb_id, student_id, session_id, meta, now_iso))
                    if cur.rowcount > 0:
                        newly_awarded.append({
                            "id": pb_id,
                            "achievement_type": "PERSONAL_BEST",
                            "title": "Personal Best Accuracy",
                            "description": "Achieved highest retrieval accuracy across a full study mission.",
                            "evidence_id": session_id,
                            "awarded_at": now_iso
                        })
                except Exception:
                    pass

        # Check Rule F: Weekly Goal Met
        goal = self.get_or_create_goal(student_id, cur=cur)
        if goal["status"] == "active":
            target = goal["target_count"]
            today = datetime.date.today()
            year, week_num, _ = today.isocalendar()
            iso_week = f"{year}-W{week_num:02d}"
            # Count completed sessions in current ISO week
            # Find Monday of this week
            mon = today - datetime.timedelta(days=today.weekday())
            sun = mon + datetime.timedelta(days=6)
            cur.execute("""
            SELECT count(distinct session_date)
            FROM study_sessions
            WHERE user_id = ? AND status = 'completed' AND session_date BETWEEN ? AND ?
            """, (student_id, mon.isoformat(), sun.isoformat()))
            completed_in_week = cur.fetchone()[0] or 0
            if completed_in_week >= target:
                wg_id = f"ach_{student_id}_WEEKLY_GOAL_MET_{iso_week}"
                meta = json.dumps({"iso_week": iso_week, "target": target, "achieved": completed_in_week})
                now_iso = datetime.datetime.now(timezone.utc).isoformat()
                try:
                    cur.execute("""
                    INSERT OR IGNORE INTO learner_achievements 
                    (id, student_id, achievement_type, title, description, evidence_type, evidence_id, evidence_metadata_json, awarded_at, rule_version)
                    VALUES (?, ?, 'WEEKLY_GOAL_MET', 'Weekly Study Goal Met', 'Reached your weekly planned study missions with consistent practice.', 'iso_week', ?, ?, ?, '1.0.0')
                    """, (wg_id, student_id, iso_week, meta, now_iso))
                    if cur.rowcount > 0:
                        newly_awarded.append({
                            "id": wg_id,
                            "achievement_type": "WEEKLY_GOAL_MET",
                            "title": "Weekly Study Goal Met",
                            "description": "Reached your weekly planned study missions with consistent practice.",
                            "evidence_id": iso_week,
                            "awarded_at": now_iso
                        })
                except Exception:
                    pass

        if own_conn:
            conn.commit()
            conn.close()
        return newly_awarded

    def evaluate_attempt_milestones(self, student_id: str, question_id: str, is_correct: bool, cur: Optional[sqlite3.Cursor] = None) -> List[Dict[str, Any]]:
        """
        Evaluates Rules B, C, D upon a committed attempt:
        - Rule B: Delayed Recall (Correct attempt after >= 24 hours)
        - Rule C: Misconception Repair (Correct attempt on concept previously with active/recurring trap)
        - Rule D: Topic Mastery (Concept reaches DEMONSTRATED_MASTERY)
        """
        if not is_correct:
            return []

        own_conn = False
        if cur is None:
            conn = self._get_connection()
            cur = conn.cursor()
            own_conn = True
        else:
            conn = cur.connection

        newly_awarded = []
        now_iso = datetime.datetime.now(timezone.utc).isoformat()

        # Retrieve concept_id
        cur.execute("SELECT concept_id FROM questions WHERE id = ?", (question_id,))
        q_row = cur.fetchone()
        concept_id = q_row[0] if q_row else None

        # --- Rule B: Delayed Recall Improvement ---
        cur.execute("""
        SELECT created_at
        FROM student_attempts
        WHERE student_id = ? AND question_id = ?
        ORDER BY id DESC
        LIMIT 2
        """, (student_id, question_id))
        att_rows = cur.fetchall()
        if len(att_rows) >= 2:
            latest_time_str = att_rows[0][0]
            prior_time_str = att_rows[1][0]
            try:
                def _parse_utc(ts_str):
                    if not ts_str:
                        return datetime.datetime.now(timezone.utc)
                    cleaned = ts_str.replace("Z", "+00:00")
                    dt = datetime.datetime.fromisoformat(cleaned)
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    return dt

                t1 = _parse_utc(latest_time_str)
                t0 = _parse_utc(prior_time_str)
                diff_sec = (t1 - t0).total_seconds()
                if diff_sec >= 86400: # >= 24 hours
                    dr_id = f"ach_{student_id}_DELAYED_RECALL_{question_id}"
                    meta = json.dumps({"question_id": question_id, "interval_hours": round(diff_sec / 3600, 1), "prior_attempt": prior_time_str})
                    cur.execute("""
                    INSERT OR IGNORE INTO learner_achievements
                    (id, student_id, achievement_type, title, description, evidence_type, evidence_id, evidence_metadata_json, awarded_at, rule_version)
                    VALUES (?, ?, 'DELAYED_RECALL', 'Durable Recall Milestone', 'Successfully recalled concept after a 24+ hour retention interval.', 'question_id', ?, ?, ?, '1.0.0')
                    """, (dr_id, student_id, question_id, meta, now_iso))
                    if cur.rowcount > 0:
                        newly_awarded.append({
                            "id": dr_id,
                            "achievement_type": "DELAYED_RECALL",
                            "title": "Durable Recall Milestone",
                            "description": "Successfully recalled concept after a 24+ hour retention interval.",
                            "evidence_id": question_id,
                            "awarded_at": now_iso
                        })
            except Exception:
                pass

        def _val(row, col_name, idx):
            if row is None:
                return None
            if isinstance(row, sqlite3.Row) or hasattr(row, "keys"):
                return row[col_name]
            return row[idx]

        # --- Rule C: Misconception Correction ---
        if concept_id:
            cur.execute("""
            SELECT id, distractor_reason, resolved_at
            FROM student_misconceptions
            WHERE student_id = ? AND concept_id = ? AND status = 'REPAIRED'
            ORDER BY id DESC
            LIMIT 1
            """, (student_id, concept_id))
            repaired_row = cur.fetchone()
            if repaired_row:
                reason = _val(repaired_row, "distractor_reason", 1)
                res_at = _val(repaired_row, "resolved_at", 2)
                mr_id = f"ach_{student_id}_MISCONCEPTION_REPAIR_{concept_id}"
                meta = json.dumps({"concept_id": concept_id, "distractor_reason": reason, "resolved_at": res_at})
                cur.execute("""
                INSERT OR IGNORE INTO learner_achievements
                (id, student_id, achievement_type, title, description, evidence_type, evidence_id, evidence_metadata_json, awarded_at, rule_version)
                VALUES (?, ?, 'MISCONCEPTION_REPAIR', 'Conceptual Trap Repaired', 'Successfully untangled a recurring misconception through active retrieval.', 'concept_id', ?, ?, ?, '1.0.0')
                """, (mr_id, student_id, concept_id, meta, now_iso))
                if cur.rowcount > 0:
                    newly_awarded.append({
                        "id": mr_id,
                        "achievement_type": "MISCONCEPTION_REPAIR",
                        "title": "Conceptual Trap Repaired",
                        "description": "Successfully untangled a recurring misconception through active retrieval.",
                        "evidence_id": concept_id,
                        "awarded_at": now_iso
                    })

        # --- Rule D: Topic Mastery ---
        if concept_id:
            cur.execute("""
            SELECT attempts, correct, stability, misconception_count
            FROM concept_memory_state
            WHERE student_id = ? AND concept_id = ?
            """, (student_id, concept_id))
            c_mem = cur.fetchone()
            if c_mem:
                c_att = _val(c_mem, "attempts", 0)
                c_cor = _val(c_mem, "correct", 1)
                c_stab = _val(c_mem, "stability", 2)
                c_misc = _val(c_mem, "misconception_count", 3)
                
                # Deterministic classifier: attempts >= 3, acc >= 0.8, stability >= 7.0, active traps = 0
                if c_att >= 3 and (c_cor / max(1, c_att)) >= 0.8 and c_stab >= 7.0:
                    # Verify no currently ACTIVE or RECURRING misconceptions
                    cur.execute("""
                    SELECT count(*) FROM student_misconceptions
                    WHERE student_id = ? AND concept_id = ? AND status IN ('ACTIVE', 'RECURRING')
                    """, (student_id, concept_id))
                    active_trap_count = cur.fetchone()[0] or 0
                    if active_trap_count == 0:
                        tm_id = f"ach_{student_id}_TOPIC_MASTERY_{concept_id}"
                        meta = json.dumps({"concept_id": concept_id, "attempts": c_att, "accuracy": round(c_cor / c_att, 2), "stability_days": round(c_stab, 1)})
                        cur.execute("""
                        INSERT OR IGNORE INTO learner_achievements
                        (id, student_id, achievement_type, title, description, evidence_type, evidence_id, evidence_metadata_json, awarded_at, rule_version)
                        VALUES (?, ?, 'TOPIC_MASTERY', 'Demonstrated Topic Mastery', 'Consolidated robust memory stability and high accuracy across multiple sessions.', 'concept_id', ?, ?, ?, '1.0.0')
                        """, (tm_id, student_id, concept_id, meta, now_iso))
                        if cur.rowcount > 0:
                            newly_awarded.append({
                                "id": tm_id,
                                "achievement_type": "TOPIC_MASTERY",
                                "title": "Demonstrated Topic Mastery",
                                "description": "Consolidated robust memory stability and high accuracy across multiple sessions.",
                                "evidence_id": concept_id,
                                "awarded_at": now_iso
                            })

        if own_conn:
            conn.commit()
            conn.close()
        return newly_awarded

    def get_progress_rewards(self, student_id: str) -> Dict[str, Any]:
        """Returns the full rewards overview: weekly goal progress, recent achievements, and personal bests."""
        conn = self._get_connection()
        cur = conn.cursor()

        # Goal & Weekly Progress
        goal = self.get_or_create_goal(student_id)
        today = datetime.date.today()
        mon = today - datetime.timedelta(days=today.weekday())
        sun = mon + datetime.timedelta(days=6)
        year, week_num, _ = today.isocalendar()
        iso_week = f"{year}-W{week_num:02d}"

        cur.execute("""
        SELECT count(distinct session_date)
        FROM study_sessions
        WHERE user_id = ? AND status = 'completed' AND session_date BETWEEN ? AND ?
        """, (student_id, mon.isoformat(), sun.isoformat()))
        completed_in_week = cur.fetchone()[0] or 0

        # Achievements list
        cur.execute("""
        SELECT id, achievement_type, title, description, evidence_type, evidence_id, evidence_metadata_json, awarded_at
        FROM learner_achievements
        WHERE student_id = ?
        ORDER BY awarded_at DESC
        """, (student_id,))
        ach_rows = cur.fetchall()
        achievements = []
        for r in ach_rows:
            meta = {}
            if r["evidence_metadata_json"]:
                try:
                    meta = json.loads(r["evidence_metadata_json"])
                except Exception:
                    pass
            achievements.append({
                "id": r["id"],
                "achievement_type": r["achievement_type"],
                "title": r["title"],
                "description": r["description"],
                "evidence_type": r["evidence_type"],
                "evidence_id": r["evidence_id"],
                "metadata": meta,
                "awarded_at": r["awarded_at"]
            })

        # Categorized counts
        counts = {
            "mission_completed": sum(1 for a in achievements if a["achievement_type"] == "MISSION_COMPLETION"),
            "delayed_recall": sum(1 for a in achievements if a["achievement_type"] == "DELAYED_RECALL"),
            "misconception_repaired": sum(1 for a in achievements if a["achievement_type"] == "MISCONCEPTION_REPAIR"),
            "topic_mastery": sum(1 for a in achievements if a["achievement_type"] == "TOPIC_MASTERY"),
            "personal_best": sum(1 for a in achievements if a["achievement_type"] == "PERSONAL_BEST"),
            "total_awarded": len(achievements)
        }

        conn.close()
        return {
            "student_id": student_id,
            "weekly_goal": {
                "goal_type": goal["goal_type"],
                "target_count": goal["target_count"],
                "achieved_count": completed_in_week,
                "is_met": completed_in_week >= goal["target_count"],
                "status": goal["status"],
                "week_range": f"{mon.isoformat()} to {sun.isoformat()}",
                "iso_week": iso_week
            },
            "counts": counts,
            "achievements": achievements
        }
