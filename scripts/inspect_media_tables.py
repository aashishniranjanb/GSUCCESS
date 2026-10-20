import sqlite3

for db_path in ['data/gpat_baseline.db', 'gpat_knowledge.db']:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    print(f"==================== {db_path} ====================")
    for tbl in ['baseline_media', 'baseline_questions', 'questions']:
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (tbl,))
        has = cur.fetchone()
        if has:
            cur.execute(f"PRAGMA table_info({tbl})")
            cols = [c[1] for c in cur.fetchall()]
            cur.execute(f"SELECT count(*) FROM {tbl}")
            cnt = cur.fetchone()[0]
            print(f"  {tbl:20s} ({cnt:4d} rows): {cols}")
    
    # Check baseline_media content if rows exist
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='baseline_media'")
    if cur.fetchone():
        cur.execute("SELECT * FROM baseline_media LIMIT 5")
        rows = cur.fetchall()
        print("  baseline_media samples:", rows)
    conn.close()
