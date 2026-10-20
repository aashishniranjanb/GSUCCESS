import unittest
import sqlite3
import shutil
import tempfile
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from scripts.enhanced_topic_classifier import EnhancedTopicClassifier

class TestPhase61TopicMapping(unittest.TestCase):
    def setUp(self):
        self.classifier = EnhancedTopicClassifier()

    def test_01_confident_matches_have_high_precision_signals(self):
        # 1. Pharmaceutics (Dryers)
        res1 = self.classifier.classify_question(
            "Which is an example of continuous shelf moving bed dryer?",
            ["Vacuum Tumble Dryer", "Turbo Tray Dryer", "Tray Dryer", "Spray Dryer"]
        )
        self.assertEqual(res1["decision"], "CONFIDENT_MATCH")
        self.assertEqual(res1["subject_id"], "pharmaceutics")
        self.assertIn("tray dryer", res1["matched_terms"])

        # 2. Pharmacognosy (Saponin)
        res2 = self.classifier.classify_question(
            "Chikusetsu saponin is present in which crude drug?",
            ["Senega", "Ginseng", "Quillia", "Liquorice"]
        )
        self.assertEqual(res2["decision"], "CONFIDENT_MATCH")
        self.assertEqual(res2["subject_id"], "pharmacognosy")
        self.assertIn("chikusetsu saponin", res2["matched_terms"])

        # 3. Jurisprudence / Law
        res3 = self.classifier.classify_question(
            "Chapter IV of which law states that experiment on animals are avoided wherever possible?",
            ["Drugs and Cosmetics Act", "Pharmacy Act 1948", "Medicinal and Toilet Preparations Act 1955", "Magic Remedies Act"]
        )
        self.assertEqual(res3["decision"], "CONFIDENT_MATCH")
        self.assertEqual(res3["subject_id"], "other_subjects")

    def test_02_ambiguous_questions_are_routed_to_needs_review(self):
        # Ambiguous question mentioning both analytical UV and biological tissue
        res = self.classifier.classify_question(
            "The visible coloured ring of the eye is called:",
            ["Lens", "Iris", "Cornea", "Retina"]
        )
        # Eye tissue without anatomy phrasing routes safely to review/unmapped, never falsely to pk_absorption
        self.assertNotEqual(res["topic_id"], "pharmacology__pk_absorption")

    def test_03_zero_keyword_questions_route_to_unmapped(self):
        res = self.classifier.classify_question(
            "If emission intensity doubles when concentration increases from 5 to 10 ppm:",
            ["Option A", "Option B", "Option C", "Option D"]
        )
        self.assertEqual(res["decision"], "UNMAPPED_PYQ")
        self.assertEqual(res["topic_id"], "UNMAPPED_PYQ")
        self.assertIsNone(res["subject_id"])

    def test_04_staging_table_integrity(self):
        conn = sqlite3.connect("data/pyq_topic_staging.db")
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM staged_topic_mappings")
        total = cur.fetchone()[0]
        self.assertGreater(total, 2000)

        cur.execute("SELECT count(*) FROM staged_topic_mappings WHERE classification_state = 'CONFIDENT_MATCH'")
        confident = cur.fetchone()[0]
        self.assertGreater(confident, 100)
        conn.close()

if __name__ == "__main__":
    unittest.main()
