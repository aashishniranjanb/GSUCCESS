import json
import sqlite3
import os

STAGED_FILE = "data/pyq_staging/gpat_2025_staged.json"
BASELINE_DB = "data/gpat_baseline.db"
LEARNER_DB = "gpat_knowledge.db"

def import_pyqs_to_db():
    print(f"Loading staged PYQs from {STAGED_FILE}...")
    with open(STAGED_FILE, "r", encoding="utf-8") as f:
        questions = json.load(f)
    print(f"Total questions to import: {len(questions)}")
    
    # 1. Insert into data/gpat_baseline.db
    base_conn = sqlite3.connect(BASELINE_DB)
    base_cur = base_conn.cursor()
    
    # Check if pyq_year column exists in baseline_questions
    base_cur.execute("PRAGMA table_info(baseline_questions)")
    cols = [c[1] for c in base_cur.fetchall()]
    if "pyq_year" not in cols:
        base_cur.execute("ALTER TABLE baseline_questions ADD COLUMN pyq_year INTEGER")
    if "paper_id" not in cols:
        base_cur.execute("ALTER TABLE baseline_questions ADD COLUMN paper_id TEXT")
        
    for q in questions:
        base_cur.execute("""
        INSERT OR REPLACE INTO baseline_questions (
            id, concept_id, topic_id, question_type, cognitive_level, difficulty,
            question_text, media_id, options_json, correct_option, distractor_reasons_json,
            explanation, source_page, provenance, verification_status, cue, pyq_year, paper_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            q["id"], q["concept_id"], f"{q['subject_id']}__{q['concept_id']}",
            q["question_type"], q["cognitive_level"], q["difficulty"],
            q["question_text"], None, json.dumps(q["options"]),
            q["correct_option"], json.dumps(q["distractor_reasons"]),
            q["explanation"], q["source_page"], q["provenance"],
            q["verification_status"], f"Official GPAT {q['pyq_year']} Q{q['original_q_number']}",
            q["pyq_year"], q["paper_id"]
        ))
        
    base_conn.commit()
    base_cur.execute("SELECT count(*) FROM baseline_questions WHERE provenance = 'OFFICIAL_PYQ'")
    print(f"data/gpat_baseline.db now has {base_cur.fetchone()[0]} verified OFFICIAL_PYQ records.")
    base_conn.close()

    # 2. Also register into gpat_knowledge.db for runtime learning access
    learn_conn = sqlite3.connect(LEARNER_DB)
    learn_cur = learn_conn.cursor()
    
    # Ensure baseline_questions table in learner DB has matching schema
    learn_cur.execute("PRAGMA table_info(baseline_questions)")
    l_cols = [c[1] for c in learn_cur.fetchall()]
    if "pyq_year" not in l_cols:
        learn_cur.execute("ALTER TABLE baseline_questions ADD COLUMN pyq_year INTEGER")
    if "paper_id" not in l_cols:
        learn_cur.execute("ALTER TABLE baseline_questions ADD COLUMN paper_id TEXT")
        
    for q in questions:
        # Check if concept exists in concepts table of learner DB to satisfy FK if inserting to questions table
        learn_cur.execute("SELECT id FROM concepts WHERE id = ?", (q["concept_id"],))
        c_exists = learn_cur.fetchone()
        target_concept = q["concept_id"] if c_exists else "pk_absorption"
        
        learn_cur.execute("""
        INSERT OR REPLACE INTO baseline_questions (
            id, concept_id, topic_id, question_type, cognitive_level, difficulty,
            question_text, media_id, options_json, correct_option, distractor_reasons_json,
            explanation, source_page, provenance, verification_status, cue, pyq_year, paper_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            q["id"], target_concept, f"{q['subject_id']}__{target_concept}",
            q["question_type"], q["cognitive_level"], q["difficulty"],
            q["question_text"], None, json.dumps(q["options"]),
            q["correct_option"], json.dumps(q["distractor_reasons"]),
            q["explanation"], q["source_page"], q["provenance"],
            q["verification_status"], f"Official GPAT {q['pyq_year']} Q{q['original_q_number']}",
            q["pyq_year"], q["paper_id"]
        ))
        
        # Also populate core questions table so LearnerEngine can serve them in practice sessions
        learn_cur.execute("""
        INSERT OR REPLACE INTO questions (
            id, concept_id, question_type, difficulty, question_text,
            options_json, correct_option, distractor_reasons_json,
            explanation, source_page, cue
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            q["id"], target_concept, q["question_type"], q["difficulty"],
            q["question_text"], json.dumps(q["options"]), q["correct_option"],
            json.dumps(q["distractor_reasons"]), q["explanation"], q["source_page"],
            f"GPAT {q['pyq_year']} Q{q['original_q_number']}"
        ))

    learn_conn.commit()
    learn_cur.execute("SELECT count(*) FROM questions")
    print(f"gpat_knowledge.db questions table now has {learn_cur.fetchone()[0]} total questions.")
    learn_conn.close()

if __name__ == '__main__':
    import_pyqs_to_db()
