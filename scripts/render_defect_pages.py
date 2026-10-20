import fitz # PyMuPDF
import os

os.makedirs("baseline/media/recovered_defects", exist_ok=True)

targets = [
    {"year": 2017, "qnum": 84, "page": 5, "pdf": r"PYQs 2026-2010\GPAT_QPAK_2017.pdf"},
    {"year": 2017, "qnum": 87, "page": 6, "pdf": r"PYQs 2026-2010\GPAT_QPAK_2017.pdf"},
    {"year": 2014, "qnum": 103, "page": 5, "pdf": r"PYQs 2026-2010\GPAT_QPAK_2014-2.pdf"},
    {"year": 2012, "qnum": 116, "page": 9, "pdf": r"PYQs 2026-2010\GPAT_QPAK_2012-2.pdf"},
    {"year": 2012, "qnum": 117, "page": 9, "pdf": r"PYQs 2026-2010\GPAT_QPAK_2012-2.pdf"},
    {"year": 2022, "qnum": 92, "page": 7, "pdf": r"PYQs 2026-2010\GPAT_QPAK_2022-1.pdf"},
    {"year": 2015, "qnum": 71, "page": 4, "pdf": r"PYQs 2026-2010\GPAT_QPAK_2015.pdf"}
]

for t in targets:
    doc = fitz.open(t["pdf"])
    page = doc[t["page"] - 1]
    pix = page.get_pixmap(dpi=150)
    out_img = f"baseline/media/recovered_defects/page_{t['year']}_q{t['qnum']}_p{t['page']}.png"
    pix.save(out_img)
    print(f"Rendered Page {t['page']} for GPAT {t['year']} Q{t['qnum']} -> {out_img}")
