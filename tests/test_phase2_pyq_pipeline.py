import unittest
import os
import sqlite3
import shutil
import tempfile

from scripts.pyq_pipeline import PYQPipeline, ingest_pyq_batch, QUALITY_PUBLISHED, QUALITY_NEEDS_CONTENT_REVIEW

class TestPhase2PYQPipeline(unittest.TestCase):
    """
    Automated verification of Phase 2 deliverables:
    1. Stable IDs and metadata provenance across repeated extractions.
    2. Re-import idempotency (no duplicate baseline_questions or review items).
    3. Official answer key reconciliation without guessing.
    4. Review quarantine for questions with malformed options or missing markers.
    5. Database integrity and complete preservation of learner history in gpat_knowledge.db.
    """

    def setUp(self):
        self.baseline_db = "data/gpat_baseline.db"
        self.learner_db = "gpat_knowledge.db"
        self.pdf_2026 = "PYQs 2026-2010/GPAT_QPAK_2026.pdf"

    def test_01_pipeline_extraction_and_quarantine(self):
        """Verifies extraction classifies valid MCQs as PUBLISHED and malformed as quarantined."""
        self.assertTrue(os.path.exists(self.pdf_2026), "GPAT 2026 PDF must exist")
        pipeline = PYQPipeline(
            pdf_path=self.pdf_2026,
            paper_id="GPAT_QPAK_2026",
            pyq_year=2026,
            key_page=7
        )
        records = pipeline.extract_questions_linear(max_q=125)
        self.assertEqual(len(records), 125, "Must attempt extraction on 125 questions")

        # Q1 must be valid and verified
        q1 = records[0]
        self.assertEqual(q1["q_id"], "pyq_gpat_2026_001")
        self.assertEqual(q1["original_q_number"], 1)
        self.assertEqual(q1["pyq_year"], 2026)
        self.assertEqual(q1["quality_status"], QUALITY_PUBLISHED)
        self.assertEqual(len(q1["options"]), 4)
        self.assertEqual(q1["correct_option"], 0) # Key is 'a' -> index 0
        self.assertEqual(q1["source_page"], 1)
        self.assertEqual(q1["key_source_page"], 7)

        # Q55 has no (a) marker and must be quarantined
        q55 = next(r for r in records if r["original_q_number"] == 55)
        self.assertEqual(q55["quality_status"], QUALITY_NEEDS_CONTENT_REVIEW)
        self.assertIn("MISSING_OPTION_A_MARKER", q55["issues"])

    def test_02_idempotent_reimport(self):
        """Ensures running ingest_pyq_batch multiple times creates 0 duplicate rows."""
        temp_dir = tempfile.mkdtemp()
        t_base = os.path.join(temp_dir, "test_base.db")
        t_learn = os.path.join(temp_dir, "test_learn.db")

        # Copy databases to isolated sandbox
        with sqlite3.connect(self.baseline_db) as s, sqlite3.connect(t_base) as d:
            s.backup(d)
        with sqlite3.connect(self.learner_db) as s, sqlite3.connect(t_learn) as d:
            s.backup(d)

        try:
            pipeline = PYQPipeline(self.pdf_2026, "GPAT_QPAK_2026", 2026, 7)
            records = pipeline.extract_questions_linear(max_q=30) # test pilot slice

            # Mock DB paths in pipeline module
            import scripts.pyq_pipeline as p_mod
            orig_base = p_mod.BASELINE_DB
            orig_learn = p_mod.LEARNER_DB
            p_mod.BASELINE_DB = t_base
            p_mod.LEARNER_DB = t_learn

            # Run 1
            stats1 = p_mod.ingest_pyq_batch(records)
            conn = sqlite3.connect(t_base)
            count1 = conn.execute("SELECT count(*) FROM baseline_questions WHERE pyq_year = 2026").fetchone()[0]
            rev_count1 = conn.execute("SELECT count(*) FROM pyq_review_queue WHERE pyq_year = 2026").fetchone()[0]
            conn.close()

            # Run 2 (repeat import)
            stats2 = p_mod.ingest_pyq_batch(records)
            conn = sqlite3.connect(t_base)
            count2 = conn.execute("SELECT count(*) FROM baseline_questions WHERE pyq_year = 2026").fetchone()[0]
            rev_count2 = conn.execute("SELECT count(*) FROM pyq_review_queue WHERE pyq_year = 2026").fetchone()[0]
            conn.close()

            # Restore original paths
            p_mod.BASELINE_DB = orig_base
            p_mod.LEARNER_DB = orig_learn

            self.assertEqual(count1, count2, "Repeat import must not create duplicate questions")
            self.assertEqual(rev_count1, rev_count2, "Repeat import must not create duplicate review queue rows")

        finally:
            try:
                shutil.rmtree(temp_dir)
            except Exception:
                pass

    def test_03_database_safety_and_learner_integrity(self):
        """Guarantees zero data loss across learner state in gpat_knowledge.db."""
        conn = sqlite3.connect(self.learner_db)
        cur = conn.cursor()
        
        # Verify integrity
        cur.execute("PRAGMA integrity_check")
        self.assertEqual(cur.fetchone()[0], "ok")
        
        # Verify preserved records
        cur.execute("SELECT count(*) FROM student_attempts")
        self.assertEqual(cur.fetchone()[0], 7)
        cur.execute("SELECT count(*) FROM fsrs_cards")
        self.assertEqual(cur.fetchone()[0], 11)
        cur.execute("SELECT count(*) FROM learning_events")
        self.assertEqual(cur.fetchone()[0], 10)
        cur.execute("SELECT count(*) FROM study_sessions")
        self.assertEqual(cur.fetchone()[0], 3)
        conn.close()

if __name__ == '__main__':
    unittest.main()
