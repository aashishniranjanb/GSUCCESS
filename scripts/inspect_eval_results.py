import json

with open("reports/phase6_1_annotated_eval_results.json", "r", encoding="utf-8") as f:
    results = json.load(f)

print("=== CONFIDENT MATCHES ===")
for r in results:
    if r["predicted_decision"] == "CONFIDENT_MATCH":
        print(f"[{r['pyq_year']} Q{r['original_q_number']}] Correct? {r['is_correct_subject']} | GT: {r['ground_truth_subject']} | Pred: {r['predicted_subject']} | Terms: {r['matched_terms']}")
        print(f"    Stem: {r['stem_preview']}")

print("\n=== SAMPLE NEEDS REVIEW (Wrong Preds) ===")
wrong_review = [r for r in results if r["predicted_decision"] == "NEEDS_REVIEW" and not r["is_correct_subject"]]
for r in wrong_review[:6]:
    print(f"[{r['pyq_year']} Q{r['original_q_number']}] GT: {r['ground_truth_subject']} | Pred: {r['predicted_subject']} ({r['predicted_topic']}) | Terms: {r['matched_terms']}")
    print(f"    Stem: {r['stem_preview']}")
