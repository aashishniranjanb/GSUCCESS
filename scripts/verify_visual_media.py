import hashlib
import os

recovered = [
    {
        "media_id": "med_pyq_2017_084_dienes",
        "question_id": "pyq_gpat_2017_084",
        "relative_file_path": "baseline/media/mcqs/pyq_gpat_2017_084_options.png",
        "media_type": "CHEMICAL_STRUCTURE_OPTIONS",
        "alt_text": "Four conjugated diene structural choices (a) 2-methyl-1,3-pentadiene, (b) 1,3-cyclohexadiene, (c) 1,4-cyclohexadiene, (d) bicyclic diene",
        "caption": "Question 84: Diels-Alder diene candidate structures",
        "source_id": "GPAT_QPAK_2017",
        "source_file": "GPAT_QPAK_2017.pdf",
        "page_number": 5
    },
    {
        "media_id": "med_pyq_2017_087_bromonitrotoluene",
        "question_id": "pyq_gpat_2017_087",
        "relative_file_path": "baseline/media/mcqs/pyq_gpat_2017_087_options.png",
        "media_type": "CHEMICAL_STRUCTURE_OPTIONS",
        "alt_text": "Four isomeric bromonitrotoluene structures (a) 6-bromo-2-nitrotoluene, (b) 4-bromo-2-nitrotoluene, (c) 5-bromo-2-nitrotoluene, (d) 3-bromo-2-nitrotoluene",
        "caption": "Question 87: Bromonitrotoluene reaction product isomers",
        "source_id": "GPAT_QPAK_2017",
        "source_file": "GPAT_QPAK_2017.pdf",
        "page_number": 6
    },
    {
        "media_id": "med_pyq_2014_103_barbituric",
        "question_id": "pyq_gpat_2014_103",
        "relative_file_path": "baseline/media/mcqs/pyq_gpat_2014_103_options.png",
        "media_type": "CHEMICAL_STRUCTURE_OPTIONS",
        "alt_text": "Four heterocyclic pyrimidinetrione/piperidinedione structures representing barbituric acid and its isomers",
        "caption": "Question 103: Barbituric acid tautomeric and ring structures",
        "source_id": "GPAT_QPAK_2014-2",
        "source_file": "GPAT_QPAK_2014-2.pdf",
        "page_number": 5
    },
    {
        "media_id": "med_pyq_2012_116_dimethylcyclohexane",
        "question_id": "pyq_gpat_2012_116",
        "relative_file_path": "baseline/media/mcqs/pyq_gpat_2012_116_options.png",
        "media_type": "CHEMICAL_STRUCTURE_OPTIONS",
        "alt_text": "Four dimethylcyclohexane isomers: (a) 1,1-dimethylcyclohexane, (b) 1,2-dimethylcyclohexane, (c) 1,3-dimethylcyclohexane, (d) 1,4-dimethylcyclohexane",
        "caption": "Question 116: Dimethylcyclohexane isomers for PMR and CMI spectra interpretation",
        "source_id": "GPAT_QPAK_2012-2",
        "source_file": "GPAT_QPAK_2012-2.pdf",
        "page_number": 9
    },
    {
        "media_id": "med_pyq_2012_117_aromatic",
        "question_id": "pyq_gpat_2012_117",
        "relative_file_path": "baseline/media/mcqs/pyq_gpat_2012_117_options.png",
        "media_type": "CHEMICAL_STRUCTURE_OPTIONS",
        "alt_text": "Four conjugated ring systems: (a) Naphthalene, (b) Bicyclic annulene, (c) Cyclooctatetraene, (d) Cycloheptatriene",
        "caption": "Question 117: Conjugated cyclic hydrocarbon structures for aromaticity assessment",
        "source_id": "GPAT_QPAK_2012-2",
        "source_file": "GPAT_QPAK_2012-2.pdf",
        "page_number": 9
    }
]

for item in recovered:
    path = item["relative_file_path"]
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    item["file_sha256"] = h.hexdigest()
    item["size_bytes"] = os.path.getsize(path)
    print(f"Verified {item['media_id']}: SHA256={item['file_sha256'][:16]}..., Size={item['size_bytes']} bytes")

import json
with open("reports/phase6_2_recovered_visual_assets.json", "w", encoding="utf-8") as f:
    json.dump(recovered, f, indent=2)
