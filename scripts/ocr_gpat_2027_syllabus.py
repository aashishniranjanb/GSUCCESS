import os
import time
import json
import pypdfium2 as pdfium
import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

PDF_PATH = r"BASELINE docs\GPAT 2027 Syllabus.pdf"
OUTPUT_MD = r"baseline\sources\markdown\gpat_2027_syllabus.md"
MANIFEST_PATH = r"baseline\source_manifest.json"

def main():
    print(f"Opening {PDF_PATH}...")
    pdf = pdfium.PdfDocument(PDF_PATH)
    total_pages = len(pdf)
    print(f"Total pages: {total_pages}")
    
    extracted_pages = []
    total_chars = 0
    start_time = time.time()
    
    for page_idx in range(total_pages):
        t0 = time.time()
        page = pdf[page_idx]
        # Render at 1.5x scale (approx 150 DPI) for optimal balance of OCR accuracy and speed
        image = page.render(scale=1.5).to_pil()
        text = pytesseract.image_to_string(image)
        text_clean = text.strip()
        elapsed = time.time() - t0
        total_chars += len(text_clean)
        
        extracted_pages.append(f"<!-- Page {page_idx + 1} -->\n## Page {page_idx + 1}\n\n{text_clean}\n")
        print(f"  Page {page_idx + 1}/{total_pages} processed in {elapsed:.1f}s | chars={len(text_clean)}")
        
    full_markdown = "\n".join(extracted_pages)
    
    with open(OUTPUT_MD, 'w', encoding='utf-8') as f:
        f.write(full_markdown)
        
    total_time = time.time() - start_time
    print(f"\nOCR Complete! Total time: {total_time:.1f}s | Total characters: {total_chars:,}")
    print(f"Written to: {OUTPUT_MD}")
    
    # Update baseline/source_manifest.json
    if os.path.exists(MANIFEST_PATH):
        with open(MANIFEST_PATH, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
            
        for item in manifest:
            if item["source_id"] == "gpat_2027_syllabus":
                item["conversion_status"] = "SUCCESS"
                item["character_count"] = total_chars
                item["line_count"] = len(full_markdown.splitlines())
                item["warnings"] = ["Scanned PDF converted via Tesseract OCR v5 engine (scale 1.5x)"]
                item["conversion_tool"] = "tesseract-ocr-5.x"
                print("Updated gpat_2027_syllabus status to SUCCESS in source_manifest.json")
                
        with open(MANIFEST_PATH, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)

if __name__ == "__main__":
    main()
