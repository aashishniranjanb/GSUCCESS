import sqlite3
import json
import csv
from scripts.enhanced_topic_classifier import EnhancedTopicClassifier

def stage_all_pyq_mappings():
    conn = sqlite3.connect("data/gpat_baseline.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT id, concept_id, topic_id, question_text, options_json, pyq_year, original_q_number
        FROM baseline_questions
        WHERE pyq_year IS NOT NULL
        ORDER BY pyq_year DESC, original_q_number ASC
    """)
    questions = cur.fetchall()
    conn.close()

    classifier = EnhancedTopicClassifier()

    diff_records = []
    review_queue_records = []

    stats = {
        "total_questions": len(questions),
        "confident_match": 0,
        "needs_review": 0,
        "unmapped_pyq": 0,
        "subject_counts": {}
    }

    # Create staging SQLite database table in a separate staging file
    staging_db = "data/pyq_topic_staging.db"
    s_conn = sqlite3.connect(staging_db)
    s_cur = s_conn.cursor()
    s_cur.execute("""
    CREATE TABLE IF NOT EXISTS staged_topic_mappings (
        question_id TEXT PRIMARY KEY,
        pyq_year INTEGER,
        original_q_number INTEGER,
        current_topic_id TEXT,
        proposed_subject_id TEXT,
        proposed_topic_id TEXT,
        proposed_topic_name TEXT,
        classification_state TEXT, -- CONFIDENT_MATCH, NEEDS_REVIEW, UNMAPPED_PYQ
        confidence_score REAL,
        matched_terms_json TEXT,
        score_components_json TEXT,
        is_ambiguous INTEGER,
        rationale TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    for q in questions:
        qid = q["id"]
        year = q["pyq_year"]
        qnum = q["original_q_number"]
        curr_topic = q["topic_id"]
        opts = json.loads(q["options_json"]) if q["options_json"] else []

        pred = classifier.classify_question(q["question_text"], opts)
        state = pred["decision"]
        subj = pred["subject_id"]
        top_id = pred["topic_id"]
        top_name = pred["topic_name"]
        score = pred["confidence_score"]
        terms = pred["matched_terms"]
        ambig = int(pred["is_ambiguous"])
        rat = pred["rationale"]

        if state == "CONFIDENT_MATCH":
            stats["confident_match"] += 1
            stats["subject_counts"][subj] = stats["subject_counts"].get(subj, 0) + 1
        elif state == "NEEDS_REVIEW":
            stats["needs_review"] += 1
            review_queue_records.append({
                "question_id": qid,
                "pyq_year": year,
                "original_q_number": qnum,
                "stem_preview": q["question_text"][:75].replace("\n", " "),
                "current_topic": curr_topic,
                "proposed_subject": subj,
                "proposed_topic": top_id,
                "confidence_score": score,
                "matched_terms": ";".join(terms),
                "is_ambiguous": ambig,
                "rationale": rat
            })
        else:
            stats["unmapped_pyq"] += 1

        diff_records.append({
            "question_id": qid,
            "pyq_year": year,
            "original_q_number": qnum,
            "current_topic": curr_topic,
            "proposed_subject_id": subj or "UNMAPPED",
            "proposed_topic_id": top_id,
            "score": score,
            "matched_evidence": ";".join(terms),
            "classification_state": state,
            "taxonomy_version": "0.1.0",
            "will_change": (curr_topic != top_id)
        })

        s_cur.execute("""
        INSERT OR REPLACE INTO staged_topic_mappings (
            question_id, pyq_year, original_q_number, current_topic_id,
            proposed_subject_id, proposed_topic_id, proposed_topic_name,
            classification_state, confidence_score, matched_terms_json,
            score_components_json, is_ambiguous, rationale
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            qid, year, qnum, curr_topic, subj, top_id, top_name,
            state, score, json.dumps(terms), json.dumps(pred["score_components"]),
            ambig, rat
        ))

    s_conn.commit()
    s_conn.close()

    # Write Diff CSV
    with open("reports/phase6_1_mapping_diff.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "question_id", "pyq_year", "original_q_number", "current_topic",
            "proposed_subject_id", "proposed_topic_id", "score",
            "matched_evidence", "classification_state", "taxonomy_version", "will_change"
        ])
        writer.writeheader()
        writer.writerows(diff_records)

    # Write Review Queue CSV
    with open("reports/phase6_1_review_queue.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "question_id", "pyq_year", "original_q_number", "stem_preview",
            "current_topic", "proposed_subject", "proposed_topic",
            "confidence_score", "matched_terms", "is_ambiguous", "rationale"
        ])
        writer.writeheader()
        writer.writerows(review_queue_records)

    print(f"Staged {len(questions)} PYQ mappings to 'data/pyq_topic_staging.db'.")
    print(f"  CONFIDENT_MATCH : {stats['confident_match']} ({stats['confident_match']/len(questions)*100:.1f}%)")
    print(f"  NEEDS_REVIEW    : {stats['needs_review']} ({stats['needs_review']/len(questions)*100:.1f}%)")
    print(f"  UNMAPPED_PYQ    : {stats['unmapped_pyq']} ({stats['unmapped_pyq']/len(questions)*100:.1f}%)")
    print("Subject breakdown for CONFIDENT_MATCH:")
    for s, c in stats["subject_counts"].items():
        print(f"    {s:26s}: {c:4d}")

if __name__ == "__main__":
    stage_all_pyq_mappings()
