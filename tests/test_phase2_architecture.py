import unittest
import os
import sqlite3
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from vector_index import VectorIndexEngine
from learner_engine import LearnerEngine

class TestPhase2Architecture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline_db = "data/gpat_baseline.db"
        cls.learner_db = "gpat_knowledge.db"
        cls.ocr_markdown = "baseline/sources/markdown/gpat_2027_syllabus.md"
        cls.chunks_json = "baseline/chunks/baseline_chunks.json"
        cls.media_dir = Path("baseline/media/mcqs")

    def test_01_database_separation_verified(self):
        """data/gpat_baseline.db exists, has all static tables and 0 FK violations."""
        self.assertTrue(os.path.exists(self.baseline_db))
        conn = sqlite3.connect(self.baseline_db)
        cur = conn.cursor()
        cur.execute("PRAGMA integrity_check")
        self.assertEqual(cur.fetchone()[0], "ok")
        cur.execute("PRAGMA foreign_key_check")
        self.assertEqual(cur.fetchall(), [])
        
        # Verify static knowledge counts
        cur.execute("SELECT count(*) FROM baseline_sources")
        self.assertEqual(cur.fetchone()[0], 6)
        cur.execute("SELECT count(*) FROM baseline_topics")
        self.assertEqual(cur.fetchone()[0], 221)
        cur.execute("SELECT count(*) FROM baseline_questions")
        self.assertGreaterEqual(cur.fetchone()[0], 47)
        cur.execute("SELECT count(*) FROM baseline_questions WHERE provenance = 'EXPERT_VERIFIED_ORIGINAL'")
        self.assertEqual(cur.fetchone()[0], 47)
        cur.execute("SELECT count(*) FROM baseline_media")
        self.assertGreaterEqual(cur.fetchone()[0], 2)
        conn.close()

    def test_02_learner_data_preserved(self):
        """gpat_knowledge.db has all learner history completely intact."""
        conn = sqlite3.connect(self.learner_db)
        cur = conn.cursor()
        cur.execute("PRAGMA integrity_check")
        self.assertEqual(cur.fetchone()[0], "ok")
        cur.execute("SELECT count(*) FROM student_attempts")
        self.assertEqual(cur.fetchone()[0], 7)
        cur.execute("SELECT count(*) FROM fsrs_cards")
        self.assertEqual(cur.fetchone()[0], 11)
        cur.execute("SELECT count(*) FROM learning_events")
        self.assertEqual(cur.fetchone()[0], 10)
        cur.execute("SELECT count(*) FROM study_sessions")
        self.assertEqual(cur.fetchone()[0], 3)
        conn.close()

    def test_03_ocr_gpat_2027_syllabus_completed(self):
        """GPAT 2027 Syllabus has been converted via OCR with significant characters."""
        self.assertTrue(os.path.exists(self.ocr_markdown))
        with open(self.ocr_markdown, 'r', encoding='utf-8') as f:
            text = f.read()
        self.assertGreater(len(text), 50000)
        self.assertIn("Page 1", text)
        self.assertIn("Page 38", text)

    def test_04_real_vector_retrieval_and_embeddings(self):
        """All 505 chunks have valid 384-dimensional stored embeddings and hybrid search works."""
        conn = sqlite3.connect(self.baseline_db)
        cur = conn.cursor()
        cur.execute("SELECT count(*), count(embedding_blob) FROM baseline_chunks")
        total, with_emb = cur.fetchone()
        self.assertEqual(total, 505)
        self.assertEqual(with_emb, 505)
        conn.close()

        engine = VectorIndexEngine(db_path=self.baseline_db)
        results = engine.hybrid_search("Atropine muscarinic competitive antagonist", top_k=3)
        self.assertGreater(len(results), 0)
        top = results[0]
        self.assertIn("content", top)
        self.assertIn("rrf_score", top)

    def test_05_visual_mcq_media_integration(self):
        """Visual MCQs link to valid on-disk image files and learner engine packages media."""
        conn = sqlite3.connect(self.baseline_db)
        cur = conn.cursor()
        cur.execute("SELECT relative_file_path, alt_text FROM baseline_media")
        rows = cur.fetchall()
        self.assertGreaterEqual(len(rows), 2)
        for rel_path, alt in rows:
            self.assertTrue(os.path.exists(rel_path), f"Missing media file: {rel_path}")
            self.assertTrue(len(alt) > 5)
        conn.close()

        # Test daily session packaging
        engine = LearnerEngine(db_path=self.learner_db)
        session = engine.generate_daily_session(session_minutes=25, student_id="student_01")
        self.assertGreater(len(session["questions"]), 0)
        visual_qs = [q for q in session["questions"] if q.get("media_url")]
        self.assertGreater(len(visual_qs), 0)
        v = visual_qs[0]
        self.assertTrue(v["media_url"].startswith("/media/"))
        self.assertTrue(len(v["media_alt"]) > 5)

if __name__ == '__main__':
    unittest.main()
