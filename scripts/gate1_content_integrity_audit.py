import sqlite3
import json
import re
import csv

BASE_DB = "data/gpat_baseline.db"

def run_content_integrity_audit():
    conn = sqlite3.connect(BASE_DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    cur.execute("""
        SELECT id, concept_id, topic_id, question_text, options_json, correct_option,
               source_page, provenance, verification_status, pyq_year, paper_id,
               quality_status, raw_text, original_q_number, answer_status, answer_source_page
        FROM baseline_questions
        ORDER BY pyq_year DESC, original_q_number ASC
    """)
    questions = cur.fetchall()
    
    findings = []
    stats = {
        "total_audited": len(questions),
        "clean": 0,
        "truncated_stem": 0,
        "invalid_option_count": 0,
        "missing_options": 0,
        "unmapped_or_generic_concept": 0,
        "unsupported_characters": 0,
        "missing_answer_key": 0,
        "duplicate_hash": 0
    }
    
    seen_stems = {}
    
    for q in questions:
        qid = q["id"]
        year = q["pyq_year"]
        qnum = q["original_q_number"]
        stem = q["question_text"] or ""
        opts_raw = q["options_json"]
        corr = q["correct_option"]
        concept = q["concept_id"]
        issues = []
        
        # 1. Stem completeness & length
        if len(stem.strip()) < 10:
            issues.append("STEM_TOO_SHORT")
            stats["truncated_stem"] += 1
        if "..." in stem[-5:] or stem.endswith("Arrange the following"):
            issues.append("POSSIBLE_STEM_TRUNCATION")
            stats["truncated_stem"] += 1
            
        # 2. Options check
        try:
            opts = json.loads(opts_raw) if opts_raw else []
        except Exception:
            opts = []
            issues.append("CORRUPT_OPTIONS_JSON")
            
        if len(opts) != 4:
            issues.append(f"INVALID_OPTION_COUNT_{len(opts)}")
            stats["invalid_option_count"] += 1
        elif any(len(o.strip()) == 0 for o in opts):
            issues.append("EMPTY_OPTION_FOUND")
            stats["missing_options"] += 1
            
        # 3. Key validity
        if corr is None or not (0 <= corr <= 3):
            issues.append("INVALID_OR_MISSING_KEY_INDEX")
            stats["missing_answer_key"] += 1
            
        # 4. Special / Broken characters (e.g., Replacement character \ufffd or null bytes)
        if "\ufffd" in stem or any("\ufffd" in o for o in opts):
            issues.append("CONTAINS_REPLACEMENT_CHAR_UFFFD")
            stats["unsupported_characters"] += 1
        if "\x00" in stem or any("\x00" in o for o in opts):
            issues.append("CONTAINS_NULL_BYTE")
            stats["unsupported_characters"] += 1
            
        # 5. Duplicate detection
        norm_stem = re.sub(r'\s+', ' ', stem.strip().lower())
        if norm_stem in seen_stems:
            issues.append(f"DUPLICATE_OF_{seen_stems[norm_stem]}")
            stats["duplicate_hash"] += 1
        else:
            seen_stems[norm_stem] = qid
            
        # 6. Concept mapping specificity
        if not concept or concept in ["pk_absorption", "gen_pharmacology"]:
            # Check if likely placeholder
            stats["unmapped_or_generic_concept"] += 1
            
        if not issues:
            stats["clean"] += 1
            
        findings.append({
            "question_id": qid,
            "pyq_year": year,
            "original_q_number": qnum,
            "issue_count": len(issues),
            "issues": ";".join(issues) if issues else "NONE",
            "stem_preview": stem[:60].replace("\n", " "),
            "concept_id": concept,
            "quality_status": q["quality_status"]
        })
        
    conn.close()
    
    # Write findings CSV
    csv_path = "reports/content_integrity_findings.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "question_id", "pyq_year", "original_q_number", "issue_count",
            "issues", "stem_preview", "concept_id", "quality_status"
        ])
        writer.writeheader()
        writer.writerows(findings)
        
    print(f"Audited {len(findings)} questions.")
    print("Stats:", json.dumps(stats, indent=2))
    return stats, findings

if __name__ == "__main__":
    run_content_integrity_audit()
