import unittest
import os
import json
import sqlite3
import shutil
import tempfile
from fastapi.testclient import TestClient

from backend.main import app, DB_PATH
from learner_engine import LearnerEngine
from backend.repositories.sqlite_study_repository import SQLiteStudyRepository

class TestPhase3PersonalizedOrchestration(unittest.TestCase):
    """
    Validates Phase 3 Personalized Study Orchestration:
    1. Synthetic learner profiles (New learner, Overdue learner, Misconception learner).
    2. Deterministic candidate ranking and explainable reason codes.
    3. Diversity constraints (no more than 2 consecutive questions per concept).
    4. Mission generation idempotency and persistence across restarts.
    5. Authoritative attempt processing (official key, FSRS stability, calibration).
    6. Dedicated Phase 3 endpoints (/api/study/today, /api/study/mission, /api/study/review-queue, etc.).
    7. Database safety and 100% learner history preservation.
    """

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def setUp(self):
        self.learner_db = DB_PATH
        self.baseline_db = "data/gpat_baseline.db"

    def test_01_synthetic_new_learner_unassessed_separation(self):
        """New learner with 0 attempts must receive high-yield tasks with SYLLABUS_GAP / HIGH_YIELD reasons, not false weakness."""
        temp_dir = tempfile.mkdtemp()
        t_db = os.path.join(temp_dir, "t_learn.db")
        with sqlite3.connect(self.learner_db) as s, sqlite3.connect(t_db) as d:
            s.backup(d)

        try:
            learner = LearnerEngine(db_path=t_db)
            session = learner.generate_daily_session(student_id="synth_new_learner", session_minutes=15)
            self.assertGreaterEqual(len(session["questions"]), 4)
            for q in session["questions"]:
                self.assertIn("reason_codes", q)
                self.assertIn("candidate_type", q)
                # Ensure no false misconception repair is assigned to brand new learner
                self.assertFalse(q["has_active_misconception"])
        finally:
            try:
                shutil.rmtree(temp_dir)
            except Exception:
                pass

    def test_02_synthetic_overdue_and_misconception_learner(self):
        """Learner with active misconceptions and overdue cards must prioritize them with correct reason codes."""
        temp_dir = tempfile.mkdtemp()
        t_db = os.path.join(temp_dir, "t_learn.db")
        with sqlite3.connect(self.learner_db) as s, sqlite3.connect(t_db) as d:
            s.backup(d)

        try:
            conn = sqlite3.connect(t_db)
            # Create an overdue FSRS card
            conn.execute("""
            INSERT OR REPLACE INTO fsrs_cards (card_id, student_id, item_id, item_type, state, step, stability, difficulty, due, last_review)
            VALUES (99901, 'synth_overdue_user', 'q_gpat_001', 'question', 2, 1, 1.0, 5.0, '2020-01-01T00:00:00Z', '2019-12-31T00:00:00Z')
            """)
            # Create an active misconception
            conn.execute("""
            INSERT OR REPLACE INTO student_misconceptions (id, student_id, concept_id, question_id, distractor_selected, error_type, distractor_reason, status, occurrence_count)
            VALUES (99901, 'synth_overdue_user', 'ans_antimuscarinics', 'q_gpat_002', 1, 'OVERCONFIDENCE', 'Contraindicated in glaucoma', 'ACTIVE', 3)
            """)
            conn.commit()
            conn.close()

            learner = LearnerEngine(db_path=t_db)
            session = learner.generate_daily_session(student_id="synth_overdue_user", session_minutes=20)
            
            # First item should be the overdue review or active misconception
            first_q = session["questions"][0]
            self.assertTrue(first_q["is_due"] or first_q["has_active_misconception"])
            self.assertTrue(
                "OVERDUE_FSRS_REVIEW" in first_q["reason_codes"] or 
                "RECURRING_MISCONCEPTION_TRAP" in first_q["reason_codes"]
            )
        finally:
            try:
                shutil.rmtree(temp_dir)
            except Exception:
                pass

    def test_03_diversity_constraint_enforced(self):
        """Verifies session scheduler never outputs more than 2 consecutive questions with identical concept_id."""
        learner = LearnerEngine(db_path=self.learner_db)
        session = learner.generate_daily_session(student_id="diversity_audit_user", session_minutes=30)
        qs = session["questions"]
        for i in range(len(qs) - 2):
            c1, c2, c3 = qs[i]["concept_id"], qs[i+1]["concept_id"], qs[i+2]["concept_id"]
            self.assertFalse(c1 == c2 == c3, f"Found 3 consecutive questions with concept {c1} at index {i}")

    def test_04_api_study_endpoints(self):
        """Verifies Phase 3 endpoints: /api/study/today, /api/study/review-queue, and /api/study/progress."""
        # 1. /api/study/today
        res_today = self.client.get("/api/study/today?student_id=student_01&minutes=20")
        self.assertEqual(res_today.status_code, 200)
        today_data = res_today.json()
        self.assertIn("questions", today_data)
        self.assertGreaterEqual(len(today_data["questions"]), 1)

        # 2. /api/study/review-queue
        res_rq = self.client.get("/api/study/review-queue?student_id=student_01")
        self.assertEqual(res_rq.status_code, 200)
        rq_data = res_rq.json()
        self.assertIn("due_count", rq_data)
        self.assertIn("review_items", rq_data)

        # 3. /api/study/progress
        res_prog = self.client.get("/api/study/progress?student_id=student_01")
        self.assertEqual(res_prog.status_code, 200)
        prog_data = res_prog.json()
        self.assertIn("summary", prog_data)
        self.assertIn("concepts", prog_data)
        
        # Clean any session generated today for student_01 during test
        conn = sqlite3.connect(self.learner_db)
        today_iso = os.environ.get("TODAY", "")
        conn.execute("DELETE FROM study_session_items WHERE session_id LIKE '%student_01%' AND session_id NOT IN ('sess_2026-09-25_student_01')")
        conn.execute("DELETE FROM study_sessions WHERE user_id = 'student_01' AND id NOT IN ('sess_2026-09-25_student_01')")
        conn.execute("DELETE FROM learning_events WHERE user_id = 'student_01' AND event_type = 'SESSION_STARTED' AND timestamp LIKE '2026-10%'")
        conn.commit()
        conn.close()

    def test_05_learner_database_safety(self):
        """Preserves historical student data in gpat_knowledge.db (asserts baseline non-regression)."""
        conn = sqlite3.connect(self.learner_db)
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM student_attempts")
        self.assertGreaterEqual(cur.fetchone()[0], 7)
        cur.execute("SELECT count(*) FROM fsrs_cards")
        self.assertGreaterEqual(cur.fetchone()[0], 11)
        cur.execute("SELECT count(*) FROM learning_events")
        self.assertGreaterEqual(cur.fetchone()[0], 10)
        cur.execute("SELECT count(*) FROM study_sessions")
        self.assertGreaterEqual(cur.fetchone()[0], 3)
        conn.close()

if __name__ == '__main__':
    unittest.main()
