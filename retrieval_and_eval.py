import sqlite3
import json
import re

DB_PATH = "gpat_knowledge.db"

EVAL_QUESTIONS = [
    {
        "id": "q01",
        "question": "What is the mechanism of action of cardiac glycosides like Digoxin in heart failure?",
        "subject": "Pharmacology",
        "topic": "Cardiovascular System",
        "expected_concepts": ["cvs_cardiac_glycosides"],
        "keywords": ["digoxin", "atpase", "heart failure", "inotropic"]
    },
    {
        "id": "q02",
        "question": "Why is Atropine contraindicated in narrow-angle glaucoma?",
        "subject": "Pharmacology",
        "topic": "Autonomic Nervous System",
        "expected_concepts": ["ans_antimuscarinics"],
        "keywords": ["atropine", "antimuscarinic", "glaucoma", "mydriasis"]
    },
    {
        "id": "q03",
        "question": "How do Loop diuretics such as Furosemide exert their diuretic effect?",
        "subject": "Pharmacology",
        "topic": "Cardiovascular System",
        "expected_concepts": ["cvs_diuretics"],
        "keywords": ["furosemide", "diuretic", "loop", "henle", "na+/k+/2cl-"]
    },
    {
        "id": "q04",
        "question": "What is the primary difference between competitive and noncompetitive antagonism?",
        "subject": "Pharmacology",
        "topic": "General Pharmacology",
        "expected_concepts": ["pd_antagonism"],
        "keywords": ["competitive", "antagonism", "emax", "agonist", "surmountable"]
    },
    {
        "id": "q05",
        "question": "Why is Levodopa combined with Carbidopa in Parkinson's disease treatment?",
        "subject": "Pharmacology",
        "topic": "Central Nervous System",
        "expected_concepts": ["cns_antiparkinsonian"],
        "keywords": ["levodopa", "carbidopa", "dopa decarboxylase", "dopamine"]
    },
    {
        "id": "q06",
        "question": "Which phase of biotransformation involves cytochrome P450 enzymes?",
        "subject": "Pharmacology",
        "topic": "General Pharmacology",
        "expected_concepts": ["pk_biotransformation"],
        "keywords": ["biotransformation", "phase i", "cytochrome", "cyp450", "oxidation"]
    },
    {
        "id": "q07",
        "question": "What is the molecular mechanism of action of Benzodiazepines on GABA receptors?",
        "subject": "Pharmacology",
        "topic": "Central Nervous System",
        "expected_concepts": ["cns_gaba_sedative_hypnotics"],
        "keywords": ["benzodiazepine", "gaba", "chloride", "frequency"]
    },
    {
        "id": "q08",
        "question": "What is the mechanism of action of ACE inhibitors such as Captopril and Enalapril?",
        "subject": "Pharmacology",
        "topic": "Cardiovascular System",
        "expected_concepts": ["cvs_ace_inhibitors_and_arbs", "cvs_renin_angiotensin_system"],
        "keywords": ["captopril", "enalapril", "angiotensin", "ace", "bradykinin"]
    },
    {
        "id": "q09",
        "question": "How does Phenytoin control epileptic seizures, and what is its kinetic characteristic?",
        "subject": "Pharmacology",
        "topic": "Central Nervous System",
        "expected_concepts": ["cns_antiepileptics"],
        "keywords": ["phenytoin", "sodium channel", "saturation", "kinetics", "seizure"]
    },
    {
        "id": "q10",
        "question": "What is the antidote used to reactivate cholinesterase in Organophosphate poisoning?",
        "subject": "Pharmacology",
        "topic": "Autonomic Nervous System",
        "expected_concepts": ["ans_organophosphate_poisoning", "ans_anticholinesterases"],
        "keywords": ["organophosphate", "pralidoxime", "atropine", "pam", "cholinesterase"]
    },
    {
        "id": "q11",
        "question": "How do Beta blockers like Propranolol reduce blood pressure and cardiac workload?",
        "subject": "Pharmacology",
        "topic": "Autonomic Nervous System",
        "expected_concepts": ["ans_beta_blockers"],
        "keywords": ["propranolol", "beta blocker", "heart rate", "renin"]
    },
    {
        "id": "q12",
        "question": "What determines the apparent Volume of Distribution (Vd) of a drug?",
        "subject": "Pharmacology",
        "topic": "General Pharmacology",
        "expected_concepts": ["pk_volume_of_distribution"],
        "keywords": ["volume of distribution", "vd", "lipid solubility", "plasma protein binding"]
    },
    {
        "id": "q13",
        "question": "What is Dale's vasomotor reversal and what receptor mechanisms cause it?",
        "subject": "Pharmacology",
        "topic": "Autonomic Nervous System",
        "expected_concepts": ["ans_adrenergic_antagonists", "ans_adrenergic_agonists"],
        "keywords": ["dale", "vasomotor", "reversal", "adrenaline", "beta-2", "alpha"]
    },
    {
        "id": "q14",
        "question": "Why is Propylthiouracil used in thyroid storm and how does it inhibit thyroid hormones?",
        "subject": "Pharmacology",
        "topic": "Endocrine Pharmacology",
        "expected_concepts": ["endo_thyroid_drugs"],
        "keywords": ["propylthiouracil", "thyroid", "peroxidase", "storm", "deiodinase"]
    },
    {
        "id": "q15",
        "question": "What is the mechanism of action of Metformin in diabetes mellitus?",
        "subject": "Pharmacology",
        "topic": "Endocrine Pharmacology",
        "expected_concepts": ["endo_antidiabetic_drugs"],
        "keywords": ["metformin", "ampk", "gluconeogenesis", "glucose", "insulin"]
    }
]

STOPWORDS = {
    "the", "and", "what", "which", "how", "why", "who", "whom", "this", "that", "these",
    "those", "are", "is", "was", "were", "been", "being", "have", "has", "had", "does",
    "did", "doing", "would", "should", "could", "ought", "such", "its", "with", "from",
    "for", "about", "against", "between", "into", "through", "during", "before", "after",
    "above", "below", "to", "under", "again", "further", "then", "once", "here", "there",
    "when", "where", "all", "any", "both", "each", "few", "more", "most", "other", "some",
    "only", "own", "same", "than", "too", "very", "can", "will", "just"
}

def search_knowledge_base(conn, query_text: str, top_k: int = 5):
    """Hybrid lexical & concept-guided retrieval over ingested content blocks and claims."""
    cur = conn.cursor()
    raw_terms = [w.lower() for w in re.findall(r"\b[a-zA-Z0-9\-\+\/]{3,}\b", query_text)]
    terms = [w for w in raw_terms if w not in STOPWORDS]
    
    # Query blocks
    cur.execute("SELECT id, page_number, heading_path, content FROM content_blocks")
    blocks = cur.fetchall()
    
    scored_blocks = []
    for b_id, page_no, heading_path, content in blocks:
        c_lower = content.lower()
        score = 0
        matched = []
        for term in terms:
            if term in c_lower:
                score += c_lower.count(term)
                matched.append(term)
                
        if score > 0:
            scored_blocks.append({
                "block_id": b_id,
                "page_number": page_no,
                "heading_path": json.loads(heading_path) if heading_path else [],
                "content": content,
                "score": score,
                "matched_terms": matched
            })
            
    scored_blocks.sort(key=lambda x: x["score"], reverse=True)
    top_blocks = scored_blocks[:top_k]
    
    # Also find associated claims
    evidence_claims = []
    if top_blocks:
        top_ids = [b["block_id"] for b in top_blocks]
        q_marks = ",".join("?" * len(top_ids))
        cur.execute(f"""
        SELECT id, concept_id, page_number, claim_text, confidence 
        FROM candidate_claims 
        WHERE source_block_id IN ({q_marks})
        """, top_ids)
        for row in cur.fetchall():
            evidence_claims.append({
                "claim_id": row[0],
                "concept_id": row[1],
                "page_number": row[2],
                "claim_text": row[3],
                "confidence": row[4]
            })
            
    return top_blocks, evidence_claims

def run_evaluation():
    conn = sqlite3.connect(DB_PATH)
    results = []
    total_recall_hits = 0
    total_questions = len(EVAL_QUESTIONS)
    
    print(f"\n==========================================")
    print(f"RUNNING GPAT RETRIEVAL & GROUNDING EVALUATION")
    print(f"Total Test Questions: {total_questions}")
    print(f"==========================================\n")
    
    for item in EVAL_QUESTIONS:
        q_id = item["id"]
        q_text = item["question"]
        expected_concepts = set(item["expected_concepts"])
        
        top_blocks, claims = search_knowledge_base(conn, q_text + " " + " ".join(item["keywords"]), top_k=5)
        
        # Check concept retrieval match
        retrieved_concepts = set()
        cur = conn.cursor()
        if top_blocks:
            b_ids = [b["block_id"] for b in top_blocks]
            q_marks = ",".join("?" * len(b_ids))
            cur.execute(f"SELECT DISTINCT concept_id FROM block_concept_mappings WHERE block_id IN ({q_marks})", b_ids)
            retrieved_concepts = {r[0] for r in cur.fetchall()}
            
        is_hit = bool(expected_concepts.intersection(retrieved_concepts))
        if is_hit:
            total_recall_hits += 1
            
        # Grounded answer synthesis
        citations = []
        for b in top_blocks[:2]:
            citations.append({
                "document": "Pharmacology Key Points for GPAT",
                "page": b["page_number"],
                "block_id": b["block_id"],
                "excerpt": b["content"][:200] + "..."
            })
            
        eval_record = {
            "question_id": q_id,
            "question": q_text,
            "expected_concepts": list(expected_concepts),
            "retrieved_concepts": list(retrieved_concepts),
            "recall_hit": is_hit,
            "top_score": top_blocks[0]["score"] if top_blocks else 0,
            "evidence_citations": citations,
            "extracted_claims_count": len(claims)
        }
        results.append(eval_record)
        
        status_sym = "[OK]" if is_hit else "[MISS]"
        print(f"{status_sym} {q_id}: {q_text[:65]}... (Recall@5 Hit: {is_hit})")
        if top_blocks:
            print(f"   --> Source: Page {top_blocks[0]['page_number']} | Matched: {top_blocks[0]['matched_terms'][:4]}")
            
    recall_at_5 = (total_recall_hits / total_questions) * 100
    print(f"\n==========================================")
    print(f"EVALUATION SUMMARY")
    print(f"Questions Evaluated: {total_questions}")
    print(f"Recall@5 Accuracy: {recall_at_5:.1f}% ({total_recall_hits}/{total_questions})")
    print(f"==========================================\n")
    
    report = {
        "metrics": {
            "total_questions": total_questions,
            "recall_at_5_percent": recall_at_5,
            "recall_hits": total_recall_hits
        },
        "details": results
    }
    
    with open("evaluation_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
        
    conn.close()
    return report

if __name__ == "__main__":
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    run_evaluation()
