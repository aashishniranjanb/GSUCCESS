import json

with open("reports/phase6_1_enhanced_eval_results.json", "r", encoding="utf-8") as f:
    results = json.load(f)

for r in results:
    if r["decision"] in ("CONFIDENT_MATCH", "NEEDS_REVIEW"):
        status = "CORRECT" if r["is_correct"] else "WRONG"
        print(f"[{status:7s}] [{r['decision']:15s}] {r['question_id']} ({r['pyq_year']} Q{r['original_q_number']})")
        print(f"  GT: {r['gt_subject']:24s} | Pred: {r['pred_subject']} ({r['pred_topic']})")
        print(f"  Matched: {r['matched']} (Score {r['confidence_score']})")
        print(f"  Stem: {r['stem_preview']}")
