import unittest
import tempfile
import shutil
import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from learner_engine import LearnerEngine
from backend.repositories.sqlite_study_repository import SQLiteStudyRepository

BASELINE_DB = REPO_ROOT / "gpat_knowledge.db"

class TestGateCLearningLoop(unittest.TestCase):
    """
    Gate C Evidence:
    Verifies that the same verified question, attempt, learner-state update,
    and FSRS transition connect correctly end-to-end on an isolated disposable test database.
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

    def test_complete_learning_loop_closed(self):
        student_id = "gate_c_student"
        
        # 1. Generate study mission
        mission = self.engine.generate_daily_session(student_id=student_id, session_minutes=15)
        self.assertGreaterEqual(len(mission["questions"]), 4)
        target_q = mission["questions"][0]
        q_id = target_q.get("question_id") or target_q.get("id")
        c_id = target_q["concept_id"]

        # Fetch correct option for this question from db
        conn_init = sqlite3.connect(self.tmp_path)
        correct_opt = conn_init.execute("SELECT correct_option FROM questions WHERE id = ?", (q_id,)).fetchone()[0]
        conn_init.close()

        # 2. Record initial incorrect attempt with high confidence (overconfident misconception)
        fb1 = self.engine.record_attempt(
            student_id=student_id,
            question_id=q_id,
            selected_option=(correct_opt + 1) % 4, # incorrect option
            response_time_sec=11.2,
            confidence=5
        )
        self.assertFalse(fb1["is_correct"])
        self.assertEqual(fb1["calibration_category"], "OVERCONFIDENT_MISCONCEPTION")
        self.assertEqual(fb1["fsrs_rating"], "Again")
        
        # Check FSRS stability is collapsed for reset
        self.assertLess(fb1["stability_days"], 1.0)

        # 3. Verify concept memory state in database
        conn = sqlite3.connect(self.tmp_path)
        cur = conn.cursor()
        cur.execute("SELECT mastery, misconception_count, overconfidence_count FROM concept_memory_state WHERE student_id = ? AND concept_id = ?", (student_id, c_id))
        row = cur.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], 0.0) # mastery = 0
        self.assertEqual(row[1], 1)   # misconception_count = 1
        self.assertEqual(row[2], 1)   # overconfidence_count = 1

        # 4. Generate targeted repair mission: system must prioritize this misconception
        repair_mission = self.engine.generate_daily_session(student_id=student_id, session_minutes=15, mode="balanced")
        top_q = repair_mission["questions"][0]
        self.assertEqual(top_q["concept_id"], c_id)
        self.assertIn("RECURRING_MISCONCEPTION_TRAP", top_q["reason_codes"])
        self.assertEqual(top_q["candidate_type"], "TARGETED_REPAIR")

        # 5. Answer correctly on repair
        fb2 = self.engine.record_attempt(
            student_id=student_id,
            question_id=q_id,
            selected_option=correct_opt,
            response_time_sec=14.0,
            confidence=4
        )
        self.assertTrue(fb2["is_correct"])
        self.assertEqual(fb2["calibration_category"], "SOLID_MASTERY")
        self.assertGreater(fb2["stability_days"], fb1["stability_days"]) # FSRS stability increased

        # 6. Verify mastery updated
        cur.execute("SELECT mastery, attempts, correct FROM concept_memory_state WHERE student_id = ? AND concept_id = ?", (student_id, c_id))
        row2 = cur.fetchone()
        self.assertEqual(row2[0], 0.5) # 1 correct / 2 attempts = 0.5
        self.assertEqual(row2[1], 2)
        self.assertEqual(row2[2], 1)
        conn.close()

if __name__ == "__main__":
    unittest.main()
