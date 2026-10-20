import sqlite3

BASE_DB = "data/gpat_baseline.db"
conn = sqlite3.connect(BASE_DB)
cur = conn.cursor()

print("=== BASELINE SUBJECTS ===")
cur.execute("SELECT id, name FROM baseline_subjects")
for r in cur.fetchall():
    print(f"  {r[0]}: {r[1]}")

print("\n=== TOPIC COUNTS BY SUBJECT ===")
cur.execute("SELECT subject_id, count(*) FROM baseline_topics GROUP BY subject_id")
for r in cur.fetchall():
    print(f"  {r[0]}: {r[1]} topics")

print("\n=== SAMPLE TOPICS ===")
cur.execute("SELECT id, subject_id, title FROM baseline_topics LIMIT 10")
for r in cur.fetchall():
    print(f"  {r[0]} ({r[1]}): {r[2]}")

print("\n=== CURRENT QUESTION CONCEPT MAPPINGS ===")
cur.execute("SELECT concept_id, count(*) FROM baseline_questions GROUP BY concept_id ORDER BY count(*) DESC LIMIT 10")
for r in cur.fetchall():
    print(f"  {r[0]}: {r[1]} questions")

conn.close()
