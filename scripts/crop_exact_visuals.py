import fitz
import os

os.makedirs("baseline/media/mcqs", exist_ok=True)

# 1. GPAT 2017 Q84: Page 5 (index 4)
# '84.' is at y=429, '85.' is at y=520. Options are located in y: 440..518, x: 320..550
doc_2017 = fitz.open(r"PYQs 2026-2010\GPAT_QPAK_2017.pdf")
p_2017_5 = doc_2017[4]
rect_q84 = fitz.Rect(322, 442, 545, 518)
pix_q84 = p_2017_5.get_pixmap(clip=rect_q84, dpi=200)
path_q84 = "baseline/media/mcqs/pyq_gpat_2017_084_options.png"
pix_q84.save(path_q84)
print(f"GPAT 2017 Q84 -> {path_q84} ({os.path.getsize(path_q84)} bytes)")

# 2. GPAT 2017 Q87: Page 6 (index 5)
# '87.' is at y=72, '88.' is at y=147. Options are in y: 95..145, x: 45..295
p_2017_6 = doc_2017[5]
rect_q87 = fitz.Rect(45, 96, 295, 146)
pix_q87 = p_2017_6.get_pixmap(clip=rect_q87, dpi=200)
path_q87 = "baseline/media/mcqs/pyq_gpat_2017_087_options.png"
pix_q87.save(path_q87)
print(f"GPAT 2017 Q87 -> {path_q87} ({os.path.getsize(path_q87)} bytes)")

# 3. GPAT 2014 Q103: Page 5 (index 4)
# '103.' is at y=611.8. It is the last question in the left column (y: 625..710)
doc_2014 = fitz.open(r"PYQs 2026-2010\GPAT_QPAK_2014-2.pdf")
p_2014_5 = doc_2014[4]
rect_q103 = fitz.Rect(45, 625, 295, 715)
pix_q103 = p_2014_5.get_pixmap(clip=rect_q103, dpi=200)
path_q103 = "baseline/media/mcqs/pyq_gpat_2014_103_options.png"
pix_q103.save(path_q103)
print(f"GPAT 2014 Q103 -> {path_q103} ({os.path.getsize(path_q103)} bytes)")

# 4. GPAT 2012 Q116: Page 9 (index 8)
# '116.' is at y=489.4, '117.' is at y=566.6. Options: y: 512..564, x: 45..295
doc_2012 = fitz.open(r"PYQs 2026-2010\GPAT_QPAK_2012-2.pdf")
p_2012_9 = doc_2012[8]
rect_q116 = fitz.Rect(45, 514, 295, 564)
pix_q116 = p_2012_9.get_pixmap(clip=rect_q116, dpi=200)
path_q116 = "baseline/media/mcqs/pyq_gpat_2012_116_options.png"
pix_q116.save(path_q116)
print(f"GPAT 2012 Q116 -> {path_q116} ({os.path.getsize(path_q116)} bytes)")

# 5. GPAT 2012 Q117: Page 9 (index 8)
# '117.' is at y=566.6, '118.' is at y=614.6. Options: y: 580..613, x: 45..295
rect_q117 = fitz.Rect(45, 580, 295, 614)
pix_q117 = p_2012_9.get_pixmap(clip=rect_q117, dpi=200)
path_q117 = "baseline/media/mcqs/pyq_gpat_2012_117_options.png"
pix_q117.save(path_q117)
print(f"GPAT 2012 Q117 -> {path_q117} ({os.path.getsize(path_q117)} bytes)")
