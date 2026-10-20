import pytest
import sqlite3
import json
import hashlib
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from fastapi.testclient import TestClient
from backend.main import app

def test_visual_media_assets_exist_and_hash():
    """Verify that all 5 recovered visual PYQ assets exist on disk with valid sha256 checksums."""
    catalog_path = ROOT_DIR / "reports" / "phase6_2_recovered_visual_assets.json"
    assert catalog_path.exists(), "Recovered visual assets catalog missing"
    
    with open(catalog_path, encoding="utf-8") as f:
        assets = json.load(f)
    
    assert len(assets) == 5, f"Expected 5 recovered visual assets, found {len(assets)}"
    
    for a in assets:
        img_path = ROOT_DIR / a["relative_file_path"]
        assert img_path.exists(), f"Asset file missing: {img_path}"
        assert img_path.stat().st_size == a["size_bytes"], "File size mismatch"
        
        hasher = hashlib.sha256()
        with open(img_path, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        assert hasher.hexdigest() == a["file_sha256"], f"Checksum mismatch for {a['media_id']}"

def test_visual_media_database_registration():
    """Verify that baseline_media table and baseline_questions link the recovered assets."""
    conn = sqlite3.connect(ROOT_DIR / "data" / "gpat_baseline.db")
    cur = conn.cursor()
    
    catalog_path = ROOT_DIR / "reports" / "phase6_2_recovered_visual_assets.json"
    with open(catalog_path, encoding="utf-8") as f:
        assets = json.load(f)
        
    for a in assets:
        cur.execute("SELECT media_type, relative_file_path, file_sha256 FROM baseline_media WHERE media_id = ?", (a["media_id"],))
        row = cur.fetchone()
        assert row is not None, f"media_id {a['media_id']} not registered in baseline_media"
        assert row[0] == "CHEMICAL_STRUCTURE"
        assert row[2] == a["file_sha256"]
        
        cur.execute("SELECT media_id FROM baseline_questions WHERE id = ?", (a["question_id"],))
        q_row = cur.fetchone()
        assert q_row is not None, f"Question {a['question_id']} not found in baseline_questions"
        assert q_row[0] == a["media_id"], f"Question {a['question_id']} does not point to media_id {a['media_id']}"
    
    conn.close()

def test_media_static_endpoint_serving():
    """Verify that FastAPI serves the recovered visual media images with correct content-type."""
    client = TestClient(app)
    
    catalog_path = ROOT_DIR / "reports" / "phase6_2_recovered_visual_assets.json"
    with open(catalog_path, encoding="utf-8") as f:
        assets = json.load(f)
        
    for a in assets:
        url = "/" + a["relative_file_path"].replace("baseline/", "")
        resp = client.get(url)
        assert resp.status_code == 200, f"Failed to retrieve media via {url}: status {resp.status_code}"
        assert resp.headers.get("content-type") == "image/png"
        assert len(resp.content) == a["size_bytes"]

def test_explanation_review_queue_structure():
    """Verify that reports/phase6_2_review_queue.csv is valid and contains stratified pilot entries."""
    csv_path = ROOT_DIR / "reports" / "phase6_2_review_queue.csv"
    assert csv_path.exists(), "review_queue.csv is missing"
    
    import csv
    with open(csv_path, encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
        
    assert len(reader) == 25, f"Expected 25 pilot explanation entries, found {len(reader)}"
    
    subjects = set()
    for row in reader:
        assert row["question_id"].startswith("pyq_gpat_")
        assert row["evidence_status"] in ["OFFICIAL_KEY_VERIFIED", "AUTHORITATIVE_VERIFIED", "AI_GENERATED_NEEDS_REVIEW", "INSUFFICIENT_EVIDENCE"]
        assert len(row["rationale"]) > 30, f"Rationale too short for {row['question_id']}"
        assert len(row["textbook_citation"]) > 10, f"Citation missing for {row['question_id']}"
        assert len(row["official_key"]) > 0
        
        # Check distractor reasons json
        d_reasons = json.loads(row["distractor_reasons_json"])
        assert isinstance(d_reasons, dict)
        subjects.add(row["subject_id"])
        
    expected_subjects = {"pharmaceutical_chemistry", "pharmaceutics", "pharmacognosy", "pharmacology", "other_subjects"}
    assert subjects == expected_subjects, f"Subject coverage mismatch: {subjects} vs {expected_subjects}"

def test_learner_db_protection_integrity():
    """Confirm zero destructive side-effects on learner progress records."""
    conn = sqlite3.connect(ROOT_DIR / "gpat_knowledge.db")
    cur = conn.cursor()
    
    cur.execute("SELECT count(*) FROM student_attempts")
    assert cur.fetchone()[0] == 7, "Learner student_attempts modified unexpectedly"
    
    cur.execute("SELECT count(*) FROM fsrs_cards")
    assert cur.fetchone()[0] == 11, "Learner fsrs_cards modified unexpectedly"
    
    cur.execute("SELECT count(*) FROM learner_achievements")
    assert cur.fetchone()[0] == 4, "Learner achievements modified unexpectedly"
    
    cur.execute("PRAGMA integrity_check")
    assert cur.fetchall() == [("ok",)]
    
    cur.execute("PRAGMA foreign_key_check")
    assert len(cur.fetchall()) == 0, "Foreign key violations in learner db"
    
    conn.close()
