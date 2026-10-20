import json

with open("reports/phase6_1_raw_eval_sample.json", "r", encoding="utf-8") as f:
    sample = json.load(f)

for idx, q in enumerate(sample[:15]):
    print(f"[{idx+1:2d}] {q['question_id']} ({q['pyq_year']} Q{q['original_q_number']})")
    print(f"     Stem: {q['stem'][:90]}...")
    print(f"     Opts: {q['options']}")
