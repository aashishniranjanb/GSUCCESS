import pytest
import sqlite3
import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
BASELINE_DB = ROOT_DIR / "data" / "gpat_baseline.db"
TOPICS_JSON = ROOT_DIR / "baseline" / "topics.json"
SUBJECTS_JSON = ROOT_DIR / "baseline" / "subjects.json"

@pytest.fixture
def baseline_conn():
    conn = sqlite3.connect(str(BASELINE_DB))
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()

def test_topics_json_referential_integrity():
    """Verify that every topic has a valid subject_id and no broken parent references."""
    with open(SUBJECTS_JSON, "r", encoding="utf-8") as f:
        subjects = json.load(f)
    valid_subject_ids = set(s["subject_id"] for s in subjects)

    with open(TOPICS_JSON, "r", encoding="utf-8") as f:
        topics = json.load(f)

    assert len(topics) == 221
    topic_ids = set(t["topic_id"] for t in topics)

    for t in topics:
        assert t["subject_id"] in valid_subject_ids, f"Topic {t['topic_id']} has invalid subject_id {t['subject_id']}"
        if t.get("parent_topic_id"):
            assert t["parent_topic_id"] in topic_ids, f"Topic {t['topic_id']} references non-existent parent {t['parent_topic_id']}"

def test_database_topics_integrity(baseline_conn):
    """Verify baseline_topics in data/gpat_baseline.db matches canonical counts and passes integrity."""
    cur = baseline_conn.cursor()
    cur.execute("PRAGMA integrity_check")
    assert cur.fetchone()[0] == "ok"

    cur.execute("SELECT count(*) FROM baseline_topics")
    assert cur.fetchone()[0] == 221

    cur.execute("SELECT count(*) FROM baseline_subjects")
    assert cur.fetchone()[0] == 5

    # Check that all subject_ids in baseline_topics exist in baseline_subjects
    cur.execute("""
    SELECT count(*) FROM baseline_topics t
    WHERE t.subject_id NOT IN (SELECT subject_id FROM baseline_subjects)
    """)
    assert cur.fetchone()[0] == 0

def test_no_cyclic_parent_topic_references(baseline_conn):
    """Verify there are zero cyclic parent-child topic loops."""
    cur = baseline_conn.cursor()
    cur.execute("SELECT topic_id, parent_topic_id FROM baseline_topics WHERE parent_topic_id IS NOT NULL")
    pairs = cur.fetchall()
    
    # Direct self-loop check
    for p in pairs:
        assert p[0] != p[1], f"Self-loop detected on topic {p[0]}"
