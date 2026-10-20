import sqlite3
import json

base_conn = sqlite3.connect("data/gpat_baseline.db")
base_cur = base_conn.cursor()

print("=== BASELINE_QUESTIONS in data/gpat_baseline.db ===")
base_cur.execute("SELECT pyq_year, count(*) FROM baseline_questions GROUP BY pyq_year ORDER BY pyq_year")
for r in base_cur.fetchall():
    print(f"  Year {r[0]}: {r[1]} questions")

base_cur.execute("SELECT quality_status, count(*) FROM baseline_questions GROUP BY quality_status")
print("\n=== Quality Status in baseline_questions ===")
for r in base_cur.fetchall():
    print(f"  {r[0]}: {r[1]}")

base_cur.execute("SELECT answer_status, count(*) FROM baseline_questions GROUP BY answer_status")
print("\n=== Answer Status in baseline_questions ===")
for r in base_cur.fetchall():
    print(f"  {r[0]}: {r[1]}")

print("\n=== PYQ_REVIEW_QUEUE in data/gpat_baseline.db ===")
base_cur.execute("SELECT pyq_year, count(*) FROM pyq_review_queue GROUP BY pyq_year ORDER BY pyq_year")
for r in base_cur.fetchall():
    print(f"  Year {r[0]}: {r[1]} items in review queue")

base_cur.execute("SELECT issue_type, count(*) FROM pyq_review_queue GROUP BY issue_type")
print("\n=== Issue Types in pyq_review_queue ===")
for r in base_cur.fetchall():
    print(f"  {r[0]}: {r[1]}")

base_conn.close()
