import unittest
import sqlite3
import json
import os
import shutil
import tempfile
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.evaluation.mock_blueprint import OFFICIAL_GPAT_125, BLUEPRINTS
from backend.evaluation.mock_engine import MockExamEngine

DB_PATH = Path("gpat_knowledge.db")

class TestOfficial125MockExam(unittest.TestCase):
    """
    Verifies that the mock exam engine supports full 125Q GPAT simulation
    without errors, correctly samples from available verified questions,
    scores with +4 / -1 negative marking, and tracks remaining time.
    """

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.tmp_db = Path(self.temp_dir) / "test_knowledge.db"
        shutil.copyfile(DB_PATH, self.tmp_db)
        self.engine = MockExamEngine(db_path=self.tmp_db)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_official_125_blueprint_parameters(self):
        bp = OFFICIAL_GPAT_125
        self.assertEqual(bp.total_questions, 125)
        self.assertEqual(bp.duration_minutes, 180)
        self.assertEqual(bp.marks_per_question, 4.0)
        self.assertEqual(bp.negative_marks, 1.0)
        self.assertEqual(bp.exam_version, "OFFICIAL_EXAM_SIMULATION")

    def test_create_and_run_official_125_mock(self):
        created = self.engine.create_mock_exam(user_id="test_candidate", blueprint_name="official_125")
        exam_id = created["exam_id"]
        self.assertEqual(created["status"], "CREATED")
        self.assertEqual(created["total_questions"], 125)
        self.assertEqual(created["duration_seconds"], 180 * 60)

        started = self.engine.start_mock_exam(exam_id=exam_id, user_id="test_candidate")
        self.assertEqual(started["status"], "IN_PROGRESS")
        self.assertEqual(started["remaining_seconds"], 180 * 60)

        mock_data = self.engine.get_mock_exam(exam_id=exam_id, user_id="test_candidate")
        self.assertEqual(len(mock_data["questions"]), 125)
        
        # Verify first 3 questions have options and IDs
        for q in mock_data["questions"][:3]:
            self.assertIn("question_id", q)
            self.assertIn("options", q)
            self.assertGreaterEqual(len(q["options"]), 2)

        # Answer 5 questions: 3 correct, 2 incorrect
        conn = sqlite3.connect(self.tmp_db)
        c = conn.cursor()
        for idx in range(5):
            q = mock_data["questions"][idx]
            c.execute("SELECT correct_option FROM questions WHERE id = ?", (q["question_id"],))
            corr = c.fetchone()[0]
            selected = corr if idx < 3 else (corr + 1) % 4
            self.engine.record_mock_answer(
                exam_id=exam_id,
                user_id="test_candidate",
                question_id=q["question_id"],
                selected_option=selected,
                time_spent_ms=25000,
                confidence=4
            )
        conn.close()

        # Submit
        result = self.engine.submit_mock_exam(exam_id=exam_id, user_id="test_candidate")
        self.assertEqual(result["status"], "EVALUATED")
        summary = result["summary"]
        self.assertEqual(summary["attempted"], 5)
        self.assertEqual(summary["correct"], 3)
        self.assertEqual(summary["incorrect"], 2)
        # 3 * 4 - 2 * 1 = 10.0
        self.assertEqual(summary["raw_score"], 10.0)
        self.assertEqual(summary["max_possible_score"], 500.0)

if __name__ == "__main__":
    unittest.main()
