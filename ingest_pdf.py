import os
import sys
import json
import sqlite3
import yaml
import time
from pathlib import Path

from gpat_v0_ontology_ingestion.gpat_v0.ingestion_pipeline.app.docling_adapter import DoclingAdapter
from gpat_v0_ontology_ingestion.gpat_v0.ingestion_pipeline.app.concept_mapper import ConceptMapper
from gpat_v0_ontology_ingestion.gpat_v0.ingestion_pipeline.app.claim_extractor import ClaimExtractor

DB_PATH = "gpat_knowledge.db"

def init_sqlite_db(db_path: str = DB_PATH):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Enable WAL mode for high concurrency & speed
    cur.execute("PRAGMA journal_mode=WAL;")
    
    # 1. Documents
    cur.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id TEXT PRIMARY KEY,
        filename TEXT NOT NULL,
        title TEXT,
        authority_level INTEGER DEFAULT 3,
        total_pages INTEGER,
        status TEXT DEFAULT 'completed',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    # 2. Content Blocks (Chunks from Docling HybridChunker)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS content_blocks (
        id TEXT PRIMARY KEY,
        document_id TEXT NOT NULL,
        page_number INTEGER NOT NULL,
        heading_path TEXT,
        content TEXT NOT NULL,
        block_type TEXT DEFAULT 'paragraph',
        FOREIGN KEY (document_id) REFERENCES documents(id)
    );
    """)
    
    # 3. Concepts
    cur.execute("""
    CREATE TABLE IF NOT EXISTS concepts (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        subject_id TEXT NOT NULL,
        domain_id TEXT NOT NULL,
        learning_objective TEXT,
        importance_score INTEGER,
        difficulty INTEGER,
        status TEXT DEFAULT 'active'
    );
    """)
    
    # 4. Block-Concept Mappings
    cur.execute("""
    CREATE TABLE IF NOT EXISTS block_concept_mappings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        block_id TEXT NOT NULL,
        concept_id TEXT NOT NULL,
        matched_terms TEXT,
        confidence REAL DEFAULT 0.9,
        FOREIGN KEY (block_id) REFERENCES content_blocks(id),
        FOREIGN KEY (concept_id) REFERENCES concepts(id)
    );
    """)
    
    # 5. Candidate Claims
    cur.execute("""
    CREATE TABLE IF NOT EXISTS candidate_claims (
        id TEXT PRIMARY KEY,
        concept_id TEXT NOT NULL,
        source_block_id TEXT NOT NULL,
        page_number INTEGER NOT NULL,
        claim_text TEXT NOT NULL,
        evidence_text TEXT NOT NULL,
        confidence REAL DEFAULT 0.85,
        verification_status TEXT DEFAULT 'unverified',
        FOREIGN KEY (concept_id) REFERENCES concepts(id),
        FOREIGN KEY (source_block_id) REFERENCES content_blocks(id)
    );
    """)
    
    conn.commit()
    return conn

def populate_concepts(conn, seed_data):
    cur = conn.cursor()
    concepts = seed_data.get("concepts", [])
    for c in concepts:
        cur.execute("""
        INSERT OR REPLACE INTO concepts (id, name, subject_id, domain_id, learning_objective, importance_score, difficulty, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            c.get("id"),
            c.get("name"),
            c.get("subject_id", "pharmacology"),
            c.get("domain_id", "general_pharmacology"),
            c.get("learning_objective", "EXPLAIN"),
            c.get("importance_score", 5),
            c.get("difficulty", 5),
            c.get("status", "active")
        ))
    conn.commit()
    print(f"Populated {len(concepts)} concepts into SQLite database.")

def ingest_document(pdf_path: str, page_ranges: list[tuple[int, int]], document_id: str = "doc_pharmacology_complete"):
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
    print(f"\n==========================================")
    print(f"STARTING GPAT DOCUMENT INGESTION")
    print(f"Target PDF: {pdf_path}")
    print(f"Page Ranges: {page_ranges}")
    print(f"==========================================\n")
    
    # 1. Load Ontology Seed
    seed_path = "gpat_concept_seed.yaml"
    with open(seed_path, "r", encoding="utf-8") as f:
        seed_data = yaml.safe_load(f)
        
    conn = init_sqlite_db()
    populate_concepts(conn, seed_data)
    
    cur = conn.cursor()
    cur.execute("""
    INSERT OR REPLACE INTO documents (id, filename, title, authority_level, total_pages, status)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        document_id,
        os.path.basename(pdf_path),
        "Pharmacology Key Points for GPAT (Dr Rajesh Choudhary)",
        3, # Standard Textbook / Verified Educational
        121,
        "processing"
    ))
    conn.commit()
    
    adapter = DoclingAdapter(do_ocr=False)
    mapper = ConceptMapper(seed_data)
    claim_extractor = ClaimExtractor()
    
    total_blocks_ingested = 0
    total_mapped_blocks = 0
    total_claims_extracted = 0
    all_mapped_blocks = []
    
    for start_page, end_page in page_ranges:
        t0 = time.time()
        print(f"\nProcessing pages {start_page} to {end_page} with Docling...")
        
        doc = adapter.convert(pdf_path, page_range=(start_page, end_page))
        blocks = adapter.extract_chunks(doc, document_id=document_id)
        
        print(f"Extracted {len(blocks)} hybrid chunks in {time.time() - t0:.2f}s.")
        
        # Concept Mapping
        mapped_blocks = mapper.map_blocks(blocks)
        claims = claim_extractor.extract(mapped_blocks)
        
        # Insert blocks
        for b in mapped_blocks:
            cur.execute("""
            INSERT OR REPLACE INTO content_blocks (id, document_id, page_number, heading_path, content, block_type)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
                b["block_id"],
                b["document_id"],
                b["page_number"],
                json.dumps(b.get("heading_path", [])),
                b["text"],
                b.get("block_type", "paragraph")
            ))
            
            # Insert mappings
            for match in b.get("concept_matches", []):
                cur.execute("""
                INSERT INTO block_concept_mappings (block_id, concept_id, matched_terms, confidence)
                VALUES (?, ?, ?, ?)
                """, (
                    b["block_id"],
                    match["concept_id"],
                    json.dumps(match.get("matched_terms", [])),
                    0.95
                ))
                
        # Insert claims
        for cl in claims:
            cur.execute("""
            INSERT OR REPLACE INTO candidate_claims (id, concept_id, source_block_id, page_number, claim_text, evidence_text, confidence, verification_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cl["claim_id"],
                cl["concept_id"],
                cl["source_block_id"],
                cl["page_number"],
                cl["claim_text"],
                cl["evidence_text"],
                cl["confidence"],
                cl["verification_status"]
            ))
            
        conn.commit()
        
        mapped_count = sum(1 for b in mapped_blocks if b["concept_candidates"])
        total_blocks_ingested += len(blocks)
        total_mapped_blocks += mapped_count
        total_claims_extracted += len(claims)
        all_mapped_blocks.extend(mapped_blocks)
        
        print(f"Batch complete: {mapped_count}/{len(blocks)} blocks matched concepts, {len(claims)} claims extracted.")
        
    cur.execute("UPDATE documents SET status = 'completed' WHERE id = ?", (document_id,))
    conn.commit()
    
    # Generate Summary Metrics
    summary = {
        "document_id": document_id,
        "filename": os.path.basename(pdf_path),
        "total_blocks": total_blocks_ingested,
        "total_mapped_blocks": total_mapped_blocks,
        "total_candidate_claims": total_claims_extracted,
        "page_ranges_processed": page_ranges,
        "concepts_detected": {}
    }
    
    cur.execute("""
    SELECT c.id, c.name, COUNT(DISTINCT m.block_id) as block_count, COUNT(DISTINCT cl.id) as claim_count
    FROM concepts c
    LEFT JOIN block_concept_mappings m ON c.id = m.concept_id
    LEFT JOIN candidate_claims cl ON c.id = cl.concept_id
    GROUP BY c.id, c.name
    HAVING block_count > 0
    ORDER BY block_count DESC
    """)
    
    rows = cur.fetchall()
    for row in rows:
        summary["concepts_detected"][row[0]] = {
            "name": row[1],
            "blocks": row[2],
            "claims": row[3]
        }
        
    with open("ingestion_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
        
    print("\n==========================================")
    print("INGESTION COMPLETE")
    print(f"Total Chunks Ingested: {total_blocks_ingested}")
    print(f"Chunks Mapped to Concepts: {total_mapped_blocks}")
    print(f"Candidate Claims Extracted: {total_claims_extracted}")
    print(f"SQLite DB: {DB_PATH}")
    print(f"Summary saved to ingestion_summary.json")
    print("==========================================\n")
    
    conn.close()
    return summary

if __name__ == "__main__":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    # Comprehensive Vertical Slice: General Pharmacology, ANS, CVS, CNS
    pdf = "Pharmacology-complete.pdf"
    ranges = [(1, 15), (16, 24), (25, 41), (79, 96)]
    ingest_document(pdf, ranges)
