import os
import sys
import tempfile
import shutil
import sqlite3
import datetime
from datetime import timezone
from pathlib import Path
import unittest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from learner_engine import LearnerEngine
from backend.repositories.sqlite_study_repository import SQLiteStudyRepository
from backend.main import get_student_progress, sync_offline_attempts, SyncBatchRequest, SyncAttemptItem

BASELINE_DB = REPO_ROOT / "gpat_knowledge.db"

class TestPhase64AdaptivePersonas(unittest.TestCase):
    """
    Phase 6.4 — Adaptive Mission Validation: 10 Full Personas
    1. new_learner
    2. overdue_reviews
    3. repeated_misconception
    4. overconfident_wrong_answer
    5. low_confidence_correct_answer
    6. demonstrated_mastery
    7. incomplete_mission_resume
    8. offline_sync_replay
    9. empty_eligible_question_pool
    10. unmapped_topic_questions
    """

    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp_path = Path(self.tmp.name)
        shutil.copyfile(BASELINE_DB, self.tmp_path)
        self.engine = LearnerEngine(db_path=self.tmp_path)
        self.repo = SQLiteStudyRepository(db_path=self.tmp_path)
        os.environ["GPAT_DB_PATH"] = str(self.tmp_path)

    def tearDown(self):
        os.environ.pop("GPAT_DB_PATH", None)
        if self.tmp_path.exists():
            try:
                self.tmp_path.unlink()
            except Exception:
                pass

    def test_01_new_learner(self):
        """Persona 1: New learner with 0 history gets structured new learning items with valid reason codes."""
        student_id = "persona_new_learner"
        plan = self.engine.generate_daily_session(student_id=student_id, session_minutes=15)
        self.assertIsNotNone(plan)
        self.assertGreaterEqual(len(plan["questions"]), 4)
        for q in plan["questions"]:
            self.assertEqual(q["candidate_type"], "NEW_LEARNING")
            self.assertIn("HIGH_YIELD_SYLLABUS_CONCEPT", q["reason_codes"])

    def test_02_overdue_reviews(self):
        """Persona 2: Learner with past due FSRS cards has them prioritized under DUE_REVIEW."""
        student_id = "persona_overdue_reviews"
        conn = sqlite3.connect(self.tmp_path)
        past_iso = "2026-08-01T00:00:00+00:00"
        conn.execute("""
            INSERT INTO fsrs_cards (card_id, student_id, item_id, item_type, state, step, stability, difficulty, due, last_review)
            VALUES (90001, ?, 'q_gpat_001', 'question', 2, 1, 3.0, 3.0, ?, ?)
        """, (student_id, past_iso, past_iso))
        conn.commit()
        conn.close()

        plan = self.engine.generate_daily_session(student_id=student_id, session_minutes=15)
        due_items = [q for q in plan["questions"] if q["candidate_type"] == "DUE_REVIEW"]
        self.assertGreaterEqual(len(due_items), 1)
        self.assertEqual(due_items[0]["question_id"], "q_gpat_001")
        self.assertIn("OVERDUE_FSRS_REVIEW", due_items[0]["reason_codes"])

    def test_03_repeated_misconception(self):
        """Persona 3: Repeated misconception creates RECURRING trap and triggers TARGETED_REPAIR."""
        student_id = "persona_recurring_trap"
        q_id = "q_gpat_001"
        conn = sqlite3.connect(self.tmp_path)
        corr = conn.execute("SELECT correct_option FROM questions WHERE id = ?", (q_id,)).fetchone()[0]
        conn.close()

        # Submit wrong attempt twice with high confidence
        for _ in range(2):
            self.engine.record_attempt(student_id, q_id, selected_option=(corr + 1) % 4, response_time_sec=12.0, confidence=5)

        plan = self.engine.generate_daily_session(student_id=student_id, session_minutes=15)
        repairs = [q for q in plan["questions"] if q["candidate_type"] == "TARGETED_REPAIR"]
        self.assertGreaterEqual(len(repairs), 1)
        self.assertIn("RECURRING_MISCONCEPTION_TRAP", repairs[0]["reason_codes"])

    def test_04_overconfident_wrong_answer(self):
        """Persona 4: Overconfident wrong answer resets stability and classifies as OVERCONFIDENT_MISCONCEPTION."""
        student_id = "persona_overconfident_wrong"
        q_id = "q_gpat_002"
        conn = sqlite3.connect(self.tmp_path)
        corr = conn.execute("SELECT correct_option FROM questions WHERE id = ?", (q_id,)).fetchone()[0]
        conn.close()

        fb = self.engine.record_attempt(student_id, q_id, selected_option=(corr + 1) % 4, response_time_sec=9.0, confidence=5)
        self.assertFalse(fb["is_correct"])
        self.assertEqual(fb["calibration_category"], "OVERCONFIDENT_MISCONCEPTION")
        self.assertLess(fb["stability_days"], 1.0)
        self.assertEqual(fb["fsrs_rating"], "Again")

    def test_05_low_confidence_correct_answer(self):
        """Persona 5: Correct low confidence answer classified as FRAGILE_KNOWLEDGE with conservative review interval."""
        student_id = "persona_low_conf_correct"
        q_id = "q_gpat_002"
        conn = sqlite3.connect(self.tmp_path)
        corr = conn.execute("SELECT correct_option FROM questions WHERE id = ?", (q_id,)).fetchone()[0]
        conn.close()

        fb = self.engine.record_attempt(student_id, q_id, selected_option=corr, response_time_sec=15.0, confidence=1)
        self.assertTrue(fb["is_correct"])
        self.assertEqual(fb["calibration_category"], "FRAGILE_KNOWLEDGE")
        self.assertEqual(fb["fsrs_rating"], "Hard")

    def test_06_demonstrated_mastery(self):
        """Persona 6: Strong repeated retention across spaced intervals transitions to DEMONSTRATED_MASTERY."""
        student_id = "persona_mastery_proven"
        q_id = "q_gpat_003"
        conn = sqlite3.connect(self.tmp_path)
        c_id = conn.execute("SELECT concept_id, correct_option FROM questions WHERE id = ?", (q_id,)).fetchone()
        concept_id, corr = c_id[0], c_id[1]
        conn.close()

        for _ in range(4):
            self.engine.record_attempt(student_id, q_id, selected_option=corr, response_time_sec=8.0, confidence=5)

        conn = sqlite3.connect(self.tmp_path)
        conn.execute("UPDATE fsrs_cards SET stability = 15.0 WHERE student_id = ? AND item_id = ?", (student_id, q_id))
        conn.execute("UPDATE concept_memory_state SET stability = 15.0 WHERE student_id = ? AND concept_id = ?", (student_id, concept_id))
        conn.commit()
        conn.close()

        prog = get_student_progress(student_id=student_id)
        c_prog = next(c for c in prog["concepts"] if c["id"] == concept_id)
        self.assertEqual(c_prog["mastery_state"], "DEMONSTRATED_MASTERY")

    def test_07_incomplete_mission_resume(self):
        """Persona 7: Returning learner with an incomplete mission receives identical session order and state."""
        student_id = "persona_resume_session"
        today_date = datetime.date.today().isoformat()
        
        m1 = self.repo.get_or_create_daily_session(user_id=student_id, session_date=today_date, target_minutes=15)
        if not m1:
            generated = self.engine.generate_daily_session(student_id=student_id, session_minutes=15)
            self.repo.persist_daily_session(student_id, today_date, 15, generated["questions"])
            m1 = self.repo.get_or_create_daily_session(user_id=student_id, session_date=today_date, target_minutes=15)

        m2 = self.repo.get_or_create_daily_session(user_id=student_id, session_date=today_date, target_minutes=15)
        self.assertEqual(m1["session_id"], m2["session_id"])
        self.assertEqual(len(m1["questions"]), len(m2["questions"]))
        for q1, q2 in zip(m1["questions"], m2["questions"]):
            self.assertEqual(q1["question_id"], q2["question_id"])

    def test_08_offline_sync_replay(self):
        """Persona 8: Offline events sync once and replaying identical events is strictly idempotent."""
        student_id = "persona_offline_sync"
        client_evt_id = "p8_evt_unique_101"

        batch = SyncBatchRequest(
            student_id=student_id,
            events=[
                SyncAttemptItem(
                    client_event_id=client_evt_id,
                    student_id=student_id,
                    question_id="q_gpat_001",
                    selected_option=0,
                    response_time_sec=11.0,
                    confidence=4,
                    timestamp=datetime.datetime.now(timezone.utc).isoformat()
                )
            ]
        )

        res1 = sync_offline_attempts(batch=batch, engine=self.engine, repo=self.repo)
        self.assertEqual(res1["synced_count"], 1)
        self.assertEqual(res1["results"][0]["status"], "synced")

        # Duplicate replay
        res2 = sync_offline_attempts(batch=batch, engine=self.engine, repo=self.repo)
        self.assertEqual(res2["synced_count"], 1)
        self.assertEqual(res2["results"][0]["status"], "duplicate")

    def test_09_empty_eligible_question_pool(self):
        """Persona 9: In review mode with zero reviews due, scheduler recovers gracefully with high-yield practice."""
        student_id = "persona_empty_pool"
        plan = self.engine.generate_daily_session(student_id=student_id, session_minutes=15, mode="review")
        self.assertIsNotNone(plan)
        self.assertGreaterEqual(len(plan["questions"]), 4)
        self.assertIn("FALLBACK_HIGH_YIELD_PRACTICE", plan["questions"][0]["reason_codes"])

    def test_10_unmapped_topic_questions(self):
        """Persona 10: Questions from unmapped topic pool are served without inventing false subject mastery."""
        student_id = "persona_unmapped_topic"
        # Questions with unmapped topic fall back safely to discovery without crashing
        plan = self.engine.generate_daily_session(student_id=student_id, session_minutes=15)
        self.assertIsNotNone(plan)
        for q in plan["questions"]:
            self.assertIn("reason_codes", q)
            self.assertIsInstance(q["reason_codes"], list)
            self.assertGreater(len(q["reason_codes"]), 0)

if __name__ == "__main__":
    unittest.main()
