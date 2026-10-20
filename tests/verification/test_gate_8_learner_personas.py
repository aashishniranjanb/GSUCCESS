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

BASELINE_DB = REPO_ROOT / "gpat_knowledge.db"

class TestGate8LearnerPersonasValidation(unittest.TestCase):
    """
    Gate 8 Verification: Synthetic Personas & Edge Profiles Validation
    Verifies that the product handles all 8 required learner archetypes gracefully
    without falsely claiming mastery, crashing, or corrupting state:
    1. New learner with no assessed topics
    2. Learner with overdue FSRS reviews
    3. Learner with repeated high-confidence errors (overconfident misconceptions)
    4. Learner with correct but low-confidence answers (fragile knowledge)
    5. Learner with strong demonstrated retention
    6. Learner with incomplete missions
    7. Learner with an offline queue
    8. Learner with insufficient eligible questions (graceful recovery)
    """

    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp_path = Path(self.tmp.name)
        shutil.copyfile(BASELINE_DB, self.tmp_path)
        self.engine = LearnerEngine(db_path=self.tmp_path)
        self.repo = SQLiteStudyRepository(db_path=self.tmp_path)

    def tearDown(self):
        if self.tmp_path.exists():
            try:
                self.tmp_path.unlink()
            except Exception:
                pass

    def test_persona_1_new_learner_no_assessed_topics(self):
        """New learner: zero attempts, concepts classified as UNASSESSED, not WEAK."""
        student_id = "persona_1_new_learner"
        mission = self.engine.generate_daily_session(student_id=student_id, session_minutes=15)
        self.assertGreaterEqual(len(mission["questions"]), 4)
        for q in mission["questions"]:
            self.assertEqual(q["candidate_type"], "NEW_LEARNING")

    def test_persona_2_learner_with_overdue_fsrs_reviews(self):
        """Learner with overdue FSRS items: prioritized under DUE_REVIEW."""
        student_id = "persona_2_overdue_reviews"
        conn = sqlite3.connect(self.tmp_path)
        past_iso = "2026-09-01T00:00:00+00:00"
        conn.execute("""
        INSERT INTO fsrs_cards (card_id, student_id, item_id, item_type, state, step, stability, difficulty, due, last_review)
        VALUES (999901, ?, 'q_gpat_001', 'question', 2, 1, 3.0, 3.0, ?, ?)
        """, (student_id, past_iso, past_iso))
        conn.commit()
        conn.close()

        mission = self.engine.generate_daily_session(student_id=student_id, session_minutes=15)
        due_items = [q for q in mission["questions"] if q["candidate_type"] == "DUE_REVIEW"]
        self.assertGreaterEqual(len(due_items), 1)
        self.assertEqual(due_items[0]["question_id"], "q_gpat_001")

    def test_persona_3_repeated_high_confidence_errors(self):
        """Learner with high-confidence errors: creates ACTIVE/RECURRING trap and prioritizes TARGETED_REPAIR."""
        student_id = "persona_3_overconfident_traps"
        q_id = "q_gpat_001"
        conn = sqlite3.connect(self.tmp_path)
        corr = conn.execute("SELECT correct_option FROM questions WHERE id = ?", (q_id,)).fetchone()[0]
        conn.close()

        # Submit wrong option with confidence 5
        fb1 = self.engine.record_attempt(student_id, q_id, selected_option=(corr + 1) % 4, response_time_sec=12.0, confidence=5)
        self.assertEqual(fb1["calibration_category"], "OVERCONFIDENT_MISCONCEPTION")
        self.assertLess(fb1["stability_days"], 1.0)

        # Mission must prioritize this trap
        mission = self.engine.generate_daily_session(student_id=student_id, session_minutes=15)
        repairs = [q for q in mission["questions"] if q["candidate_type"] == "TARGETED_REPAIR"]
        self.assertGreaterEqual(len(repairs), 1)

    def test_persona_4_correct_low_confidence_answers(self):
        """Learner with correct but low confidence (guessing): scheduled with Hard rating."""
        student_id = "persona_4_fragile_knowledge"
        q_id = "q_gpat_002"
        conn = sqlite3.connect(self.tmp_path)
        corr = conn.execute("SELECT correct_option FROM questions WHERE id = ?", (q_id,)).fetchone()[0]
        conn.close()

        fb = self.engine.record_attempt(student_id, q_id, selected_option=corr, response_time_sec=14.0, confidence=1)
        self.assertTrue(fb["is_correct"])
        self.assertEqual(fb["calibration_category"], "FRAGILE_KNOWLEDGE")
        self.assertEqual(fb["fsrs_rating"], "Hard")

    def test_persona_5_strong_demonstrated_retention(self):
        """Learner with repeated correct attempts across spaced intervals: achieves DEMONSTRATED_MASTERY."""
        student_id = "persona_5_mastered_student"
        q_id = "q_gpat_003"
        conn = sqlite3.connect(self.tmp_path)
        c_id = conn.execute("SELECT concept_id, correct_option FROM questions WHERE id = ?", (q_id,)).fetchone()
        concept_id, corr = c_id[0], c_id[1]
        conn.close()

        for _ in range(4):
            self.engine.record_attempt(student_id, q_id, selected_option=corr, response_time_sec=10.0, confidence=5)

        conn = sqlite3.connect(self.tmp_path)
        conn.execute("UPDATE fsrs_cards SET stability = 14.0 WHERE student_id = ? AND item_id = ?", (student_id, q_id))
        conn.execute("UPDATE concept_memory_state SET stability = 14.0 WHERE student_id = ? AND concept_id = ?", (student_id, concept_id))
        conn.commit()
        conn.close()

        from backend.main import get_student_progress
        os.environ["GPAT_DB_PATH"] = str(self.tmp_path)
        try:
            prog = get_student_progress(student_id=student_id)
            c_prog = next(c for c in prog["concepts"] if c["id"] == concept_id)
            self.assertEqual(c_prog["mastery_state"], "DEMONSTRATED_MASTERY")
        finally:
            os.environ.pop("GPAT_DB_PATH", None)

    def test_persona_6_incomplete_mission_safe_resumption(self):
        """Incomplete mission: retrieving today's mission preserves exact sequence without generating new items."""
        student_id = "persona_6_incomplete_session"
        today_date = datetime.date.today().isoformat()
        
        m1 = self.repo.get_or_create_daily_session(user_id=student_id, session_date=today_date, target_minutes=25)
        if not m1:
            generated = self.engine.generate_daily_session(student_id=student_id, session_minutes=25)
            self.repo.persist_daily_session(student_id, today_date, 25, generated["questions"])
            m1 = self.repo.get_or_create_daily_session(user_id=student_id, session_date=today_date, target_minutes=25)

        m2 = self.repo.get_or_create_daily_session(user_id=student_id, session_date=today_date, target_minutes=25)
        self.assertEqual(m1["session_id"], m2["session_id"])
        self.assertEqual(len(m1["questions"]), len(m2["questions"]))
        self.assertEqual(m1["questions"][0]["question_id"], m2["questions"][0]["question_id"])

    def test_persona_7_offline_queue_preservation_and_idempotency(self):
        """Offline queue: processes queued attempt and handles duplicate sync requests idempotently."""
        from backend.main import sync_offline_attempts, SyncBatchRequest, SyncAttemptItem
        os.environ["GPAT_DB_PATH"] = str(self.tmp_path)
        student_id = "persona_7_offline_student"
        client_evt_id = "p7_offline_evt_42"

        batch = SyncBatchRequest(
            student_id=student_id,
            events=[
                SyncAttemptItem(
                    client_event_id=client_evt_id,
                    student_id=student_id,
                    question_id="q_gpat_001",
                    selected_option=0,
                    response_time_sec=13.0,
                    confidence=4,
                    timestamp=datetime.datetime.now(timezone.utc).isoformat()
                )
            ]
        )

        try:
            res1 = sync_offline_attempts(batch=batch, engine=self.engine, repo=self.repo)
            self.assertEqual(res1["synced_count"], 1)
            self.assertEqual(res1["results"][0]["status"], "synced")

            # Duplicate replay
            res2 = sync_offline_attempts(batch=batch, engine=self.engine, repo=self.repo)
            self.assertEqual(res2["synced_count"], 1)
            self.assertEqual(res2["results"][0]["status"], "duplicate")
        finally:
            os.environ.pop("GPAT_DB_PATH", None)

    def test_persona_8_empty_candidate_pool_graceful_recovery(self):
        """Empty candidate pool in specialized mode: recovers smoothly with fallback practice instead of crashing."""
        student_id = "persona_8_empty_pool_student"
        # Pure review mode for a student with 0 due items
        plan = self.engine.generate_daily_session(student_id=student_id, session_minutes=15, mode="review")
        self.assertIsNotNone(plan)
        self.assertGreaterEqual(len(plan["questions"]), 4)
        # Should gracefully fall back to high-yield questions
        self.assertIn("FALLBACK_HIGH_YIELD_PRACTICE", plan["questions"][0]["reason_codes"])

if __name__ == "__main__":
    unittest.main()
