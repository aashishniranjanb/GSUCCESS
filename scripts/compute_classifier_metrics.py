import json
import sqlite3
import csv
from scripts.enhanced_topic_classifier import EnhancedTopicClassifier

with open("reports/phase6_1_raw_eval_sample.json", "r", encoding="utf-8") as f:
    sample = json.load(f)

with open("reports/phase6_1_ground_truth_reviewed.json", "r", encoding="utf-8") as f:
    ground_truth = json.load(f)

gt_dict = {x["question_id"]: x for x in ground_truth}

classifier = EnhancedTopicClassifier()

eval_results = []
matrix = {}
subjects = ["pharmaceutics", "pharmacology", "pharmaceutical_chemistry", "pharmacognosy", "other_subjects"]
for s in subjects:
    matrix[s] = {s2: 0 for s2 in subjects}
    matrix[s]["UNMAPPED_OR_REVIEW"] = 0

for q in sample:
    qid = q["question_id"]
    gt = gt_dict[qid]
    gt_s = gt["ground_truth_subject"]
    
    pred = classifier.classify_question(q["stem"], q["options"])
    pred_s = pred["subject_id"]
    pred_t = pred["topic_id"]
    dec = pred["decision"]
    
    if dec == "CONFIDENT_MATCH" and pred_s:
        matrix[gt_s][pred_s] += 1
        is_subj_correct = (pred_s == gt_s)
    else:
        matrix[gt_s]["UNMAPPED_OR_REVIEW"] += 1
        is_subj_correct = False

    eval_results.append({
        "question_id": qid,
        "pyq_year": q["pyq_year"],
        "original_q_number": q["original_q_number"],
        "ground_truth_subject": gt_s,
        "ground_truth_topic": gt["ground_truth_topic"],
        "predicted_subject": pred_s,
        "predicted_topic": pred_t,
        "decision": dec,
        "confidence_score": pred["confidence_score"],
        "is_correct_subject": is_subj_correct,
        "matched_terms": pred["matched_terms"]
    })

# Compute Precision, Recall, Confusion
total_sample = len(eval_results)
confident_items = [x for x in eval_results if x["decision"] == "CONFIDENT_MATCH"]
c_correct = sum(1 for x in confident_items if x["is_correct_subject"])

precision = c_correct / max(1, len(confident_items))
coverage = len(confident_items) / total_sample

print(f"==================================================")
print(f"PILOT CLASSIFIER EVALUATION (N={total_sample})")
print(f"==================================================")
print(f"CONFIDENT_MATCH Decisions : {len(confident_items)} / {total_sample} ({coverage*100:.1f}% coverage)")
print(f"CONFIDENT Precision       : {precision*100:.1f}% ({c_correct} / {len(confident_items)} correct)")
print(f"NEEDS_REVIEW Items        : {sum(1 for x in eval_results if x['decision'] == 'NEEDS_REVIEW')}")
print(f"UNMAPPED Items            : {sum(1 for x in eval_results if x['decision'] == 'UNMAPPED_PYQ')}")
print(f"\nCONFUSION MATRIX (Ground Truth rows -> Predicted columns for CONFIDENT_MATCH):")
print(f"{'Subject':26s} | {'P-ceut':6s} | {'P-col':6s} | {'P-chem':6s} | {'P-cogn':6s} | {'Other':6s} | {'Review/Unm':10s}")
print("-" * 80)
for s in subjects:
    row = matrix[s]
    print(f"{s:26s} | {row['pharmaceutics']:6d} | {row['pharmacology']:6d} | {row['pharmaceutical_chemistry']:6d} | {row['pharmacognosy']:6d} | {row['other_subjects']:6d} | {row['UNMAPPED_OR_REVIEW']:10d}")

# Write to CSV
with open("reports/phase6_1_classifier_pilot_metrics.json", "w", encoding="utf-8") as f:
    json.dump({
        "total_sample": total_sample,
        "confident_count": len(confident_items),
        "confident_correct": c_correct,
        "precision": precision,
        "coverage": coverage,
        "confusion_matrix": matrix
    }, f, indent=2)
