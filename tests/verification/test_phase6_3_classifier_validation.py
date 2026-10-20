import pytest
import sqlite3
import json
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

def test_holdout_ground_truth_integrity():
    """Verify that independent holdout dataset is present, populated, and valid."""
    gt_path = ROOT_DIR / "reports" / "phase6_3_holdout_ground_truth.json"
    assert gt_path.exists(), "Holdout ground truth missing"
    
    with open(gt_path, encoding="utf-8") as f:
        gt_data = json.load(f)
        
    assert len(gt_data) == 75, f"Expected 75 holdout questions, found {len(gt_data)}"
    
    conn = sqlite3.connect(ROOT_DIR / "data" / "gpat_baseline.db")
    cur = conn.cursor()
    cur.execute("SELECT topic_id FROM baseline_topics")
    valid_topics = set(r[0] for r in cur.fetchall())
    conn.close()
    
    for item in gt_data:
        assert item["question_id"].startswith("pyq_gpat_")
        assert item["gt_subject"] in ["pharmaceutical_chemistry", "pharmaceutics", "pharmacognosy", "pharmacology", "other_subjects"]
        assert item["gt_topic"] in valid_topics, f"Invalid topic {item['gt_topic']} for {item['question_id']}"

def test_holdout_evaluation_reproducibility():
    """Verify that classifier evaluation metrics on the holdout are exact and reproducible."""
    pred_path = ROOT_DIR / "reports" / "phase6_3_holdout_predictions.json"
    assert pred_path.exists(), "Holdout predictions file missing"
    
    with open(pred_path, encoding="utf-8") as f:
        preds = json.load(f)
        
    assert len(preds) == 75
    
    confident = [p for p in preds if p["classification_state"] == "CONFIDENT_MATCH"]
    assert len(confident) == 5, f"Expected 5 confident matches, got {len(confident)}"
    
    # Verify 100% subject precision on confident matches
    subj_correct = sum(1 for p in confident if p["gt_subject"] == p["pred_subject"])
    assert subj_correct == 5, f"Subject precision regression: {subj_correct}/5"

def test_editorial_review_staging_table():
    """Verify editorial review queue persistence schema in staging database."""
    conn = sqlite3.connect(ROOT_DIR / "data" / "pyq_topic_staging.db")
    cur = conn.cursor()
    
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='editorial_reviews'")
    assert cur.fetchone() is not None, "editorial_reviews table missing in pyq_topic_staging.db"
    
    cur.execute("SELECT count(*) FROM editorial_reviews")
    cnt = cur.fetchone()[0]
    assert cnt >= 4, f"Expected at least 4 sample review records, found {cnt}"
    
    cur.execute("SELECT count(*) FROM staged_topic_mappings WHERE classification_state = 'CONFIDENT_MATCH'")
    assert cur.fetchone()[0] == 137, "Staged confident match count altered"
    
    conn.close()

def test_promotion_proposal_file_structure():
    """Verify the mapping promotion proposal CSV format and row count."""
    proposal_path = ROOT_DIR / "reports" / "phase6_3_mapping_promotion_proposal.csv"
    assert proposal_path.exists(), "Mapping promotion proposal CSV missing"
    
    import csv
    with open(proposal_path, encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
        
    assert len(reader) == 137, f"Expected 137 candidate rows, found {len(reader)}"
    for r in reader:
        assert r["promotion_recommendation"] == "STAGED_READY_FOR_APPROVAL"
        assert len(r["proposed_topic_id"]) > 0

def test_production_and_learner_database_untouched():
    """Guarantee that production databases and protected learner tables remain 100% untouched."""
    conn = sqlite3.connect(ROOT_DIR / "gpat_knowledge.db")
    cur = conn.cursor()
    
    cur.execute("SELECT count(*) FROM student_attempts")
    assert cur.fetchone()[0] == 7
    cur.execute("SELECT count(*) FROM fsrs_cards")
    assert cur.fetchone()[0] == 11
    cur.execute("SELECT count(*) FROM learner_achievements")
    assert cur.fetchone()[0] == 4
    
    cur.execute("PRAGMA integrity_check")
    assert cur.fetchall() == [("ok",)]
    cur.execute("PRAGMA foreign_key_check")
    assert len(cur.fetchall()) == 0
    conn.close()
    
    # Confirm gpat_baseline.db was not modified
    b_conn = sqlite3.connect(ROOT_DIR / "data" / "gpat_baseline.db")
    b_cur = b_conn.cursor()
    b_cur.execute("SELECT count(*) FROM baseline_questions WHERE topic_id = 'pharmacology__pk_absorption'")
    assert b_cur.fetchone()[0] == 2015, "Production baseline topic assignments unexpectedly modified"
    b_conn.close()
