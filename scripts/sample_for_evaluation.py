import sqlite3
import json
import random

conn = sqlite3.connect("data/gpat_baseline.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Get 2015 bulk questions
cur.execute("""
    SELECT id, pyq_year, original_q_number, question_text, options_json
    FROM baseline_questions
    WHERE pyq_year IS NOT NULL AND id LIKE 'pyq_gpat_%'
    ORDER BY pyq_year DESC, original_q_number ASC
""")
rows = cur.fetchall()
conn.close()

# Stratify by year groups (Recent: 2024-2026, Mid: 2017-2023, Early: 2010-2016)
recent = [r for r in rows if r["pyq_year"] in (2024, 2025, 2026)]
mid = [r for r in rows if 2017 <= r["pyq_year"] <= 2023]
early = [r for r in rows if 2010 <= r["pyq_year"] <= 2016]

random.seed(42)
sample_recent = random.sample(recent, 20)
sample_mid = random.sample(mid, 20)
sample_early = random.sample(early, 15)
combined_sample = sample_recent + sample_mid + sample_early # 55 items

sample_out = []
for r in combined_sample:
    opts = json.loads(r["options_json"]) if r["options_json"] else []
    sample_out.append({
        "question_id": r["id"],
        "pyq_year": r["pyq_year"],
        "original_q_number": r["original_q_number"],
        "stem": r["question_text"],
        "options": opts
    })

with open("reports/phase6_1_raw_eval_sample.json", "w", encoding="utf-8") as f:
    json.dump(sample_out, f, indent=2)

print(f"Sampled {len(sample_out)} questions across recent ({len(sample_recent)}), mid ({len(sample_mid)}), early ({len(sample_early)}).")
