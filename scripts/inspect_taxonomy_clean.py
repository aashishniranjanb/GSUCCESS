import sqlite3

BASE_DB = "data/gpat_baseline.db"
conn = sqlite3.connect(BASE_DB)
cur = conn.cursor()

print("=== BASELINE SUBJECTS ===")
cur.execute("SELECT subject_id, name, status FROM baseline_subjects")
for r in cur.fetchall():
    print(f"  {r[0]}: {r[1]} [{r[2]}]")

print("\n=== TOPIC COUNTS BY SUBJECT ===")
cur.execute("SELECT subject_id, count(*) FROM baseline_topics GROUP BY subject_id")
for r in cur.fetchall():
    print(f"  {r[0]}: {r[1]} topics")

print("\n=== WEIGHTAGE EVIDENCE SAMPLES ===")
cur.execute("SELECT subject_id, reported_value, reported_unit, authority_status, source_filename FROM baseline_weightage_evidence")
for r in cur.fetchall():
    print(f"  {r[0]}: {r[1]} {r[2]} ({r[3]}) from {r[4]}")

print("\n=== BASELINE QUESTIONS MAPPING SUMMARY ===")
cur.execute("SELECT topic_id, count(*) FROM baseline_questions GROUP BY topic_id ORDER BY count(*) DESC LIMIT 10")
for r in cur.fetchall():
    print(f"  Topic: {r[0]} -> {r[1]} questions")

conn.close()
