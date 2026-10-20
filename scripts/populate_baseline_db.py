import json
import sqlite3
import os
import sys
from datetime import datetime, timezone

DB_PATH = os.environ.get("GPAT_DB_PATH", "gpat_knowledge.db")

def populate_baseline(db_path, dry_run=False):
    print(f"Connecting to {db_path} (dry_run={dry_run})...")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    build_id = "build_baseline_v1_0"
    now_iso = datetime.now(timezone.utc).isoformat()

    # Load JSON files
    with open('baseline/source_manifest.json', 'r', encoding='utf-8') as f:
        sources = json.load(f)
    with open('baseline/subjects.json', 'r', encoding='utf-8') as f:
        subjects = json.load(f)
    with open('baseline/topics.json', 'r', encoding='utf-8') as f:
        topics = json.load(f)
    with open('baseline/weightage_evidence.json', 'r', encoding='utf-8') as f:
        weightage = json.load(f)
    with open('baseline/chunks/baseline_chunks.json', 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    with open('baseline/baseline_graph.json', 'r', encoding='utf-8') as f:
        graph = json.load(f)

    if dry_run:
        print(f"[DRY-RUN] Would record build: {build_id}")
        print(f"[DRY-RUN] Sources: {len(sources)}")
        print(f"[DRY-RUN] Subjects: {len(subjects)}")
        print(f"[DRY-RUN] Topics: {len(topics)}")
        print(f"[DRY-RUN] Weightage entries: {len(weightage)}")
        print(f"[DRY-RUN] Chunks: {len(chunks)}")
        print(f"[DRY-RUN] Graph edges: {len(graph['edges'])}")
        conn.close()
        return

    # 1. Insert Build Record
    cur.execute("""
        INSERT OR REPLACE INTO baseline_builds (
            build_id, version, build_timestamp, source_count, subject_count,
            topic_count, chunk_count, graph_node_count, graph_edge_count,
            embedding_model, embedding_dimensions, status, completed_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        build_id, "1.0.0", now_iso, len(sources), len(subjects),
        len(topics), len(chunks), len(graph["nodes"]), len(graph["edges"]),
        "sentence-transformers/all-MiniLM-L6-v2", 384, "COMPLETED", now_iso
    ))

    # 2. Insert Baseline Sources
    for s in sources:
        cur.execute("""
            INSERT OR REPLACE INTO baseline_sources (
                source_id, filename, original_path, sha256, size_bytes,
                title, authority_category, conversion_status, conversion_tool,
                conversion_version, markdown_output_path, warnings_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            s["source_id"], s["filename"], s["original_path"], s["sha256"], s["size_bytes"],
            s["title"], s["authority_category"], s["conversion_status"], s["conversion_tool"],
            s["conversion_version"], s["markdown_output_path"], json.dumps(s.get("warnings", [])), now_iso
        ))

    # 3. Insert Baseline Subjects
    for sub in subjects:
        cur.execute("""
            INSERT OR REPLACE INTO baseline_subjects (
                subject_id, name, original_label, source_ids_json,
                source_pages_json, status, created_at, build_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            sub["subject_id"], sub["name"], sub["original_label"],
            json.dumps(sub["source_ids"]), json.dumps(sub.get("source_pages", [])),
            sub["status"], now_iso, build_id
        ))

    # 4. Insert Baseline Topics
    for t in topics:
        cur.execute("""
            INSERT OR REPLACE INTO baseline_topics (
                topic_id, name, original_label, subject_id, unit_id,
                parent_topic_id, source_ids_json, source_pages_json,
                existing_concept_id, extraction_status, verification_status,
                created_at, build_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            t["topic_id"], t["name"], t["original_label"], t["subject_id"], t["unit_id"],
            t.get("parent_topic_id"), json.dumps(t["source_ids"]),
            json.dumps(t.get("source_pages", [])), t.get("existing_concept_id"),
            t["extraction_status"], t["verification_status"], now_iso, build_id
        ))

    # 5. Insert Baseline Weightage Evidence
    for w in weightage:
        cur.execute("""
            INSERT OR REPLACE INTO baseline_weightage_evidence (
                evidence_id, source_id, source_filename, page_or_section,
                subject_id, topic_id, reported_value, reported_unit,
                total_context, stated_year, methodology, authority_status,
                confidence, exact_quote, notes, created_at, build_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            w["evidence_id"], w["source_id"], w["source_filename"], w["page_or_section"],
            w.get("subject_id"), w.get("topic_id"), w["reported_value"], w["reported_unit"],
            w["total_context"], w["stated_year"], w["methodology"], w["authority_status"],
            w["confidence"], w["exact_quote"], w.get("notes"), now_iso, build_id
        ))

    # 6. Insert Baseline Chunks
    for chk in chunks:
        cur.execute("""
            INSERT OR REPLACE INTO baseline_chunks (
                chunk_id, source_id, source_hash, heading_path, content,
                content_type, embedding_model, created_at, build_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            chk["chunk_id"], chk["source_id"], chk["source_hash"],
            chk["heading_path"], chk["content"], chk["content_type"],
            chk["embedding_model"], now_iso, build_id
        ))

    # 7. Insert Baseline Graph Edges
    for edge in graph["edges"]:
        cur.execute("""
            INSERT OR REPLACE INTO baseline_graph_edges (
                source_node, target_node, relationship, provenance, evidence, created_at, build_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            edge["source"], edge["target"], edge["relationship"],
            edge["provenance"], edge["evidence"], now_iso, build_id
        ))

    conn.commit()
    conn.close()
    print("Database population complete and committed.")

if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    db = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else DB_PATH
    populate_baseline(db, dry_run=dry_run)
