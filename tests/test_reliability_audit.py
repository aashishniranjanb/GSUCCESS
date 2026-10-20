import unittest
import json
import sqlite3
import tempfile
import shutil
from pathlib import Path

from backend.repositories.sqlite_study_repository import SQLiteStudyRepository
from learner_engine import LearnerEngine

class TestReliabilityAudit(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.db_path = self.test_dir / "test_gpat.db"

        # Initialize schema from main schema or active db
        conn = sqlite3.connect(str(self.db_path))
        cur = conn.cursor()
        
        # Core tables for persistence & learner
        cur.execute("""
        CREATE TABLE study_sessions (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            session_date TEXT NOT NULL,
            target_minutes INTEGER NOT NULL,
            status TEXT NOT NULL,
            started_at TEXT,
            completed_at TEXT,
            created_at TEXT NOT NULL,
            UNIQUE(user_id, session_date)
        )""")

        cur.execute("""
        CREATE TABLE study_session_items (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            question_id TEXT NOT NULL,
            concept_id TEXT,
            sequence INTEGER NOT NULL,
            source_type TEXT NOT NULL,
            status TEXT NOT NULL,
            presented_at TEXT,
            answered_at TEXT,
            is_correct INTEGER,
            FOREIGN KEY (session_id) REFERENCES study_sessions(id)
        )""")

        cur.execute("""
        CREATE TABLE learning_events (
            event_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            question_id TEXT,
            concept_id TEXT,
            timestamp TEXT NOT NULL,
            payload_json TEXT
        )""")

        cur.execute("""
        CREATE TABLE questions (
            id TEXT PRIMARY KEY,
            concept_id TEXT,
            question_type TEXT,
            difficulty INTEGER,
            question_text TEXT,
            options_json TEXT,
            correct_option INTEGER,
            distractor_reasons_json TEXT,
            explanation TEXT,
            source_page INTEGER,
            cue TEXT
        )""")

        cur.execute("""
        CREATE TABLE concepts (
            id TEXT PRIMARY KEY,
            name TEXT,
            domain_id TEXT,
            importance_score INTEGER,
            learning_objective TEXT,
            difficulty INTEGER
        )""")

        cur.execute("""
        CREATE TABLE student_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            question_id TEXT,
            concept_id TEXT,
            selected_option INTEGER,
            is_correct INTEGER,
            response_time_sec REAL,
            confidence INTEGER,
            hint_used INTEGER DEFAULT 0,
            calibration_category TEXT,
            error_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")

        cur.execute("""
        CREATE TABLE fsrs_cards (
            card_id TEXT PRIMARY KEY,
            student_id TEXT,
            item_id TEXT,
            item_type TEXT,
            state INTEGER,
            step INTEGER,
            stability REAL,
            difficulty REAL,
            due TEXT,
            last_review TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")

        cur.execute("""
        CREATE TABLE student_misconceptions (
            id TEXT PRIMARY KEY,
            student_id TEXT,
            concept_id TEXT,
            question_id TEXT,
            distractor_selected INTEGER,
            distractor_reason TEXT,
            error_type TEXT,
            occurrence_count INTEGER,
            status TEXT,
            first_detected TEXT,
            last_detected TEXT,
            resolved_at TEXT
        )""")

        cur.execute("""
        CREATE TABLE concept_memory_state (
            student_id TEXT,
            concept_id TEXT,
            stability REAL,
            difficulty REAL,
            retrievability REAL,
            mastery REAL,
            attempts INTEGER,
            correct INTEGER,
            misconception_count INTEGER,
            last_review TEXT,
            next_review TEXT,
            overconfidence_count INTEGER DEFAULT 0,
            PRIMARY KEY (student_id, concept_id)
        )""")

        # Insert seed question & concept
        cur.execute("""
        INSERT INTO concepts VALUES ('c_atropine', 'Atropine', 'ANS', 10, 'Muscarinic antagonist', 6)
        """)
        cur.execute("""
        INSERT INTO questions VALUES (
            'q_atropine_01', 'c_atropine', 'mechanism', 7,
            'What is the mechanism of atropine?',
            '["Competitive muscarinic antagonist", "Nicotinic antagonist", "AChE inhibitor", "Adrenergic agonist"]',
            0,
            '{"1": "Wrong receptor", "2": "Opposite action", "3": "Wrong system"}',
            'Atropine competitively blocks muscarinic acetylcholine receptors.',
            112,
            'Blocks M1-M5 receptors'
        )""")

        conn.commit()
        conn.close()

        self.repo = SQLiteStudyRepository(db_path=str(self.db_path))
        self.learner = LearnerEngine(db_path=str(self.db_path))

    def tearDown(self):
        try:
            shutil.rmtree(self.test_dir)
        except Exception:
            pass

    def test_session_immutability(self):
        questions = [{
            "question_id": "q_atropine_01",
            "concept_id": "c_atropine",
            "source_type": "high_yield"
        }]
        
        # 1. First persist
        sess_id = self.repo.persist_daily_session("student_test", "2026-10-15", 25, questions)
        self.assertTrue(sess_id.startswith("sess_2026-10-15_student_test"))

        # 2. Retrieve
        retrieved = self.repo.get_or_create_daily_session("student_test", "2026-10-15", 25)
        self.assertIsNotNone(retrieved)
        self.assertEqual(len(retrieved["questions"]), 1)
        self.assertEqual(retrieved["questions"][0]["question_id"], "q_atropine_01")

        # 3. Repeat retrieve must return the exact same persisted items (immutable)
        retrieved2 = self.repo.get_or_create_daily_session("student_test", "2026-10-15", 25)
        self.assertEqual(retrieved["session_id"], retrieved2["session_id"])
        self.assertEqual(retrieved["questions"][0]["question_id"], retrieved2["questions"][0]["question_id"])

    def test_learning_event_log(self):
        evt_id = self.repo.log_learning_event(
            user_id="student_test",
            event_type="QUESTION_ANSWERED",
            question_id="q_atropine_01",
            concept_id="c_atropine",
            payload={"selected_option": 0, "is_correct": True}
        )
        self.assertTrue(evt_id.startswith("evt_"))

        conn = sqlite3.connect(str(self.db_path))
        cur = conn.cursor()
        cur.execute("SELECT event_type, question_id, payload_json FROM learning_events WHERE event_id = ?", (evt_id,))
        row = cur.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], "QUESTION_ANSWERED")
        self.assertEqual(row[1], "q_atropine_01")
        payload = json.loads(row[2])
        self.assertTrue(payload["is_correct"])
        conn.close()

    def test_fsrs_attempt_recording(self):
        res = self.learner.record_attempt(
            student_id="student_test",
            question_id="q_atropine_01",
            selected_option=0,
            response_time_sec=11.5,
            confidence=5
        )
        self.assertTrue(res["is_correct"])
        self.assertEqual(res["calibration_category"], "SOLID_MASTERY")
        self.assertGreater(res["stability_days"], 0)

        # Check card in db
        conn = sqlite3.connect(str(self.db_path))
        cur = conn.cursor()
        cur.execute("SELECT stability, state FROM fsrs_cards WHERE student_id = ? AND item_id = ?", ("student_test", "q_atropine_01"))
        card = cur.fetchone()
        self.assertIsNotNone(card)
        self.assertGreater(card[0], 0)
        conn.close()

    def test_session_item_completion(self):
        questions = [{
            "question_id": "q_atropine_01",
            "concept_id": "c_atropine",
            "source_type": "high_yield"
        }]
        self.repo.persist_daily_session("student_test", "2026-10-15", 25, questions)
        
        # Mark answer
        self.repo.update_session_item_result("student_test", "q_atropine_01", True)

        conn = sqlite3.connect(str(self.db_path))
        cur = conn.cursor()
        cur.execute("SELECT status FROM study_sessions WHERE user_id = ? AND session_date = '2026-10-15'", ("student_test",))
        sess_status = cur.fetchone()[0]
        self.assertEqual(sess_status, "completed")
        conn.close()

if __name__ == "__main__":
    unittest.main()
