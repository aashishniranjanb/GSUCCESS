import os
import re
import csv
import hashlib
import json
import pypdfium2 as pdfium

PYQ_DIR = r"C:\Users\Home\Downloads\PROJECTS\SRE_APP\PYQs 2026-2010"
OUT_CSV = r"C:\Users\Home\Downloads\PROJECTS\SRE_APP\reports\pyq_inventory.csv"
OUT_JSON = r"C:\Users\Home\Downloads\PROJECTS\SRE_APP\reports\pyq_inventory.json"

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def analyze_pdf(filename, filepath):
    size_bytes = os.path.getsize(filepath)
    file_sha = sha256_file(filepath)
    
    # Parse exam type & year
    exam_type = "GPAT" if filename.startswith("GPAT") else "GATE"
    year_match = re.search(r"(\d{4})", filename)
    year = int(year_match.group(1)) if year_match else 0
    
    paper_id = filename.replace(".pdf", "")
    
    pdf = pdfium.PdfDocument(filepath)
    page_count = len(pdf)
    
    # Scan text extractability & search for Answer Key locations
    total_chars = 0
    answer_key_pages = []
    has_selectable_text = False
    
    for i in range(page_count):
        page = pdf[i]
        textpage = page.get_textpage()
        text = textpage.get_text_range()
        chars = len(text.strip())
        total_chars += chars
        if chars > 50:
            has_selectable_text = True
            
        # Look for answer key markers
        text_lower = text.lower()
        if any(k in text_lower for k in ["answer key", "answers key", "answer sheet", "key answers", "q.no. ans", "q. no. ans", "q.no ans"]):
            answer_key_pages.append(i + 1)
        elif "ans" in text_lower and ("1." in text or "1 " in text) and i >= page_count - 4:
            # Check if looks like tabular answer key at the back
            if re.search(r"\b1\s+[A-D]\b|\b1\s*[-:]\s*[A-D]\b|\b1\.\s*[A-D]\b", text, re.IGNORECASE):
                answer_key_pages.append(i + 1)

    text_mode = "SELECTABLE_TEXT" if has_selectable_text else "SCANNED_IMAGE_ONLY"
    
    # Answer key detection confidence
    key_location_str = ",".join(map(str, sorted(list(set(answer_key_pages))))) if answer_key_pages else "NOT_DETECTED_IN_TEXT"
    key_status = "FOUND_IN_TEXT" if answer_key_pages else ("NEEDS_OCR" if not has_selectable_text else "NEEDS_MANUAL_CHECK")

    return {
        "paper_id": paper_id,
        "filename": filename,
        "exam_type": exam_type,
        "year": year,
        "page_count": page_count,
        "size_bytes": size_bytes,
        "sha256": file_sha,
        "text_mode": text_mode,
        "total_chars_extracted": total_chars,
        "detected_key_pages": key_location_str,
        "key_detection_status": key_status
    }

def main():
    files = sorted([f for f in os.listdir(PYQ_DIR) if f.lower().endswith(".pdf")])
    print(f"Inventorying {len(files)} PDFs in {PYQ_DIR}...")
    
    records = []
    for f in files:
        fp = os.path.join(PYQ_DIR, f)
        res = analyze_pdf(f, fp)
        records.append(res)
        print(f"  [{res['exam_type']} {res['year']}] {f:26s} | Pages: {res['page_count']:2d} | Mode: {res['text_mode']:16s} | Key Page: {res['detected_key_pages']}")

    # Write CSV
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "paper_id", "filename", "exam_type", "year", "page_count",
            "size_bytes", "sha256", "text_mode", "total_chars_extracted",
            "detected_key_pages", "key_detection_status"
        ])
        writer.writeheader()
        writer.writerows(records)
        
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)

    print(f"\nWritten {len(records)} records to:")
    print(f"  CSV:  {OUT_CSV}")
    print(f"  JSON: {OUT_JSON}")

if __name__ == "__main__":
    main()
