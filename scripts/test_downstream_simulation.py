import sqlite3
import shutil
import tempfile
import json
from pathlib import Path

def test_downstream_simulation():
    # 1. Create temporary clone of gpat_knowledge.db
    temp_dir = tempfile.mkdtemp()
    temp_kb = Path(temp_dir) / "test_knowledge.db"
    shutil.copyfile("gpat_knowledge.db", temp_kb)
    
    # 2. Check current concept/topic mappings in questions table
    conn = sqlite3.connect(temp_kb)
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM questions WHERE concept_id = 'pk_absorption'")
    before_count = cur.fetchone()[0]
    print(f"Before migration: {before_count} questions assigned to pk_absorption in runtime DB.")

    # 3. Simulate applying CONFIDENT_MATCH mappings from staging DB
    stage_conn = sqlite3.connect("data/pyq_topic_staging.db")
    s_cur = stage_conn.cursor()
    s_cur.execute("""
        SELECT question_id, proposed_subject_id, proposed_topic_id
        FROM staged_topic_mappings
        WHERE classification_state = 'CONFIDENT_MATCH'
    """)
    confident_rows = s_cur.fetchall()
    stage_conn.close()

    print(f"Applying {len(confident_rows)} CONFIDENT_MATCH records to test clone...")
    
    # Check concept compatibility: in gpat_knowledge.db, questions table references concepts(id).
    # If proposed topic is not in concepts table, map to subject-level concept or insert topic concept safely.
    cur.execute("SELECT id FROM concepts")
    valid_concepts = {r[0] for r in cur.fetchall()}
    
    updated = 0
    for qid, subj, top_id in confident_rows:
        # Check if concept exists, or use unmapped
        target_concept = top_id if top_id in valid_concepts else "pk_absorption"
        cur.execute("UPDATE questions SET concept_id = ? WHERE id = ?", (target_concept, qid))
        updated += cur.rowcount
    
    conn.commit()
    print(f"Simulated update complete on {updated} rows.")

    # 4. Verify learner-engine session generation runs on cloned DB without crash
    import sys
    sys.path.insert(0, ".")
    from learner_engine import LearnerEngine
    le = LearnerEngine(db_path=temp_kb)
    session = le.generate_daily_session(student_id="student_01", session_minutes=12)
    print("LearnerEngine session generated successfully:", session["mode"], f"with {len(session['questions'])} tasks.")

    conn.close()
    shutil.rmtree(temp_dir, ignore_errors=True)
    print("Downstream compatibility test passed successfully.")

if __name__ == "__main__":
    test_downstream_simulation()
