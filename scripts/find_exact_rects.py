import fitz

def find_q_rect(pdf_path, page_num, needle):
    doc = fitz.open(pdf_path)
    page = doc[page_num - 1]
    rects = page.search_for(needle)
    print(f"[{pdf_path} Page {page_num}] '{needle}': {rects}")
    return rects

# 1. 2017 Q84
find_q_rect(r"PYQs 2026-2010\GPAT_QPAK_2017.pdf", 5, "84.")
find_q_rect(r"PYQs 2026-2010\GPAT_QPAK_2017.pdf", 5, "85.")

# 2. 2017 Q87
find_q_rect(r"PYQs 2026-2010\GPAT_QPAK_2017.pdf", 6, "87.")
find_q_rect(r"PYQs 2026-2010\GPAT_QPAK_2017.pdf", 6, "88.")

# 3. 2014 Q103
find_q_rect(r"PYQs 2026-2010\GPAT_QPAK_2014-2.pdf", 5, "103.")
find_q_rect(r"PYQs 2026-2010\GPAT_QPAK_2014-2.pdf", 5, "104.")

# 4. 2012 Q116 and Q117
find_q_rect(r"PYQs 2026-2010\GPAT_QPAK_2012-2.pdf", 9, "116.")
find_q_rect(r"PYQs 2026-2010\GPAT_QPAK_2012-2.pdf", 9, "117.")
find_q_rect(r"PYQs 2026-2010\GPAT_QPAK_2012-2.pdf", 9, "118.")
