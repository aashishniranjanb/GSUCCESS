import unittest
import os
import json
import sqlite3

class TestBaselineBuild(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db_path = "gpat_knowledge.db"
        cls.manifest_path = "baseline/source_manifest.json"
        cls.subjects_path = "baseline/subjects.json"
        cls.topics_path = "baseline/topics.json"
        cls.weightage_path = "baseline/weightage_evidence.json"
        cls.graph_path = "baseline/baseline_graph.json"
        cls.chunks_path = "baseline/chunks/baseline_chunks.json"

    def test_01_manifest_and_markdown_exist(self):
        """Every PDF must have a manifest record and markdown output."""
        self.assertTrue(os.path.exists(self.manifest_path))
        with open(self.manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        self.assertEqual(len(manifest), 6)
        for s in manifest:
            self.assertTrue(len(s["sha256"]) == 64)
            self.assertTrue(os.path.exists(s["markdown_output_path"]))
            self.assertIn(s["conversion_status"], ["SUCCESS", "PARTIAL"])

    def test_02_subject_and_topic_records(self):
        """Subject and topic records have stable IDs and source provenance."""
        with open(self.subjects_path, 'r', encoding='utf-8') as f:
            subjects = json.load(f)
        self.assertEqual(len(subjects), 5)
        for sub in subjects:
            self.assertIn("subject_id", sub)
            self.assertTrue(len(sub["source_ids"]) > 0)

        with open(self.topics_path, 'r', encoding='utf-8') as f:
            topics = json.load(f)
        self.assertGreaterEqual(len(topics), 200)
        for t in topics:
            self.assertIn("topic_id", t)
            self.assertIn("subject_id", t)
            self.assertTrue(len(t["source_ids"]) > 0)

    def test_03_weightage_authority_separation(self):
        """No third-party estimate is mislabelled as official verified."""
        with open(self.weightage_path, 'r', encoding='utf-8') as f:
            weightage = json.load(f)
        self.assertGreaterEqual(len(weightage), 10)
        for w in weightage:
            if "pk_classes" in w["source_id"]:
                self.assertNotEqual(w["authority_status"], "OFFICIAL_VERIFIED")

    def test_04_graph_endpoints_valid(self):
        """Every edge in the baseline graph must connect to existing nodes."""
        with open(self.graph_path, 'r', encoding='utf-8') as f:
            graph = json.load(f)
        node_ids = {n["id"] for n in graph["nodes"]}
        self.assertGreater(len(node_ids), 200)
        for edge in graph["edges"]:
            self.assertIn(edge["source"], node_ids)
            self.assertIn(edge["target"], node_ids)

    def test_05_chunks_provenance(self):
        """Every chunk links to a valid source ID."""
        with open(self.chunks_path, 'r', encoding='utf-8') as f:
            chunks = json.load(f)
        self.assertGreaterEqual(len(chunks), 400)
        for c in chunks:
            self.assertIn("source_id", c)
            self.assertIn("source_hash", c)
            self.assertEqual(c["embedding_dimensions"], 384)

    def test_06_database_tables_and_learner_integrity(self):
        """Baseline tables populated and all learner data preserved."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        # Check integrity
        cur.execute("PRAGMA integrity_check")
        self.assertEqual(cur.fetchone()[0], "ok")
        cur.execute("PRAGMA foreign_key_check")
        self.assertEqual(cur.fetchall(), [])

        # Check learner data preserved
        cur.execute("SELECT count(*) FROM student_attempts")
        self.assertEqual(cur.fetchone()[0], 7)
        cur.execute("SELECT count(*) FROM fsrs_cards")
        self.assertEqual(cur.fetchone()[0], 11)
        cur.execute("SELECT count(*) FROM learning_events")
        self.assertEqual(cur.fetchone()[0], 10)
        cur.execute("SELECT count(*) FROM study_sessions")
        self.assertEqual(cur.fetchone()[0], 3)
        cur.execute("SELECT count(*) FROM synced_client_events")
        self.assertEqual(cur.fetchone()[0], 3)

        # Check baseline table rows
        cur.execute("SELECT count(*) FROM baseline_sources")
        self.assertEqual(cur.fetchone()[0], 6)
        cur.execute("SELECT count(*) FROM baseline_subjects")
        self.assertEqual(cur.fetchone()[0], 5)
        cur.execute("SELECT count(*) FROM baseline_topics")
        self.assertEqual(cur.fetchone()[0], 221)
        cur.execute("SELECT count(*) FROM baseline_weightage_evidence")
        self.assertEqual(cur.fetchone()[0], 17)
        cur.execute("SELECT count(*) FROM baseline_chunks")
        self.assertEqual(cur.fetchone()[0], 451)
        cur.execute("SELECT count(*) FROM baseline_graph_edges")
        self.assertEqual(cur.fetchone()[0], 257)

        conn.close()

if __name__ == '__main__':
    unittest.main()
