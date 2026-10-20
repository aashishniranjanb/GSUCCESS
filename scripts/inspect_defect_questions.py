import fitz # PyMuPDF
import pypdfium2 as pdfium
import re
import os
import json

papers = {
    2017: r"PYQs 2026-2010\GPAT_QPAK_2017.pdf",
    2014: r"PYQs 2026-2010\GPAT_QPAK_2014-2.pdf",
    2012: r"PYQs 2026-2010\GPAT_QPAK_2012-2.pdf",
    2022: r"PYQs 2026-2010\GPAT_QPAK_2022-1.pdf",
    2015: r"PYQs 2026-2010\GPAT_QPAK_2015.pdf"
}

def inspect_question_in_pdf(year, qnum):
    pdf_path = papers.get(year)
    if not pdf_path or not os.path.exists(pdf_path):
        print(f"Missing PDF for {year}: {pdf_path}")
        return
    doc = fitz.open(pdf_path)
    print(f"\n==================== GPAT {year} Q{qnum} ====================")
    found = False
    for p_idx, page in enumerate(doc):
        text = page.get_text()
        # Search for question number pattern
        pattern = rf"(?:^|\n)\s*{qnum}\.\s*(.*?)(?=(?:\n\s*{qnum+1}\.\s*)|$)"
        m = re.search(pattern, text, re.DOTALL)
        if m:
            print(f"Found on Page {p_idx+1}:")
            preview = m.group(1).strip()
            print(preview[:300] + "...")
            found = True
            break
    if not found:
        print(f"Q{qnum} not matched by regex in text; checking rects/images...")

# Inspect the 5 missing visual option questions
inspect_question_in_pdf(2017, 84)
inspect_question_in_pdf(2017, 87)
inspect_question_in_pdf(2014, 103)
inspect_question_in_pdf(2012, 116)
inspect_question_in_pdf(2012, 117)

# Inspect the 2 short stem questions
inspect_question_in_pdf(2022, 92)
inspect_question_in_pdf(2015, 71)
