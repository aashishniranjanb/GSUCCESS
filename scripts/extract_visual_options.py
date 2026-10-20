import fitz
import hashlib
import os

os.makedirs("baseline/media/mcqs", exist_ok=True)

# 1. GPAT 2017 Q84: Page 5 (0-indexed page 4), right column bottom
# Stem: "Which of the following dienes can undergo Diels-Alder reaction most readily"
# Option diagrams: (a) (b) (c) (d) are located between y=540 and y=650, x=530 to x=860 in 150dpi coords
doc_2017 = fitz.open(r"PYQs 2026-2010\GPAT_QPAK_2017.pdf")
p_2017_5 = doc_2017[4]
# PDF rect points: width ~ 595, height ~ 842.
# Right column x is ~306..595. Q84 is around y=530..650.
rect_q84 = fitz.Rect(320, 545, 540, 660)
pix_q84 = p_2017_5.get_pixmap(clip=rect_q84, dpi=200)
path_q84 = "baseline/media/mcqs/pyq_gpat_2017_084_options.png"
pix_q84.save(path_q84)
print(f"Cropped GPAT 2017 Q84 -> {path_q84} ({os.path.getsize(path_q84)} bytes)")

# 2. GPAT 2017 Q87: Page 6 (0-indexed page 5), left column top
# Stem: "In the reaction of 2-nitrotoluene with bromine in presence of iron..."
# Options (a) (b) (c) (d) bromonitrotoluene structures are located at y=110..185, x=50..300
p_2017_6 = doc_2017[5]
rect_q87 = fitz.Rect(50, 115, 300, 185)
pix_q87 = p_2017_6.get_pixmap(clip=rect_q87, dpi=200)
path_q87 = "baseline/media/mcqs/pyq_gpat_2017_087_options.png"
pix_q87.save(path_q87)
print(f"Cropped GPAT 2017 Q87 -> {path_q87} ({os.path.getsize(path_q87)} bytes)")

# 3. GPAT 2014 Q103: Page 5 (0-indexed page 4), left column bottom
# Stem: "Identity the structure of barbituric acid"
# Options (a) (b) (c) (d) barbituric structures are at y=770..870 (or ~750..820 in points)
doc_2014 = fitz.open(r"PYQs 2026-2010\GPAT_QPAK_2014-2.pdf")
p_2014_5 = doc_2014[4]
rect_q103 = fitz.Rect(50, 770, 300, 890)
pix_q103 = p_2014_5.get_pixmap(clip=rect_q103, dpi=200)
path_q103 = "baseline/media/mcqs/pyq_gpat_2014_103_options.png"
pix_q103.save(path_q103)
print(f"Cropped GPAT 2014 Q103 -> {path_q103} ({os.path.getsize(path_q103)} bytes)")

# 4. GPAT 2012 Q116: Page 9 (0-indexed page 8), left column bottom
# Stem: "Both of the CMI and PMR spectra of an unknown compound show four absorption peaks each..."
# Dimethylcyclohexane options: around y=650..710, x=50..300
doc_2012 = fitz.open(r"PYQs 2026-2010\GPAT_QPAK_2012-2.pdf")
p_2012_9 = doc_2012[8]
rect_q116 = fitz.Rect(50, 650, 300, 715)
pix_q116 = p_2012_9.get_pixmap(clip=rect_q116, dpi=200)
path_q116 = "baseline/media/mcqs/pyq_gpat_2012_116_options.png"
pix_q116.save(path_q116)
print(f"Cropped GPAT 2012 Q116 -> {path_q116} ({os.path.getsize(path_q116)} bytes)")

# 5. GPAT 2012 Q117: Page 9 (0-indexed page 8), left column bottom
# Stem: "Out of the four given compounds choose the one which is aromatic"
# Aromatic rings: y=730..775, x=50..300
rect_q117 = fitz.Rect(50, 735, 300, 775)
pix_q117 = p_2012_9.get_pixmap(clip=rect_q117, dpi=200)
path_q117 = "baseline/media/mcqs/pyq_gpat_2012_117_options.png"
pix_q117.save(path_q117)
print(f"Cropped GPAT 2012 Q117 -> {path_q117} ({os.path.getsize(path_q117)} bytes)")
