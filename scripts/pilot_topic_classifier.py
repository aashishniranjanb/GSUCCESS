import sqlite3
import json
import re

def build_keyword_rules():
    # Build dictionary of subject -> topic_id -> list of keywords/phrases
    conn = sqlite3.connect("data/gpat_baseline.db")
    cur = conn.cursor()
    cur.execute("SELECT topic_id, name, subject_id, original_label FROM baseline_topics")
    rows = cur.fetchall()
    conn.close()
    
    topic_rules = []
    for tid, name, sid, label in rows:
        keywords = set()
        # Clean title
        clean_name = re.sub(r'[^a-zA-Z0-9\s]', ' ', name).lower()
        words = [w for w in clean_name.split() if len(w) > 3 and w not in ["and", "with", "from", "system", "general", "allied", "basic", "drugs", "pharmacy", "study"]]
        keywords.update(words)
        keywords.add(clean_name.strip())
        
        # Specific high-signal domain keywords based on syllabus terminology
        if "alkaloid" in clean_name:
            keywords.update(["tropane", "indole alkaloid", "quinine", "morphine", "reserpine", "vinca", "atropine", "cinchona"])
        elif "glycoside" in clean_name or "cardiac" in clean_name:
            keywords.update(["cardiac glycoside", "digitalis", "digoxin", "ouabain", "anthraquinone", "senna", "aloe", "saponin"])
        elif "volatile oil" in clean_name or "terpenoid" in clean_name:
            keywords.update(["terpene", "terpenoid", "monoterpene", "sesquiterpene", "clove", "eucalyptus", "mentha"])
        elif "diels" in clean_name or "alder" in clean_name or "cycloaddition" in clean_name:
            keywords.update(["diene", "dienophile", "cycloaddition", "diels-alder", "pericyclic"])
        elif "aromatic" in clean_name:
            keywords.update(["electrophilic aromatic", "benzene", "toluene", "nitrobenzene", "huckel", "aromaticity", "phenol"])
        elif "sedative" in clean_name or "hypnotic" in clean_name or "gaba" in clean_name:
            keywords.update(["barbiturate", "benzodiazepine", "diazepam", "gaba-a", "zolpidem", "phenobarbital", "barbituric"])
        elif "diuretic" in clean_name:
            keywords.update(["furosemide", "loop diuretic", "thiazide", "spironolactone", "acetazolamide", "carbonic anhydrase", "nephron", "henle"])
        elif "autonomic" in clean_name or "cholinergic" in clean_name:
            keywords.update(["acetylcholine", "muscarinic", "nicotinic", "atropine", "physostigmine", "parasympathetic", "anticholinergic", "cholinergic", "myasthenia"])
        elif "adrenergic" in clean_name or "sympathomimetic" in clean_name:
            keywords.update(["catecholamine", "epinephrine", "norepinephrine", "alpha-blocker", "beta-blocker", "propranolol", "dobutamine", "salbutamol", "adrenergic"])
        elif "antibacterial" in clean_name or "antibiotic" in clean_name:
            keywords.update(["penicillin", "cephalosporin", "tetracycline", "aminoglycoside", "macrolide", "fluoroquinolone", "chloramphenicol", "beta-lactam"])
        elif "suspension" in clean_name or "emulsion" in clean_name:
            keywords.update(["stokes", "sedimentation", "flocculated", "deflocculated", "creaming", "zeta potential", "surfactant", "hlb"])
        elif "tablet" in clean_name or "compression" in clean_name:
            keywords.update(["capping", "lamination", "disintegration", "friability", "dissolution", "granulation", "binder", "lubricant"])
        elif "pharmacokinetics" in clean_name or "bioavailability" in clean_name:
            keywords.update(["clearance", "volume of distribution", "half-life", "auc", "bioequivalence", "cmax", "tmax", "first-pass", "elimination rate"])
        elif "chromatography" in clean_name:
            keywords.update(["hplc", "gas chromatography", "retention time", "stationary phase", "mobile phase", "rf value", "plate count", "resolution"])
        elif "spectroscopy" in clean_name or "spectrophotometry" in clean_name:
            keywords.update(["beer-lambert", "uv-visible", "infrared", "nmr", "mass spectrometry", "chemical shift", "wavelength", "absorbance"])
        elif "jurisprudence" in clean_name or "act" in clean_name:
            keywords.update(["drugs and cosmetics act", "schedule", "d&c act", "pharmacy act", "narcotic", "magic remedies", "form 20", "schedule m"])
            
        topic_rules.append({
            "topic_id": tid,
            "topic_name": name,
            "subject_id": sid,
            "keywords": [k for k in keywords if len(k) > 2]
        })
        
    return topic_rules

def test_classifier():
    rules = build_keyword_rules()
    print(f"Loaded {len(rules)} topic keyword rule sets.")
    
    conn = sqlite3.connect("data/gpat_baseline.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
        SELECT id, original_q_number, pyq_year, question_text, options_json
        FROM baseline_questions
        WHERE pyq_year IS NOT NULL
        ORDER BY pyq_year DESC, original_q_number ASC
        LIMIT 100
    """)
    sample_q = cur.fetchall()
    conn.close()
    
    mapped_count = 0
    unmapped_count = 0
    
    print("\n=== CLASSIFICATION PILOT (First 15 sample questions) ===")
    for idx, q in enumerate(sample_q):
        stem = q["question_text"] or ""
        opts = json.loads(q["options_json"]) if q["options_json"] else []
        text_corpus = (stem + " " + " ".join(opts)).lower()
        
        best_topic = None
        best_score = 0
        best_subject = None
        
        for r in rules:
            score = 0
            for kw in r["keywords"]:
                if kw in text_corpus:
                    # Longer phrase matches get higher weight
                    score += 3 if " " in kw else 1
            if score > best_score:
                best_score = score
                best_topic = r["topic_id"]
                best_subject = r["subject_id"]
                
        # Confidence threshold: minimum score 3
        if best_score >= 3:
            mapped_count += 1
            status = "CONFIDENT_MATCH"
        elif best_score >= 1:
            status = "NEEDS_REVIEW"
        else:
            status = "UNMAPPED_PYQ"
            unmapped_count += 1
            
        if idx < 15:
            print(f"[{q['pyq_year']} Q{q['original_q_number']:3d}] {status:16s} (Score {best_score:2d}) -> {best_subject or 'None'}:{best_topic or 'None'}")
            print(f"    Text: {stem[:75]}...")
            
    print(f"\nPilot of 100 questions: Mapped (score >= 3) = {mapped_count}, Review (1..2) = {100 - mapped_count - unmapped_count}, Unmapped (0) = {unmapped_count}")

if __name__ == "__main__":
    test_classifier()
