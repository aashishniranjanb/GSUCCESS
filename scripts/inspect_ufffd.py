import sqlite3

conn = sqlite3.connect('data/gpat_baseline.db')
cur = conn.cursor()
cur.execute("SELECT id, question_text, options_json FROM baseline_questions WHERE question_text LIKE '%\ufffd%' OR options_json LIKE '%\ufffd%' LIMIT 5")
rows = cur.fetchall()
print(f"Sample U+FFFD rows ({len(rows)}):")
for r in rows:
    print("ID:", r[0])
    print("  STEM:", repr(r[1][:120]))
    print("  OPTS:", repr(r[2][:120]))
conn.close()
