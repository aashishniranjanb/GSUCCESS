import sqlite3

conn = sqlite3.connect("gpat_knowledge.db")
cur = conn.cursor()

# Explanations in questions table
cur.execute("SELECT count(*) FROM questions")
tot = cur.fetchone()[0]

cur.execute("SELECT count(*) FROM questions WHERE explanation LIKE 'Official GPAT %'")
prov_only = cur.fetchone()[0]

cur.execute("SELECT count(*) FROM questions WHERE explanation NOT LIKE 'Official GPAT %' AND explanation IS NOT NULL AND explanation != ''")
real_exp = cur.fetchone()[0]

cur.execute("SELECT count(*) FROM questions WHERE explanation IS NULL OR explanation = ''")
empty_exp = cur.fetchone()[0]

cur.execute("SELECT count(*) FROM questions WHERE distractor_reasons_json IS NOT NULL AND distractor_reasons_json != '{}' AND distractor_reasons_json != ''")
distractors_cnt = cur.fetchone()[0]

print(f"Total runtime questions: {tot}")
print(f"  Grounded Conceptual Explanations: {real_exp}")
print(f"  Official Provenance Only ('Official GPAT ...'): {prov_only}")
print(f"  Empty Explanations: {empty_exp}")
print(f"  Distractor Analysis Available: {distractors_cnt}")

conn.close()
