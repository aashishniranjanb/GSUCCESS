import sqlite3
import json
import re
import sys
import io

DB_PATH = "gpat_knowledge.db"

STOPWORDS = {
    "the", "and", "what", "which", "how", "why", "who", "whom", "this", "that", "these",
    "those", "are", "is", "was", "were", "been", "being", "have", "has", "had", "does",
    "did", "doing", "would", "should", "could", "ought", "such", "its", "with", "from",
    "for", "about", "against", "between", "into", "through", "during", "before", "after",
    "above", "below", "to", "under", "again", "further", "then", "once", "here", "there",
    "when", "where", "all", "any", "both", "each", "few", "more", "most", "other", "some",
    "only", "own", "same", "than", "too", "very", "can", "will", "just"
}

def ask_tutor(question: str, top_k: int = 3):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    raw_terms = [w.lower() for w in re.findall(r"\b[a-zA-Z0-9\-\+\/]{3,}\b", question)]
    terms = [w for w in raw_terms if w not in STOPWORDS]
    
    if not terms:
        print("Please enter a specific pharmacology question.")
        return
        
    # Search content blocks
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
                "matched_terms": list(set(matched))
            })
            
    scored_blocks.sort(key=lambda x: x["score"], reverse=True)
    top_blocks = scored_blocks[:top_k]
    
    if not top_blocks:
        print(f"No direct verified textbook evidence found for: '{question}'")
        conn.close()
        return
        
    top_ids = [b["block_id"] for b in top_blocks]
    q_marks = ",".join("?" * len(top_ids))
    
    # Retrieve mapped concepts
    cur.execute(f"""
    SELECT DISTINCT c.id, c.name, c.domain_id, c.importance_score
    FROM block_concept_mappings m
    JOIN concepts c ON m.concept_id = c.id
    WHERE m.block_id IN ({q_marks})
    """, top_ids)
    concepts = cur.fetchall()
    
    # Retrieve claims
    cur.execute(f"""
    SELECT id, concept_id, page_number, claim_text, confidence
    FROM candidate_claims
    WHERE source_block_id IN ({q_marks})
    """, top_ids)
    claims = cur.fetchall()
    
    print("\n" + "=" * 60)
    print("GPAT 2027 SOURCE-GROUNDED TUTOR")
    print("=" * 60)
    print(f"\n[QUERY]: {question}\n")
    
    print("[RETRIEVED CONCEPTS]:")
    for c in concepts:
        print(f"  * {c[1]} (Domain: {c[2]}, Importance: {c[3]}/10)")
        
    print("\n[GROUNDED EVIDENCE FROM SOURCE TEXTBOOK]:")
    for i, b in enumerate(top_blocks, 1):
        heading = " > ".join(b["heading_path"]) if b["heading_path"] else "Key Points"
        print(f"\n--- Citation #{i} ---")
        print(f"Document: Pharmacology Key Points for GPAT (Dr Rajesh Choudhary)")
        print(f"Page: {b['page_number']} | Section: {heading}")
        print(f"Matched Keywords: {b['matched_terms']}")
        print(f"Excerpt: \"{b['content'].strip()}\"")
        
    if claims:
        print("\n[VERIFIED FACTUAL CLAIMS EXTRACTED]:")
        for cl in claims[:4]:
            print(f"  * [Page {cl[2]}] {cl[3].strip()}")
            
    print("\n" + "=" * 60 + "\n")
    conn.close()

if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sample_queries = [
        "What is the mechanism of action of Atropine and why does it cause mydriasis?",
        "How does Furosemide act as a loop diuretic in the kidney?",
        "What is the therapeutic advantage of combining Levodopa with Carbidopa?"
    ]
    
    for q in sample_queries:
        ask_tutor(q)
