import sqlite3
import json
import io
import sys
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel

DB_PATH = "gpat_knowledge.db"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

class VectorIndexEngine:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        self.model = AutoModel.from_pretrained(MODEL_NAME)
        self.model.eval()
        self._init_tables()

    def _init_tables(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS block_embeddings (
            block_id TEXT PRIMARY KEY,
            embedding_blob BLOB NOT NULL,
            dimensions INTEGER NOT NULL,
            model TEXT NOT NULL,
            FOREIGN KEY (block_id) REFERENCES content_blocks(id)
        );
        """)
        conn.commit()
        conn.close()

    def embed_texts(self, texts: list[str], batch_size: int = 32) -> np.ndarray:
        all_embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            encoded = self.tokenizer(
                batch,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors="pt"
            )
            with torch.no_grad():
                out = self.model(**encoded)
                # Mean pooling
                mask = encoded["attention_mask"].unsqueeze(-1).expand(out.last_hidden_state.size()).float()
                sum_embeddings = torch.sum(out.last_hidden_state * mask, 1)
                sum_mask = torch.clamp(mask.sum(1), min=1e-9)
                pooled = sum_embeddings / sum_mask
                # L2 Normalize for fast dot product cosine similarity
                norm = torch.nn.functional.normalize(pooled, p=2, dim=1)
                all_embeddings.append(norm.cpu().numpy())
                
        return np.vstack(all_embeddings)

    def build_index(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        cur.execute("SELECT id, heading_path, content FROM content_blocks")
        rows = cur.fetchall()
        
        block_ids = []
        texts_to_embed = []
        for b_id, h_path_json, content in rows:
            h_path = json.loads(h_path_json) if h_path_json else []
            prefix = " > ".join(h_path) + ": " if h_path else ""
            texts_to_embed.append(prefix + content)
            block_ids.append(b_id)
            
        print(f"Generating 384-dimensional dense embeddings for {len(block_ids)} blocks...")
        embeddings = self.embed_texts(texts_to_embed)
        
        for b_id, emb in zip(block_ids, embeddings):
            blob = emb.astype(np.float32).tobytes()
            cur.execute("""
            INSERT OR REPLACE INTO block_embeddings (block_id, embedding_blob, dimensions, model)
            VALUES (?, ?, ?, ?)
            """, (b_id, blob, len(emb), MODEL_NAME))
            
        conn.commit()
        print(f"Vector indexing complete: {len(block_ids)} embeddings saved in block_embeddings table.")
        conn.close()

    def hybrid_search(self, query: str, top_k: int = 5, rrf_k: int = 60):
        """Execute Hybrid Search: Lexical Search + Dense Vector Search + RRF Fusion."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        # 1. Lexical Search
        terms = [w.lower() for w in query.split() if len(w) > 2]
        cur.execute("SELECT id, page_number, heading_path, content FROM content_blocks")
        all_blocks = cur.fetchall()
        
        lexical_scores = []
        for b_id, p_no, h_path, content in all_blocks:
            c_low = content.lower()
            score = sum(c_low.count(t) for t in terms)
            if score > 0:
                lexical_scores.append((b_id, score, p_no, h_path, content))
                
        lexical_scores.sort(key=lambda x: x[1], reverse=True)
        lexical_rank = {item[0]: rank for rank, item in enumerate(lexical_scores)}
        
        # 2. Dense Vector Search
        q_emb = self.embed_texts([query])[0]
        cur.execute("SELECT block_id, embedding_blob FROM block_embeddings")
        emb_rows = cur.fetchall()
        
        vector_scores = []
        for b_id, blob in emb_rows:
            emb = np.frombuffer(blob, dtype=np.float32)
            sim = float(np.dot(q_emb, emb)) # Normalized cosine similarity
            vector_scores.append((b_id, sim))
            
        vector_scores.sort(key=lambda x: x[1], reverse=True)
        vector_rank = {item[0]: rank for rank, item in enumerate(vector_scores)}
        
        # 3. Reciprocal Rank Fusion (RRF)
        # RRF_Score = 1 / (60 + lexical_rank) + 1 / (60 + vector_rank)
        block_dict = {b[0]: b for b in all_blocks}
        fused_scores = []
        all_candidate_ids = set(lexical_rank.keys()).union(set(list(vector_rank.keys())[:30]))
        
        for b_id in all_candidate_ids:
            score = 0.0
            if b_id in lexical_rank:
                score += 1.0 / (rrf_k + lexical_rank[b_id])
            if b_id in vector_rank:
                score += 1.0 / (rrf_k + vector_rank[b_id])
                
            b_info = block_dict[b_id]
            fused_scores.append({
                "block_id": b_id,
                "rrf_score": score,
                "cosine_sim": dict(vector_scores).get(b_id, 0.0),
                "page_number": b_info[1],
                "heading_path": json.loads(b_info[2]) if b_info[2] else [],
                "content": b_info[3]
            })
            
        fused_scores.sort(key=lambda x: x["rrf_score"], reverse=True)
        conn.close()
        return fused_scores[:top_k]

if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    engine = VectorIndexEngine()
    engine.build_index()
    
    test_q = "What happens to maximum response Emax during competitive inhibition?"
    print(f"\n--- Testing Hybrid RRF Search: '{test_q}' ---")
    results = engine.hybrid_search(test_q, top_k=3)
    for r in results:
        print(f"\n[RRF Score: {r['rrf_score']:.4f} | Cosine: {r['cosine_sim']:.3f} | Page {r['page_number']}]")
        print(f"Heading: {' > '.join(r['heading_path']) if r['heading_path'] else 'Text'}")
        print(f"Excerpt: {r['content'][:160]}...")
