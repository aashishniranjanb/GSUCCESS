import sys
import sqlite3
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.evaluation.mock_blueprint import MockBlueprint, PROVISIONAL_MOCK_25
from backend.evaluation.mock_scorer import MockScorer
from backend.evaluation.mock_engine import MockExamEngine

DB_PATH = Path(__file__).resolve().parent.parent.parent / "gpat_knowledge.db"

import unittest

class TestMockEngine(unittest.TestCase):
    def test_mock_blueprint(self):
        bp = PROVISIONAL_MOCK_25
        self.assertEqual(bp.total_questions, 25)
        self.assertEqual(bp.duration_minutes, 45)
        self.assertEqual(bp.marks_per_question, 4.0)
        self.assertEqual(bp.negative_marks, 1.0)
        self.assertEqual(bp.exam_version, "PROVISIONAL_MOCK")

    def test_mock_scoring_calculation(self):
        blueprint = {
            "marks_per_question": 4.0,
            "negative_marks": 1.0
        }
        items = [
            {"question_id": "q1", "concept_id": "c1", "domain_id": "d1", "question_type": "mcq"},
            {"question_id": "q2", "concept_id": "c1", "domain_id": "d1", "question_type": "mcq"},
            {"question_id": "q3", "concept_id": "c2", "domain_id": "d2", "question_type": "mcq"},
            {"question_id": "q4", "concept_id": "c2", "domain_id": "d2", "question_type": "mcq"}
        ]
        attempts = [
            {"question_id": "q1", "selected_option": 0, "is_correct": True, "time_spent_ms": 15000, "confidence": 5},
            {"question_id": "q2", "selected_option": 2, "is_correct": False, "time_spent_ms": 10000, "confidence": 4},
            {"question_id": "q3", "selected_option": 0, "is_correct": True, "time_spent_ms": 46000, "confidence": 2}
        ]

        res = MockScorer.evaluate_mock_session(
            blueprint_config=blueprint,
            items=items,
            attempts=attempts,
            started_at="2026-10-15T10:00:00Z",
            submitted_at="2026-10-15T10:20:00Z"
        )

        summary = res["summary"]
        self.assertEqual(summary["attempted"], 3)
        self.assertEqual(summary["unattempted"], 1)
        self.assertEqual(summary["correct"], 2)
        self.assertEqual(summary["incorrect"], 1)
        self.assertEqual(summary["raw_score"], 7.0)
        self.assertEqual(summary["max_possible_score"], 16.0)
        self.assertEqual(summary["accuracy_percent"], 66.7)

        quadrants = res["timing_analysis"]["quadrants"]
        self.assertEqual(quadrants["fast_correct"], 1)
        self.assertEqual(quadrants["slow_correct"], 1)
        self.assertEqual(quadrants["fast_incorrect"], 1)

    def test_mock_engine_lifecycle(self):
        import tempfile
        import shutil
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            tmp_path = Path(tmp.name)
        try:
            shutil.copyfile(DB_PATH, tmp_path)
            engine = MockExamEngine(db_path=tmp_path)
            created = engine.create_mock_exam(user_id="test_student", blueprint_name="sprint_25")
            exam_id = created["exam_id"]
            self.assertEqual(created["status"], "CREATED")
            self.assertGreater(created["total_questions"], 0)

            # Start
            started = engine.start_mock_exam(exam_id=exam_id, user_id="test_student")
            self.assertEqual(started["status"], "IN_PROGRESS")
            self.assertGreater(started["remaining_seconds"], 0)

            # Retrieve
            mock_data = engine.get_mock_exam(exam_id=exam_id, user_id="test_student")
            self.assertEqual(mock_data["exam_id"], exam_id)
            self.assertGreater(len(mock_data["questions"]), 0)

            # Answer first question
            first_q = mock_data["questions"][0]
            ans_res = engine.record_mock_answer(
                exam_id=exam_id,
                user_id="test_student",
                question_id=first_q["question_id"],
                selected_option=0,
                time_spent_ms=18000,
                confidence=4
            )
            self.assertEqual(ans_res["status"], "saved")

            # Pause
            paused = engine.pause_mock_exam(exam_id=exam_id, user_id="test_student")
            self.assertEqual(paused["status"], "PAUSED")

            # Submit
            eval_res = engine.submit_mock_exam(exam_id=exam_id, user_id="test_student")
            self.assertEqual(eval_res["status"], "EVALUATED")
            self.assertIn("summary", eval_res)
            self.assertIn("timing_analysis", eval_res)
            self.assertIn("recommended_repairs", eval_res)
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

if __name__ == "__main__":
    unittest.main()
