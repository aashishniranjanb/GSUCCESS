import sqlite3
import os

for db_path in ['data/gpat_baseline.db', 'gpat_knowledge.db']:
    if not os.path.exists(db_path):
        print(f"File not found: {db_path}")
        continue
    print(f"==================== {db_path} ====================")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [r[0] for r in cur.fetchall()]
    for t in tables:
        cur.execute(f"SELECT count(*) FROM [{t}]")
        cnt = cur.fetchone()[0]
        print(f"  {t:30s}: {cnt}")
    conn.close()
