import sqlite3

base_conn = sqlite3.connect("data/gpat_baseline.db")
cur = base_conn.cursor()

cur.execute("""
    SELECT review_id, question_id, pyq_year, original_q_number, issue_type, raw_text
    FROM pyq_review_queue
    ORDER BY pyq_year DESC, original_q_number ASC
    LIMIT 10
""")
rows = cur.fetchall()
print(f"Sample quarantined items ({len(rows)} shown):")
for r in rows:
    raw_preview = (r[5][:80] if r[5] else 'None').replace('\n', ' ')
    print(f"[{r[2]} Q{r[3]}] ({r[4]}): {raw_preview}...")

base_conn.close()
