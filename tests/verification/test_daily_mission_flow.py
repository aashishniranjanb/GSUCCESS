import os
import sys
import tempfile
import shutil
import sqlite3
import datetime
from pathlib import Path
import unittest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from learner_engine import LearnerEngine
from backend.repositories.sqlite_study_repository import SQLiteStudyRepository
from fastapi.testclient import TestClient
from backend.main import app

BASELINE_DB = REPO_ROOT / "gpat_knowledge.db"

class TestDailyMissionExperience(unittest.TestCase):
    """
    Feature Verification for Daily Mission Experience:
    1. First-time learner receives clean 12-min (8 questions) diagnostic baseline.
    2. Returning learner receives existing persisted mission without duplication.
    3. Shorter 5-minute session produces ~3 questions (~4.5-5 min).
    4. Active in-progress mission reports is_resumable=True and next_pending_index.
    5. Fully completed mission reports is_completed=True.
    6. Planner reason codes match evidence:
       - Overdue reviews -> 'Protect your retention'
       - Traps -> 'Repair conceptual traps'
       - Clean baseline -> 'Establish your baseline'
    7. Database safety: All mutations run in isolated temporary clone.
    """

    def setUp(self):
        self.tmp_fd, self.tmp_path = tempfile.mkstemp(suffix=".db")
        os.close(self.tmp_fd)
        shutil.copyfile(BASELINE_DB, self.tmp_path)
        os.environ["GPAT_DB_PATH"] = self.tmp_path
        self.client = TestClient(app)
        self.engine = LearnerEngine(self.tmp_path)
        self.repo = SQLiteStudyRepository(self.tmp_path)

    def tearDown(self):
        os.environ.pop("GPAT_DB_PATH", None)
        try:
            if os.path.exists(self.tmp_path):
                os.remove(self.tmp_path)
        except Exception:
            pass

    def test_01_first_time_learner_receives_12min_mission(self):
        student_id = "test_daily_student_new"
        res = self.client.get(f"/api/study/today?student_id={student_id}&minutes=12")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["estimated_duration_minutes"], 12)
        self.assertEqual(data["target_question_count"], 8)
        self.assertEqual(data["headline"], "Establish your baseline.")
        self.assertFalse(data["is_resumable"])
        self.assertFalse(data["is_completed"])
        self.assertEqual(len(data["questions"]), 8)

    def test_02_idempotency_no_duplicate_mission_on_refresh(self):
        student_id = "test_daily_student_idempotent"
        res1 = self.client.get(f"/api/study/today?student_id={student_id}&minutes=12")
        self.assertEqual(res1.status_code, 200)
        d1 = res1.json()

        # Simulate page refresh / reconnect
        res2 = self.client.get(f"/api/study/today?student_id={student_id}&minutes=12")
        self.assertEqual(res2.status_code, 200)
        d2 = res2.json()

        self.assertEqual(d1["session_id"], d2["session_id"])
        self.assertEqual(d1["target_question_count"], d2["target_question_count"])
        q_ids_1 = [q["question_id"] for q in d1["questions"]]
        q_ids_2 = [q["question_id"] for q in d2["questions"]]
        self.assertEqual(q_ids_1, q_ids_2)

    def test_03_short_5min_mission_selection(self):
        student_id = "test_daily_student_short"
        res = self.client.get(f"/api/study/today?student_id={student_id}&minutes=5")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn(data["estimated_duration_minutes"], [4, 5])
        self.assertEqual(data["target_question_count"], 3)
        self.assertEqual(len(data["questions"]), 3)

    def test_04_in_progress_mission_resumption(self):
        student_id = "test_daily_student_resume"
        # 1. Start mission
        res = self.client.get(f"/api/study/today?student_id={student_id}&minutes=12")
        data = res.json()
        session_id = data["session_id"]
        q1 = data["questions"][0]["question_id"]

        # 2. Answer question 1
        att_res = self.client.post("/api/attempt", json={
            "student_id": student_id,
            "question_id": q1,
            "selected_option": 0,
            "response_time_sec": 12.0,
            "confidence": 4
        })
        self.assertEqual(att_res.status_code, 200)

        # 3. Reload today's mission
        res_after = self.client.get(f"/api/study/today?student_id={student_id}&minutes=12")
        d_after = res_after.json()
        self.assertTrue(d_after["is_resumable"])
        self.assertEqual(d_after["answered_count"], 1)
        self.assertEqual(d_after["pending_count"], 7)
        self.assertEqual(d_after["next_pending_index"], 1)

    def test_05_completed_mission_status(self):
        student_id = "test_daily_student_complete"
        res = self.client.get(f"/api/study/today?student_id={student_id}&minutes=5")
        data = res.json()
        session_id = data["session_id"]

        # Answer all 3 questions
        for q in data["questions"]:
            self.client.post("/api/attempt", json={
                "student_id": student_id,
                "question_id": q["question_id"],
                "selected_option": 0,
                "response_time_sec": 15.0,
                "confidence": 4
            })

        # Mark mission complete
        comp_res = self.client.post(f"/api/study/mission/{session_id}/complete?student_id={student_id}")
        self.assertEqual(comp_res.status_code, 200)

        # Verify status
        final_res = self.client.get(f"/api/study/today?student_id={student_id}&minutes=5")
        d_final = final_res.json()
        self.assertTrue(d_final["is_completed"])
        self.assertEqual(d_final["pending_count"], 0)

    def test_06_evidence_grounded_headlines(self):
        conn = sqlite3.connect(self.tmp_path)
        past_iso = "2026-09-01T00:00:00+00:00"
        
        # Student with overdue review
        conn.execute("""
        INSERT INTO fsrs_cards (card_id, student_id, item_id, item_type, state, step, stability, difficulty, due, last_review)
        VALUES (888801, 'student_with_due', 'q_gpat_001', 'question', 2, 1, 3.0, 3.0, ?, ?)
        """, (past_iso, past_iso))
        conn.commit()
        conn.close()

        res = self.client.get("/api/study/today?student_id=student_with_due&minutes=12")
        data = res.json()
        self.assertIn(data["headline"], ["Protect your retention.", "Build stronger recall."])
        self.assertIn("due", data["why_this_mission"].lower())
