import sqlite3

for db_path in ["data/gpat_baseline.db", "gpat_knowledge.db"]:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT id, pyq_year, original_q_number, question_text, quality_status FROM baseline_questions WHERE id = 'pyq_gpat_2025_017'")
    r = cur.fetchone()
    print(f"[{db_path}] baseline_questions pyq_gpat_2025_017: {r}")
    
    cur.execute("SELECT review_id, question_id, pyq_year, original_q_number, issue_type FROM pyq_review_queue WHERE question_id = 'pyq_gpat_2025_017'")
    rq = cur.fetchone()
    print(f"[{db_path}] pyq_review_queue pyq_gpat_2025_017: {rq}")
    conn.close()
