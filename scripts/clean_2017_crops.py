import fitz
import os

doc_2017 = fitz.open(r"PYQs 2026-2010\GPAT_QPAK_2017.pdf")
p_2017_5 = doc_2017[4]
# 2017 Q84: Crop precisely from y=456 to 518
rect_q84 = fitz.Rect(322, 456, 545, 518)
pix_q84 = p_2017_5.get_pixmap(clip=rect_q84, dpi=200)
path_q84 = "baseline/media/mcqs/pyq_gpat_2017_084_options.png"
pix_q84.save(path_q84)
print(f"Cleaned 2017 Q84 -> {path_q84}")

p_2017_6 = doc_2017[5]
# 2017 Q87: Crop precisely from y=108 to 146
rect_q87 = fitz.Rect(45, 108, 295, 146)
pix_q87 = p_2017_6.get_pixmap(clip=rect_q87, dpi=200)
path_q87 = "baseline/media/mcqs/pyq_gpat_2017_087_options.png"
pix_q87.save(path_q87)
print(f"Cleaned 2017 Q87 -> {path_q87}")
