import os
import json
import hashlib
from datetime import datetime, timezone

CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200

def chunk_text(text, source_id, source_hash):
    lines = text.splitlines()
    chunks = []
    current_chunk = []
    current_len = 0
    current_heading = "General"
    chunk_index = 0

    for line in lines:
        line_s = line.strip()
        if not line_s:
            continue
        if line_s.startswith('#') or (len(line_s) < 60 and line_s.isupper()):
            current_heading = line_s.lstrip('#').strip()

        current_chunk.append(line_s)
        current_len += len(line_s)

        if current_len >= CHUNK_SIZE:
            chunk_content = "\n".join(current_chunk)
            chunk_id = f"chk_{source_id}_{chunk_index:04d}"
            chunks.append({
                "chunk_id": chunk_id,
                "source_id": source_id,
                "source_hash": source_hash,
                "heading_path": current_heading,
                "content": chunk_content,
                "char_length": len(chunk_content),
                "content_type": "markdown_section",
                "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
                "embedding_dimensions": 384
            })
            chunk_index += 1
            # Retain overlap
            overlap_lines = current_chunk[-3:] if len(current_chunk) >= 3 else []
            current_chunk = overlap_lines
            current_len = sum(len(l) for l in overlap_lines)

    if current_chunk:
        chunk_content = "\n".join(current_chunk)
        chunk_id = f"chk_{source_id}_{chunk_index:04d}"
        chunks.append({
            "chunk_id": chunk_id,
            "source_id": source_id,
            "source_hash": source_hash,
            "heading_path": current_heading,
            "content": chunk_content,
            "char_length": len(chunk_content),
            "content_type": "markdown_section",
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            "embedding_dimensions": 384
        })

    return chunks

def main():
    with open('baseline/source_manifest.json', 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    all_chunks = []
    for item in manifest:
        md_path = item.get("markdown_output_path")
        if not md_path or not os.path.exists(md_path):
            continue

        with open(md_path, 'r', encoding='utf-8') as f:
            text = f.read()

        if len(text.strip()) < 50:
            continue

        chunks = chunk_text(text, item["source_id"], item["sha256"])
        all_chunks.extend(chunks)
        print(f"Generated {len(chunks)} chunks for {item['source_id']}")

    out_file = 'baseline/chunks/baseline_chunks.json'
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(all_chunks, f, indent=2)

    print(f"\nTotal baseline chunks generated: {len(all_chunks)}")
    print(f"Saved to {out_file}")

if __name__ == "__main__":
    main()
