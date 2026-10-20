import sqlite3

for db_path in ["data/gpat_baseline.db", "gpat_knowledge.db"]:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM baseline_questions")
    total_bq = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM baseline_questions WHERE topic_id = 'pharmacology__pk_absorption'")
    fb_bq = cur.fetchone()[0]
    
    # Check questions table if present
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='questions'")
    has_q = cur.fetchone()
    q_info = ""
    if has_q:
        cur.execute("SELECT count(*) FROM questions")
        tot_q = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM questions WHERE concept_id = 'pk_absorption'")
        fb_q = cur.fetchone()[0]
        q_info = f" | questions table: total={tot_q}, pk_absorption={fb_q}"
        
    print(f"[{db_path}] baseline_questions: total={total_bq}, pk_absorption={fb_bq}{q_info}")
    conn.close()
