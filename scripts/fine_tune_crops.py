import fitz
import os

# 1. 2017 Q84: Crop just below 'reaction most readily' (y: 448..518)
doc_2017 = fitz.open(r"PYQs 2026-2010\GPAT_QPAK_2017.pdf")
p_2017_5 = doc_2017[4]
rect_q84 = fitz.Rect(322, 448, 545, 518)
pix_q84 = p_2017_5.get_pixmap(clip=rect_q84, dpi=200)
path_q84 = "baseline/media/mcqs/pyq_gpat_2017_084_options.png"
pix_q84.save(path_q84)
print(f"Recropped 2017 Q84 -> {path_q84} ({os.path.getsize(path_q84)} bytes)")

# 2. 2017 Q87: Crop below 'most abundant (major) product' (y: 104..146)
p_2017_6 = doc_2017[5]
rect_q87 = fitz.Rect(45, 104, 295, 146)
pix_q87 = p_2017_6.get_pixmap(clip=rect_q87, dpi=200)
path_q87 = "baseline/media/mcqs/pyq_gpat_2017_087_options.png"
pix_q87.save(path_q87)
print(f"Recropped 2017 Q87 -> {path_q87} ({os.path.getsize(path_q87)} bytes)")

# 3. 2012 Q116: Crop below 'the unknown compound' (y: 520..564)
doc_2012 = fitz.open(r"PYQs 2026-2010\GPAT_QPAK_2012-2.pdf")
p_2012_9 = doc_2012[8]
rect_q116 = fitz.Rect(45, 521, 295, 564)
pix_q116 = p_2012_9.get_pixmap(clip=rect_q116, dpi=200)
path_q116 = "baseline/media/mcqs/pyq_gpat_2012_116_options.png"
pix_q116.save(path_q116)
print(f"Recropped 2012 Q116 -> {path_q116} ({os.path.getsize(path_q116)} bytes)")

# 4. 2012 Q117: Crop below 'is aromatic' (y: 588..614)
rect_q117 = fitz.Rect(45, 588, 295, 614)
pix_q117 = p_2012_9.get_pixmap(clip=rect_q117, dpi=200)
path_q117 = "baseline/media/mcqs/pyq_gpat_2012_117_options.png"
pix_q117.save(path_q117)
print(f"Recropped 2012 Q117 -> {path_q117} ({os.path.getsize(path_q117)} bytes)")
