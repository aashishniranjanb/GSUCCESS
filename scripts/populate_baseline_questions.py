import sqlite3
import hashlib
import json
import os
import time

DB_PATH = "data/gpat_baseline.db"

def sha256_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # 1. Register baseline_media
    media_records = [
        {
            "media_id": "med_atropine_struct_01",
            "media_type": "CHEMICAL_STRUCTURE",
            "relative_file_path": "baseline/media/mcqs/atropine_structure.png",
            "alt_text": "Chemical structure of Atropine showing tropane ring esterified with tropic acid",
            "caption": "Figure 1: Atropine chemical structure and functional pharmacophore",
            "source_id": "doc_kd_tripathi",
            "page_number": 113,
            "rights_status": "FAIR_USE_EDUCATIONAL"
        },
        {
            "media_id": "med_competitive_drc_02",
            "media_type": "GRAPH",
            "relative_file_path": "baseline/media/mcqs/competitive_drc_shift.png",
            "alt_text": "Log dose-response curve shift showing parallel rightward displacement with unchanged Emax in competitive antagonism",
            "caption": "Figure 2: Agonist concentration-response curve displacement under competitive muscarinic blockade",
            "source_id": "doc_kd_tripathi",
            "page_number": 43,
            "rights_status": "FAIR_USE_EDUCATIONAL"
        }
    ]
    
    now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    for m in media_records:
        full_p = m["relative_file_path"]
        f_sha = sha256_file(full_p) if os.path.exists(full_p) else "sha_unknown"
        cur.execute("""
        INSERT OR REPLACE INTO baseline_media (
            media_id, media_type, relative_file_path, file_sha256, alt_text, caption,
            source_id, page_number, rights_status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            m["media_id"], m["media_type"], m["relative_file_path"], f_sha,
            m["alt_text"], m["caption"], m["source_id"], m["page_number"],
            m["rights_status"], now_iso
        ))
    print(f"Registered {len(media_records)} media assets into baseline_media.")

    # 2. Populate baseline_questions from existing 47 questions + add media links for ANS visual MCQs
    cur.execute("SELECT id, concept_id, question_type, difficulty, question_text, options_json, correct_option, distractor_reasons_json, explanation, source_page, cue FROM questions")
    existing_qs = cur.fetchall()
    
    for q in existing_qs:
        qid, cid, qtype, diff, text, opts, corr, dist, expl, page, cue = q
        
        # Link media to specific questions
        media_id = None
        if "competitive antagonist" in text.lower() or "drc" in text.lower():
            media_id = "med_competitive_drc_02"
        elif "atropine" in text.lower() and ("ester" in text.lower() or "structure" in text.lower() or "receptor" in text.lower()):
            media_id = "med_atropine_struct_01"
            
        cur.execute("""
        INSERT OR REPLACE INTO baseline_questions (
            id, concept_id, topic_id, question_type, cognitive_level, difficulty,
            question_text, media_id, options_json, correct_option, distractor_reasons_json,
            explanation, source_page, provenance, verification_status, cue
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            qid, cid, f"pharmacology__ans__{cid}", qtype, "FACTUAL_RECALL" if diff < 5 else "APPLICATION",
            diff, text, media_id, opts, corr, dist, expl, page, "EXPERT_VERIFIED_ORIGINAL", "VERIFIED", cue
        ))
        
    conn.commit()
    
    cur.execute("SELECT count(*), count(media_id) FROM baseline_questions")
    total_q, with_media = cur.fetchone()
    print(f"Populated baseline_questions: {total_q} total, {with_media} questions with linked media.")
    
    cur.execute("SELECT id, question_text, media_id FROM baseline_questions WHERE media_id IS NOT NULL LIMIT 2")
    for row in cur.fetchall():
        print(f"  Visual Question [{row[0]}]: {row[1][:60]}... -> Media: {row[2]}")
        
    conn.close()

if __name__ == '__main__':
    main()
