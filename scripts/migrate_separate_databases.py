"""
Database Separation Architecture Specification & Migration Script
Target:
1. data/gpat_baseline.db:
   - baseline_sources
   - baseline_builds
   - baseline_subjects
   - baseline_topics
   - baseline_weightage_evidence
   - baseline_claims
   - baseline_chunks
   - baseline_graph_edges
   - baseline_questions (MCQs with images & distractor reasons)
   - baseline_media (images, figures, chemical structures)
   - content_blocks (canonical textbook blocks)
   - block_embeddings (384-dimensional vector embeddings)
   - block_concept_mappings
   - concepts
   - graph_nodes
   - graph_edges
   - documents

2. gpat_knowledge.db (Preserved Learner DB):
   - student_attempts
   - student_misconceptions
   - fsrs_cards
   - concept_memory_state
   - study_sessions
   - study_session_items
   - synced_client_events
   - learning_events
   - mock_exams
   - mock_exam_items
   - mock_attempts
   - evaluation_runs
"""

import os
import sqlite3
import json
import shutil

SOURCE_DB = "gpat_knowledge.db"
TARGET_BASELINE_DB = "data/gpat_baseline.db"

def separate_databases():
    print(f"Creating isolated static database: {TARGET_BASELINE_DB}...")
    os.makedirs("data", exist_ok=True)
    
    src_conn = sqlite3.connect(SOURCE_DB)
    src_cur = src_conn.cursor()
    
    tgt_conn = sqlite3.connect(TARGET_BASELINE_DB)
    tgt_cur = tgt_conn.cursor()
    
    # Tables to move/replicate in baseline DB
    baseline_tables = [
        "documents",
        "content_blocks",
        "block_embeddings",
        "block_concept_mappings",
        "concepts",
        "candidate_claims",
        "graph_nodes",
        "graph_edges",
        "questions",
        "baseline_sources",
        "baseline_builds",
        "baseline_subjects",
        "baseline_topics",
        "baseline_weightage_evidence",
        "baseline_claims",
        "baseline_chunks",
        "baseline_graph_edges"
    ]
    
    for tbl in baseline_tables:
        src_cur.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{tbl}'")
        row = src_cur.fetchone()
        if not row or not row[0]:
            print(f"  [SKIP] Table {tbl} does not exist in source DB.")
            continue
            
        create_sql = row[0]
        tgt_cur.execute(f"DROP TABLE IF EXISTS [{tbl}]")
        tgt_cur.execute(create_sql)
        
        # Copy all data
        src_cur.execute(f"SELECT * FROM [{tbl}]")
        rows = src_cur.fetchall()
        if rows:
            placeholders = ",".join(["?"] * len(rows[0]))
            tgt_cur.executemany(f"INSERT INTO [{tbl}] VALUES ({placeholders})", rows)
        print(f"  [COPIED] {tbl}: {len(rows)} rows -> {TARGET_BASELINE_DB}")
        
    # Create new baseline_media and baseline_questions tables in target
    tgt_cur.execute("""
    CREATE TABLE IF NOT EXISTS baseline_media (
        media_id TEXT PRIMARY KEY,
        media_type TEXT NOT NULL CHECK (media_type IN ('DIAGRAM', 'CHEMICAL_STRUCTURE', 'GRAPH', 'TABLE_IMAGE', 'ANATOMY_FIGURE')),
        relative_file_path TEXT NOT NULL,
        file_sha256 TEXT NOT NULL,
        alt_text TEXT NOT NULL,
        caption TEXT,
        source_id TEXT,
        page_number INTEGER,
        rights_status TEXT DEFAULT 'FAIR_USE_EDUCATIONAL',
        created_at TEXT NOT NULL
    );
    """)
    
    tgt_cur.execute("""
    CREATE TABLE IF NOT EXISTS baseline_questions (
        id TEXT PRIMARY KEY,
        concept_id TEXT NOT NULL,
        topic_id TEXT,
        question_type TEXT NOT NULL DEFAULT 'single_choice',
        cognitive_level TEXT DEFAULT 'FACTUAL_RECALL',
        difficulty INTEGER NOT NULL,
        question_text TEXT NOT NULL,
        media_id TEXT,
        options_json TEXT NOT NULL,
        correct_option INTEGER NOT NULL,
        distractor_reasons_json TEXT NOT NULL,
        explanation TEXT NOT NULL,
        source_page INTEGER NOT NULL,
        provenance TEXT DEFAULT 'EXPERT_VERIFIED_ORIGINAL',
        verification_status TEXT DEFAULT 'VERIFIED',
        duplicate_fingerprint TEXT,
        cue TEXT,
        FOREIGN KEY (media_id) REFERENCES baseline_media(media_id)
    );
    """)
    
    tgt_conn.commit()
    
    # Run PRAGMA checks on target
    tgt_cur.execute("PRAGMA integrity_check")
    ic = tgt_cur.fetchone()[0]
    tgt_cur.execute("PRAGMA foreign_key_check")
    fk = tgt_cur.fetchall()
    
    print(f"\nTarget Baseline DB Integrity: {ic}")
    print(f"Target Baseline DB FK Violations: {len(fk)}")
    
    src_conn.close()
    tgt_conn.close()
    print("Database separation script execution complete.")

if __name__ == '__main__':
    separate_databases()
