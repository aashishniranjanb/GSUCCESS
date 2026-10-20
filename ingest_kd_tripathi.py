import os
import sys
import io
import json
import sqlite3
import yaml
import time
from pathlib import Path

from gpat_v0_ontology_ingestion.gpat_v0.ingestion_pipeline.app.docling_adapter import DoclingAdapter
from gpat_v0_ontology_ingestion.gpat_v0.ingestion_pipeline.app.concept_mapper import ConceptMapper
from gpat_v0_ontology_ingestion.gpat_v0.ingestion_pipeline.app.claim_extractor import ClaimExtractor
from ingest_pdf import init_sqlite_db, populate_concepts

def ingest_kd_tripathi():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    pdf_path = "Essentials of Medical Pharmacology.pdf"
    document_id = "doc_kd_tripathi"
    
    # Gold-Standard Core Chapters:
    # 1. Chapter 4: Pharmacodynamics & Receptor Pharmacology (pp. 54-65)
    # 2. Chapter 8: Anticholinergic Drugs & Ganglionic Agents (pp. 130-140)
    # 3. Chapter 9: Adrenergic System and Drugs (pp. 140-150)
    # 4. Chapter 18: Thyroid Hormone and Thyroid Inhibitors (pp. 251-260)
    # 5. Chapter 19: Insulin, Oral Hypoglycaemic Drugs and Glucagon (pp. 274-285)
    page_ranges = [(140, 150), (251, 260), (274, 285)]
    
    print(f"\n==========================================")
    print(f"INGESTING PRIMARY ACADEMIC REFERENCE (KD TRIPATHI)")
    print(f"File: {pdf_path}")
    print(f"Document ID: {document_id}")
    print(f"Target Chapters: Ch 9 (Adrenergic), Ch 18 (Thyroid), Ch 19 (Insulin & Antidiabetic)")
    print(f"Page Ranges: {page_ranges}")
    print(f"==========================================\n")
    
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
        "Essentials of Medical Pharmacology (KD Tripathi - 7th/8th Edition)",
        4, # Primary Academic / Gold Standard Authority
        1020,
        "processing"
    ))
    conn.commit()
    
    adapter = DoclingAdapter(do_ocr=False)
    mapper = ConceptMapper(seed_data)
    claim_extractor = ClaimExtractor()
    
    total_blocks_ingested = 0
    total_mapped_blocks = 0
    total_claims_extracted = 0
    
    for start_page, end_page in page_ranges:
        t0 = time.time()
        print(f"Processing KD Tripathi pages {start_page} to {end_page} with Docling...")
        doc = adapter.convert(pdf_path, page_range=(start_page, end_page))
        blocks = adapter.extract_chunks(doc, document_id=document_id)
        print(f"Extracted {len(blocks)} hybrid chunks in {time.time() - t0:.2f}s.")
        
        mapped_blocks = mapper.map_blocks(blocks)
        claims = claim_extractor.extract(mapped_blocks)
        
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
            
            for match in b.get("concept_matches", []):
                cur.execute("""
                INSERT INTO block_concept_mappings (block_id, concept_id, matched_terms, confidence)
                VALUES (?, ?, ?, ?)
                """, (
                    b["block_id"],
                    match["concept_id"],
                    json.dumps(match.get("matched_terms", [])),
                    0.98
                ))
                
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
                0.95,
                "verified" # Authoritative textbook
            ))
            
        conn.commit()
        
        mapped_count = sum(1 for b in mapped_blocks if b["concept_candidates"])
        total_blocks_ingested += len(blocks)
        total_mapped_blocks += mapped_count
        total_claims_extracted += len(claims)
        print(f"Batch complete: {mapped_count}/{len(blocks)} blocks matched concepts, {len(claims)} claims extracted.")
        
    cur.execute("UPDATE documents SET status = 'completed' WHERE id = ?", (document_id,))
    conn.commit()
    conn.close()
    
    print("\n==========================================")
    print("KD TRIPATHI INGESTION COMPLETE")
    print(f"Total Chunks Ingested: {total_blocks_ingested}")
    print(f"Chunks Mapped to Concepts: {total_mapped_blocks}")
    print(f"Authoritative Claims Extracted: {total_claims_extracted}")
    print("==========================================\n")

if __name__ == "__main__":
    ingest_kd_tripathi()
