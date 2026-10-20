import unittest
import json
import os
import sqlite3
import shutil
import tempfile
from fastapi.testclient import TestClient

from backend.main import app
from learner_engine import LearnerEngine
from backend.repositories.sqlite_study_repository import SQLiteStudyRepository

class TestPYQPracticeFlow(unittest.TestCase):
    """
    Validates end-to-end PYQ practice & personalization pipeline:
    1. Staged official PYQ JSON validity and provenance.
    2. Baseline and Knowledge DB question integration with OFFICIAL_PYQ distinction.
    3. Practice session generation serving PYQs with options, cue, and explanations.
    4. Attempt submission updating FSRS stability, detecting calibration/misconceptions.
    5. Clean teardown ensuring test attempts don't pollute persistent databases.
    """

    def setUp(self):
        self.staged_path = "data/pyq_staging/gpat_2025_staged.json"
        self.baseline_db = "data/gpat_baseline.db"
        self.learner_db = "gpat_knowledge.db"
        self.client = TestClient(app)

    def test_01_staged_pyq_inventory_and_provenance(self):
        """Verifies staged questions from GPAT 2025 meet strict quality gate."""
        self.assertTrue(os.path.exists(self.staged_path), "Staged file must exist")
        with open(self.staged_path, "r", encoding="utf-8") as f:
            staged = json.load(f)
        
        self.assertGreaterEqual(len(staged), 60, "Expected at least 60 staged GPAT 2025 questions")
        for q in staged:
            self.assertEqual(q["provenance"], "OFFICIAL_PYQ")
            self.assertEqual(q["pyq_year"], 2025)
            self.assertEqual(q["verification_status"], "VERIFIED")
            self.assertEqual(len(q["options"]), 4, f"Question {q['id']} must have 4 options")
            self.assertIn(q["correct_option"], [0, 1, 2, 3])
            self.assertIsNotNone(q["explanation"])
            self.assertIn("distractor_reasons", q)
            self.assertGreaterEqual(len(q["distractor_reasons"]), 1)

    def test_02_database_pyq_integration(self):
        """Ensures OFFICIAL_PYQ questions are present in baseline database with complete metadata."""
        conn = sqlite3.connect(self.baseline_db)
        cur = conn.cursor()
        
        cur.execute("SELECT count(*) FROM baseline_questions WHERE provenance = 'OFFICIAL_PYQ'")
        pyq_count = cur.fetchone()[0]
        self.assertGreaterEqual(pyq_count, 60, "Must have at least 60 official PYQs in baseline")
        
        # Check specific question metadata
        cur.execute("""
        SELECT id, question_text, correct_option, cue, pyq_year, paper_id 
        FROM baseline_questions 
        WHERE provenance = 'OFFICIAL_PYQ' 
        LIMIT 1
        """)
        row = cur.fetchone()
        self.assertIsNotNone(row)
        self.assertTrue(row[0].startswith("pyq_gpat_2025_"))
        self.assertEqual(row[4], 2025)
        self.assertIn(row[5], ["gpat_2025", "GPAT_QPAK_2025"])
        conn.close()

    def test_03_practice_session_contains_rich_fields(self):
        """Verifies LearnerEngine session generator correctly packages options, cue, and questions."""
        # Test using LearnerEngine against learner DB
        engine = LearnerEngine(db_path=self.learner_db)
        session = engine.generate_daily_session(student_id="pyq_audit_student", session_minutes=15)
        self.assertIn("session_time_minutes", session)
        self.assertIn("questions", session)
        self.assertGreaterEqual(len(session["questions"]), 1)
        
        sample_q = session["questions"][0]
        self.assertIn("question_id", sample_q)
        self.assertIn("options", sample_q)
        self.assertIn("cue", sample_q)
        self.assertIn("concept_name", sample_q)

    def test_04_isolated_attempt_fsrs_and_calibration(self):
        """
        Tests attempt recording with confidence and FSRS stability calculation
        in an isolated temporary database to guarantee zero side-effects.
        """
        temp_dir = tempfile.mkdtemp()
        temp_db = os.path.join(temp_dir, "test_learning.db")
        
        # Copy schema and initial tables from learner db
        src = sqlite3.connect(self.learner_db)
        dst = sqlite3.connect(temp_db)
        src.backup(dst)
        src.close()
        dst.close()

        try:
            learner = LearnerEngine(db_path=temp_db)
            
            # Record an overconfident misconception attempt
            result = learner.record_attempt(
                student_id="isolated_student",
                question_id="pyq_gpat_2025_001",
                selected_option=1,       # Intentional wrong choice
                response_time_sec=5.0,
                confidence=5             # High confidence -> OVERCONFIDENT_MISCONCEPTION
            )
            
            self.assertFalse(result["is_correct"])
            self.assertEqual(result["calibration_category"], "OVERCONFIDENT_MISCONCEPTION")
            self.assertEqual(result["error_type"], "OVERCONFIDENCE")
            self.assertIn("stability_days", result)
            self.assertIn("distractor_reason", result)
            
            # Check card created in temp_db
            t_conn = sqlite3.connect(temp_db)
            t_cur = t_conn.cursor()
            t_cur.execute("SELECT stability, difficulty, state FROM fsrs_cards WHERE student_id = 'isolated_student'")
            card = t_cur.fetchone()
            self.assertIsNotNone(card)
            self.assertGreater(card[0], 0.0)
            t_conn.close()
            
        finally:
            shutil.rmtree(temp_dir)

if __name__ == '__main__':
    unittest.main()
