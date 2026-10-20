import json
from scripts.enhanced_topic_classifier import EnhancedTopicClassifier

with open("reports/phase6_1_raw_eval_sample.json", "r", encoding="utf-8") as f:
    sample = json.load(f)

with open("reports/phase6_1_annotated_eval_results.json", "r", encoding="utf-8") as f:
    annotated = json.load(f)

gt_map = {x["question_id"]: x["ground_truth_subject"] for x in annotated}

classifier = EnhancedTopicClassifier()

eval_results = []
for q in sample:
    qid = q["question_id"]
    gt_subj = gt_map.get(qid, "pharmaceutical_chemistry")
    res = classifier.classify_question(q["stem"], q["options"])
    
    is_correct = (res["subject_id"] == gt_subj) if res["subject_id"] else False
    
    eval_results.append({
        "question_id": qid,
        "pyq_year": q["pyq_year"],
        "original_q_number": q["original_q_number"],
        "stem_preview": q["stem"][:70].replace("\n", " "),
        "gt_subject": gt_subj,
        "pred_subject": res["subject_id"],
        "pred_topic": res["topic_id"],
        "decision": res["decision"],
        "confidence_score": res["confidence_score"],
        "is_correct": is_correct,
        "matched": res["matched_terms"]
    })

confident = [x for x in eval_results if x["decision"] == "CONFIDENT_MATCH"]
review = [x for x in eval_results if x["decision"] == "NEEDS_REVIEW"]
unmapped = [x for x in eval_results if x["decision"] == "UNMAPPED_PYQ"]

c_corr = sum(1 for x in confident if x["is_correct"])
r_corr = sum(1 for x in review if x["is_correct"])

print(f"Total Reviewed Sample: {len(eval_results)}")
print(f"  CONFIDENT_MATCH: {len(confident)} | Correct Subject: {c_corr} | Precision: {c_corr/max(1, len(confident))*100:.1f}%")
print(f"  NEEDS_REVIEW:    {len(review)} | Correct Subject: {r_corr} | Precision: {r_corr/max(1, len(review))*100:.1f}%")
print(f"  UNMAPPED_PYQ:    {len(unmapped)}")
print(f"Overall High-Precision Coverage: {len(confident)/len(eval_results)*100:.1f}%")

with open("reports/phase6_1_enhanced_eval_results.json", "w", encoding="utf-8") as f:
    json.dump(eval_results, f, indent=2)
