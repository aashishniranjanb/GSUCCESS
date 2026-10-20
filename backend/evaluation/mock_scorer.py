"""
Mock Scorer and Diagnostic Engine for GPAT 2027.

Calculates:
- Raw Score with Negative Marking (+marks, -negative marks)
- Breakdown: Attempted, Correct, Incorrect, Unattempted
- Accuracy percentage
- Time analytics: total time used, avg time/question
- 4-Quadrant Timing Analysis:
    1. Correct + Fast (< 20s): Solid / Automated Retrieval
    2. Correct + Slow (>= 45s): Knowledge exists, inefficient retrieval
    3. Wrong + Fast (< 15s): Careless error or factual gap
    4. Wrong + Slow (>= 45s): Deep reasoning difficulty / misconception
- Subject & Domain Diagnostics
- Concept Mastery Status (Strong, Fragile, Weak)
- Question Type Breakdown
- Recommended Actionable Repairs for Daily Adaptive Scheduler
"""

from typing import Dict, Any, List, Optional
import datetime

class MockScorer:
    @staticmethod
    def evaluate_mock_session(
        blueprint_config: Dict[str, Any],
        items: List[Dict[str, Any]],
        attempts: List[Dict[str, Any]],
        started_at: str,
        submitted_at: str
    ) -> Dict[str, Any]:
        marks_per_q = float(blueprint_config.get("marks_per_question", 4.0))
        neg_marks = float(blueprint_config.get("negative_marks", 1.0))
        total_questions = len(items)

        # Index attempts by question_id
        attempts_by_qid = {a["question_id"]: a for a in attempts}

        attempted_count = 0
        correct_count = 0
        incorrect_count = 0
        unattempted_count = 0
        raw_score = 0.0
        total_time_ms = 0.0

        timing_quadrants = {
            "fast_correct": 0,    # Strong retrieval
            "slow_correct": 0,    # Inefficient retrieval
            "fast_incorrect": 0,  # Careless / blind guess
            "slow_incorrect": 0   # Deep confusion / struggle
        }

        domain_stats: Dict[str, Dict[str, Any]] = {}
        concept_stats: Dict[str, Dict[str, Any]] = {}
        question_type_stats: Dict[str, Dict[str, Any]] = {}
        confidence_calibration = {
            "high_conf_correct": 0,
            "low_conf_correct": 0,
            "high_conf_incorrect": 0, # Dangerous Overconfidence!
            "low_conf_incorrect": 0
        }

        weak_concepts_flagged = set()
        recurring_traps_identified = []

        for item in items:
            qid = item["question_id"]
            cid = item.get("concept_id", "unknown_concept")
            cname = item.get("concept_name", cid)
            qtype = item.get("question_type", "mcq_standard")
            domain = item.get("domain_id", "general_pharmacology")

            # Init aggregations
            if domain not in domain_stats:
                domain_stats[domain] = {"total": 0, "correct": 0, "incorrect": 0, "unattempted": 0, "score": 0.0}
            if cid not in concept_stats:
                concept_stats[cid] = {"name": cname, "total": 0, "correct": 0, "incorrect": 0, "score": 0.0}
            if qtype not in question_type_stats:
                question_type_stats[qtype] = {"total": 0, "correct": 0, "incorrect": 0, "score": 0.0}

            domain_stats[domain]["total"] += 1
            concept_stats[cid]["total"] += 1
            question_type_stats[qtype]["total"] += 1

            attempt = attempts_by_qid.get(qid)
            if not attempt or attempt.get("selected_option") is None:
                unattempted_count += 1
                domain_stats[domain]["unattempted"] += 1
                continue

            attempted_count += 1
            sel_opt = attempt["selected_option"]
            is_corr = bool(attempt.get("is_correct", False))
            time_spent_sec = float(attempt.get("time_spent_ms", 0)) / 1000.0
            total_time_ms += float(attempt.get("time_spent_ms", 0))
            conf = int(attempt.get("confidence", 3))

            # Score calculation
            if is_corr:
                raw_score += marks_per_q
                correct_count += 1
                domain_stats[domain]["correct"] += 1
                domain_stats[domain]["score"] += marks_per_q
                concept_stats[cid]["correct"] += 1
                concept_stats[cid]["score"] += marks_per_q
                question_type_stats[qtype]["correct"] += 1
                question_type_stats[qtype]["score"] += marks_per_q

                if time_spent_sec < 25.0:
                    timing_quadrants["fast_correct"] += 1
                else:
                    timing_quadrants["slow_correct"] += 1

                if conf >= 4:
                    confidence_calibration["high_conf_correct"] += 1
                else:
                    confidence_calibration["low_conf_correct"] += 1
            else:
                raw_score -= neg_marks
                incorrect_count += 1
                domain_stats[domain]["incorrect"] += 1
                domain_stats[domain]["score"] -= neg_marks
                concept_stats[cid]["incorrect"] += 1
                concept_stats[cid]["score"] -= neg_marks
                question_type_stats[qtype]["incorrect"] += 1
                question_type_stats[qtype]["score"] -= neg_marks

                weak_concepts_flagged.add(cid)

                if time_spent_sec < 20.0:
                    timing_quadrants["fast_incorrect"] += 1
                else:
                    timing_quadrants["slow_incorrect"] += 1

                if conf >= 4:
                    confidence_calibration["high_conf_incorrect"] += 1
                else:
                    confidence_calibration["low_conf_incorrect"] += 1

                # Record distractor reason if present
                distractor_reasons = item.get("distractor_reasons", {})
                reason = distractor_reasons.get(str(sel_opt), "Incorrect option chosen")
                recurring_traps_identified.append({
                    "question_id": qid,
                    "concept_id": cid,
                    "concept_name": cname,
                    "selected_option": sel_opt,
                    "distractor_reason": reason,
                    "confidence": conf,
                    "time_spent_sec": time_spent_sec
                })

        accuracy = round((correct_count / max(1, attempted_count)) * 100, 1)
        max_possible_score = total_questions * marks_per_q
        score_percent = round((max(0.0, raw_score) / max(1.0, max_possible_score)) * 100, 1)

        # Total duration
        total_time_sec = round(total_time_ms / 1000.0, 1)
        avg_time_per_attempt = round(total_time_sec / max(1, attempted_count), 1)

        # Categorize concepts into Strong, Fragile, Weak
        concept_performance = []
        for cid, data in concept_stats.items():
            tot = data["total"]
            corr = data["correct"]
            c_acc = round((corr / max(1, tot)) * 100, 1)
            if c_acc >= 75.0:
                tier = "STRONG"
            elif c_acc >= 40.0:
                tier = "FRAGILE"
            else:
                tier = "WEAK"

            concept_performance.append({
                "concept_id": cid,
                "name": data["name"],
                "total": tot,
                "correct": corr,
                "accuracy": c_acc,
                "tier": tier,
                "score": data["score"]
            })
        concept_performance.sort(key=lambda x: x["accuracy"])

        # Formulate feedback for adaptive scheduler
        recommended_repairs = [
            {
                "concept_id": c["concept_id"],
                "concept_name": c["name"],
                "reason": f"Mock accuracy is only {c['accuracy']}% ({c['tier']})",
                "recommended_mode": "repair" if c["tier"] == "WEAK" else "review"
            }
            for c in concept_performance if c["tier"] in ["WEAK", "FRAGILE"]
        ]

        return {
            "summary": {
                "total_questions": total_questions,
                "attempted": attempted_count,
                "unattempted": unattempted_count,
                "correct": correct_count,
                "incorrect": incorrect_count,
                "raw_score": raw_score,
                "max_possible_score": max_possible_score,
                "score_percent": score_percent,
                "accuracy_percent": accuracy,
                "total_time_sec": total_time_sec,
                "avg_time_per_q_sec": avg_time_per_attempt
            },
            "timing_analysis": {
                "quadrants": timing_quadrants,
                "interpretation": {
                    "automated_retrieval_rate": round(timing_quadrants["fast_correct"] / max(1, attempted_count) * 100, 1),
                    "inefficient_retrieval_rate": round(timing_quadrants["slow_correct"] / max(1, attempted_count) * 100, 1),
                    "careless_error_rate": round(timing_quadrants["fast_incorrect"] / max(1, attempted_count) * 100, 1),
                    "deep_struggle_rate": round(timing_quadrants["slow_incorrect"] / max(1, attempted_count) * 100, 1)
                }
            },
            "confidence_calibration": confidence_calibration,
            "domain_performance": domain_stats,
            "concept_performance": concept_performance,
            "question_type_performance": question_type_stats,
            "identified_traps": recurring_traps_identified,
            "recommended_repairs": recommended_repairs
        }
