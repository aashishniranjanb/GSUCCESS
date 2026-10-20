import sqlite3

def sync_media_to_learner_db():
    src = sqlite3.connect('data/gpat_baseline.db')
    src_cur = src.cursor()

    tgt = sqlite3.connect('gpat_knowledge.db')
    tgt_cur = tgt.cursor()

    for tbl in ['baseline_media', 'baseline_questions']:
        src_cur.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{tbl}'")
        row = src_cur.fetchone()
        if not row:
            continue
        create_sql = row[0]
        tgt_cur.execute(f"DROP TABLE IF EXISTS [{tbl}]")
        tgt_cur.execute(create_sql)
        
        src_cur.execute(f"SELECT * FROM [{tbl}]")
        rows = src_cur.fetchall()
        if rows:
            ph = ','.join(['?']*len(rows[0]))
            tgt_cur.executemany(f"INSERT INTO [{tbl}] VALUES ({ph})", rows)
        print(f"Synced {tbl}: {len(rows)} rows to gpat_knowledge.db")

    tgt.commit()
    src.close()
    tgt.close()
    print("Media sync complete.")

if __name__ == '__main__':
    sync_media_to_learner_db()
