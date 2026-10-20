import sqlite3
import json

base_conn = sqlite3.connect("data/gpat_baseline.db")
cur = base_conn.cursor()
cur.execute("SELECT id, pyq_year, original_q_number, question_text FROM baseline_questions WHERE original_q_number IS NULL")
rows = cur.fetchall()
print(f"Questions with original_q_number IS NULL: {len(rows)}")
for r in rows:
    print(f"ID: {r[0]} | Year: {r[1]} | Text: {r[3][:60]}...")

base_conn.close()
