import os
import hashlib
import json
import time
from markitdown import MarkItDown

DOCS_DIR = r"C:\Users\Home\Downloads\PROJECTS\SRE_APP\BASELINE docs"
OUT_DIR = r"C:\Users\Home\Downloads\PROJECTS\SRE_APP\baseline\sources\markdown"
MANIFEST_PATH = r"C:\Users\Home\Downloads\PROJECTS\SRE_APP\baseline\source_manifest.json"

SOURCE_MAP = {
    "GDC Prime Information Brochure 2028.pdf": {
        "source_id": "gdc_prime_2028",
        "title": "GDC Prime Information Brochure 2028",
        "authority_category": "COACHING_MATERIAL"
    },
    "GPAT 2025 QP Anwer Key 2025.pdf": {
        "source_id": "gpat_2025_qp_answer_key",
        "title": "GPAT 2025 Question Paper with Answer Key",
        "authority_category": "QUESTION_PAPER"
    },
    "GPAT 2025-26 Syllabus.pdf": {
        "source_id": "gpat_2025_26_syllabus",
        "title": "GPAT 2025-26 Syllabus",
        "authority_category": "OFFICIAL_SYLLABUS"
    },
    "GPAT 2027 Syllabus.pdf": {
        "source_id": "gpat_2027_syllabus",
        "title": "GPAT 2027 Syllabus Compilation",
        "authority_category": "THIRD_PARTY_GUIDE"
    },
    "GPAT-SYLLABUS-TRACKER-2027-1.pdf": {
        "source_id": "gpat_syllabus_tracker_2027",
        "title": "GPAT 2027 Topicwise Syllabus Tracker",
        "authority_category": "USER_MATERIAL"
    },
    "ilide.info-1-gpat-2026-updated-syllabus-information-brochure-dr-pk-classes-pr_42dbe3eff5477a820afe691996dde1b3.pdf": {
        "source_id": "dr_pk_classes_brochure",
        "title": "GPAT 2026 Updated Syllabus & Brochure (Dr. PK Classes)",
        "authority_category": "THIRD_PARTY_GUIDE"
    }
}

def main():
    md_converter = MarkItDown()
    manifest_records = []
    
    for filename, meta in SOURCE_MAP.items():
        pdf_path = os.path.join(DOCS_DIR, filename)
        if not os.path.exists(pdf_path):
            print(f"[MISSING] {pdf_path}")
            continue
            
        print(f"\nProcessing {filename}...")
        start_t = time.time()
        
        # Calculate SHA-256 and size
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()
        sha256_hash = hashlib.sha256(pdf_bytes).hexdigest()
        size_bytes = len(pdf_bytes)
        
        out_filename = f"{meta['source_id']}.md"
        out_path = os.path.join(OUT_DIR, out_filename)
        
        status = "SUCCESS"
        warnings = []
        text_content = ""
        
        try:
            res = md_converter.convert(pdf_path)
            text_content = res.text_content or ""
            if len(text_content.strip()) < 100:
                warnings.append("Converted text is very short (<100 characters); check if PDF contains scanned image pages.")
                status = "PARTIAL"
        except Exception as e:
            warnings.append(f"Conversion exception: {str(e)}")
            status = "FAILED"
            
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(text_content)
            
        elapsed = time.time() - start_t
        print(f" -> {status} in {elapsed:.1f}s | chars={len(text_content):,} -> {out_filename}")
        
        manifest_records.append({
            "source_id": meta["source_id"],
            "filename": filename,
            "original_path": pdf_path,
            "sha256": sha256_hash,
            "size_bytes": size_bytes,
            "title": meta["title"],
            "authority_category": meta["authority_category"],
            "conversion_status": status,
            "conversion_tool": "markitdown",
            "conversion_version": "0.1.8",
            "markdown_output_path": os.path.relpath(out_path, r"C:\Users\Home\Downloads\PROJECTS\SRE_APP"),
            "character_count": len(text_content),
            "line_count": len(text_content.splitlines()),
            "warnings": warnings
        })
        
    with open(MANIFEST_PATH, 'w', encoding='utf-8') as f:
        json.dump(manifest_records, f, indent=2)
        
    print(f"\nSuccessfully wrote manifest to {MANIFEST_PATH}")

if __name__ == "__main__":
    main()
