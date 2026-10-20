import os
import sys
import json
import sqlite3
import numpy as np
import time

sys.path.insert(0, os.path.abspath("."))
from vector_index import VectorIndexEngine

DB_PATH = "data/gpat_baseline.db"
CHUNKS_FILE = "baseline/chunks/baseline_chunks.json"

def main():
    print(f"Loading chunks from {CHUNKS_FILE}...")
    with open(CHUNKS_FILE, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    print(f"Total chunks to embed: {len(chunks)}")

    engine = VectorIndexEngine(db_path=DB_PATH)
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Check baseline_chunks table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS baseline_chunks (
        chunk_id TEXT PRIMARY KEY,
        source_id TEXT NOT NULL,
        source_hash TEXT NOT NULL,
        heading_path TEXT,
        content TEXT NOT NULL,
        content_type TEXT DEFAULT 'markdown_section',
        embedding_model TEXT,
        embedding_blob BLOB,
        dimensions INTEGER DEFAULT 384,
        created_at TEXT NOT NULL
    );
    """)

    batch_size = 32
    texts = [c["content"] for c in chunks]
    ids = [c["chunk_id"] for c in chunks]
    
    print(f"Generating 384-d embeddings in batches of {batch_size}...")
    t0 = time.time()
    embeddings = engine.embed_texts(texts, batch_size=batch_size)
    elapsed = time.time() - t0
    print(f"Generated {len(embeddings)} embeddings in {elapsed:.2f}s ({len(embeddings)/elapsed:.1f} chunks/sec)")
    
    # Store into baseline_chunks and block_embeddings in data/gpat_baseline.db
    now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    for chunk, emb in zip(chunks, embeddings):
        blob = emb.astype(np.float32).tobytes()
        cur.execute("""
        INSERT OR REPLACE INTO baseline_chunks (
            chunk_id, source_id, source_hash, heading_path, content,
            content_type, embedding_model, embedding_blob, dimensions, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            chunk["chunk_id"], chunk["source_id"], chunk["source_hash"],
            chunk["heading_path"], chunk["content"], chunk["content_type"],
            "sentence-transformers/all-MiniLM-L6-v2", blob, 384, now_iso
        ))
        
        # Also store into unified block_embeddings
        cur.execute("""
        INSERT OR REPLACE INTO block_embeddings (
            block_id, embedding_blob, dimensions, model
        ) VALUES (?, ?, ?, ?)
        """, (
            chunk["chunk_id"], blob, 384, "sentence-transformers/all-MiniLM-L6-v2"
        ))

    conn.commit()
    
    cur.execute("SELECT count(*), count(embedding_blob) FROM baseline_chunks")
    cnt_total, cnt_emb = cur.fetchone()
    print(f"Verified stored baseline_chunks: {cnt_total} total, {cnt_emb} with valid 384-d BLOBs.")

    cur.execute("SELECT count(*) FROM block_embeddings")
    print(f"Total entries in block_embeddings: {cur.fetchone()[0]}")
    
    conn.close()

if __name__ == '__main__':
    main()
