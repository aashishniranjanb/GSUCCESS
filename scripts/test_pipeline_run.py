import os
import glob
from scripts.pyq_pipeline import PYQPipeline, ingest_pyq_batch
import sqlite3

def test_dry_run_extraction():
    # Test on GPAT 2024 (10 pages, key on page 6)
    pdf_path = r"PYQs 2026-2010\GPAT_QPAK_2024.pdf"
    pipeline = PYQPipeline(pdf_path=pdf_path, paper_id="GPAT_QPAK_2024", pyq_year=2024, key_page=6)
    key_map, kp = pipeline.extract_answer_key()
    print(f"GPAT 2024 Answer Key extracted: {len(key_map)} keys from page {kp}")
    
    records = pipeline.extract_questions_spatial(max_q=125)
    print(f"Extracted records: {len(records)}")
    pub = sum(1 for r in records if r["quality_status"] == "PUBLISHED")
    quar = sum(1 for r in records if r["quality_status"] != "PUBLISHED")
    print(f"Spatial Extraction: Published={pub}, Quarantined={quar}")

if __name__ == "__main__":
    test_dry_run_extraction()
