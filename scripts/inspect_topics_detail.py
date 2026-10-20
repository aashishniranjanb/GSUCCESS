import sqlite3
import json

conn = sqlite3.connect("data/gpat_baseline.db")
cur = conn.cursor()

cur.execute("""
    SELECT topic_id, name, subject_id, original_label 
    FROM baseline_topics
    ORDER BY subject_id, topic_id
""")
topics = [dict(zip(["topic_id", "name", "subject_id", "original_label"], r)) for r in cur.fetchall()]
conn.close()

print(f"Total topics: {len(topics)}")
by_subj = {}
for t in topics:
    by_subj.setdefault(t["subject_id"], []).append(t)

for s, tops in by_subj.items():
    print(f"Subject '{s}': {len(tops)} topics")
    sample_names = [t["name"] for t in tops[:4]]
    print("   Samples:", ", ".join(sample_names))
