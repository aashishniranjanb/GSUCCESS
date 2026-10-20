"""
Migration Script: Step 1 - Canonical Syllabus Hierarchy & Multimodal Content Schema.

Applies non-destructive schema additions to data/gpat_baseline.db:
1. syllabus_versions (Official regulatory reference metadata)
2. curriculum_subjects (19 distinct academic courses mapped to the 5 exam groups)
3. units (Pedagogical unit chapters within curriculum courses)
4. learning_objectives (Level 5 atomic competencies & flashcard hooks)
5. topic_content_links (Many-to-many associations between topics and content assets)
6. Adds curriculum_subject_id to baseline_topics if not present.
7. Populates the 19 curriculum subjects and links existing 221 topics.
"""

import os
import sqlite3
import datetime
from datetime import timezone
from pathlib import Path
import json

ROOT_DIR = Path(__file__).resolve().parent.parent
BASELINE_DB = ROOT_DIR / "data" / "gpat_baseline.db"
TOPICS_JSON = ROOT_DIR / "baseline" / "topics.json"

CURRICULUM_METADATA = {
    # Pharmaceutics & Allied
    "pharmaceutics__pharmaceutics": {
        "exam_subject_id": "pharmaceutics",
        "name": "General & Industrial Pharmacy",
        "pci_code": "BP103T / BP502T",
        "semester": 1,
        "desc": "Dosage form design, formulation principles, pilot plant scale-up and novel drug delivery systems."
    },
    "pharmaceutics__physical_pharmacy": {
        "exam_subject_id": "pharmaceutics",
        "name": "Physical Pharmaceutics",
        "pci_code": "BP302T / BP403T",
        "semester": 3,
        "desc": "States of matter, micromeritics, surface tension, viscosity, rheology and dispersion systems."
    },
    "pharmaceutics__biopharmaceutics_and_pharmacokinetics": {
        "exam_subject_id": "pharmaceutics",
        "name": "Biopharmaceutics and Pharmacokinetics",
        "pci_code": "BP604T",
        "semester": 6,
        "desc": "Drug absorption, distribution, metabolism, elimination, bio-availability and compartment models."
    },
    "pharmaceutics__dispensing": {
        "exam_subject_id": "pharmaceutics",
        "name": "Dispensing and Hospital Pharmacy",
        "pci_code": "BP703T",
        "semester": 7,
        "desc": "Prescription handling, posology, compounding, hospital formulary and patient counseling."
    },
    "pharmaceutics__pharmaceutical_engineering": {
        "exam_subject_id": "pharmaceutics",
        "name": "Pharmaceutical Engineering",
        "pci_code": "BP304T",
        "semester": 3,
        "desc": "Fluid flow, heat transfer, drying, distillation, filtration and size reduction unit operations."
    },

    # Pharmaceutical Chemistry & Allied
    "pharmaceutical_chemistry__physical_chemistry": {
        "exam_subject_id": "pharmaceutical_chemistry",
        "name": "Physical Chemistry",
        "pci_code": "BP102T",
        "semester": 1,
        "desc": "Thermodynamics, chemical kinetics, solutions, electrochemistry and phase equilibria."
    },
    "pharmaceutical_chemistry__organic_chemistry": {
        "exam_subject_id": "pharmaceutical_chemistry",
        "name": "Pharmaceutical Organic Chemistry",
        "pci_code": "BP202T / BP301T / BP401T",
        "semester": 2,
        "desc": "Nomenclature, isomerism, reaction mechanisms, pericyclic reactions and heterocyclic chemistry."
    },
    "pharmaceutical_chemistry__pharmaceutical_chemistry": {
        "exam_subject_id": "pharmaceutical_chemistry",
        "name": "Medicinal Chemistry",
        "pci_code": "BP501T / BP601T",
        "semester": 5,
        "desc": "Structure-activity relationships (SAR), synthesis, metabolism and mechanism of therapeutic agents."
    },
    "pharmaceutical_chemistry__pharmaceutical_analysis": {
        "exam_subject_id": "pharmaceutical_chemistry",
        "name": "Pharmaceutical Analysis & Instrumentation",
        "pci_code": "BP102T / BP701T",
        "semester": 1,
        "desc": "Titrations, UV-Vis, IR, NMR, Mass spectrometry, chromatography and validation parameters."
    },
    "pharmaceutical_chemistry__biochemistry": {
        "exam_subject_id": "pharmaceutical_chemistry",
        "name": "Biochemistry",
        "pci_code": "BP203T",
        "semester": 2,
        "desc": "Biomolecules, bioenergetics, metabolic pathways (carbohydrates, lipids, proteins) and molecular biology."
    },

    # Pharmacology & Allied
    "pharmacology__pharmacology": {
        "exam_subject_id": "pharmacology",
        "name": "Systemic Pharmacology & Chemotherapy",
        "pci_code": "BP404T / BP503T / BP602T",
        "semester": 4,
        "desc": "Pharmacodynamics, autonomic, cardiovascular, CNS, endocrine pharmacology and antimicrobial chemotherapy."
    },
    "pharmacology__anatomy_physiology_and_health_education": {
        "exam_subject_id": "pharmacology",
        "name": "Human Anatomy and Physiology (HAP)",
        "pci_code": "BP101T / BP201T",
        "semester": 1,
        "desc": "Organ systems, histology, neurophysiology, cardiovascular and renal physiology."
    },
    "pharmacology__pathophysiology": {
        "exam_subject_id": "pharmacology",
        "name": "Pathophysiology",
        "pci_code": "BP204T",
        "semester": 2,
        "desc": "Cellular injury, inflammation, etiology and manifestations of major clinical diseases."
    },
    "pharmacology__clinical_pharmacy_and_therapeutics": {
        "exam_subject_id": "pharmacology",
        "name": "Clinical Pharmacy and Pharmacotherapeutics",
        "pci_code": "BP703T / BP801T",
        "semester": 7,
        "desc": "Therapeutic drug monitoring, drug interactions, adverse drug reactions and clinical trials."
    },

    # Pharmacognosy & Allied
    "pharmacognosy__pharmacognosy": {
        "exam_subject_id": "pharmacognosy",
        "name": "Pharmacognosy and Phytochemistry",
        "pci_code": "BP405T / BP504T",
        "semester": 4,
        "desc": "Classification, crude drugs, isolation, secondary metabolites (alkaloids, glycosides, terpenoids) and herbal standards."
    },

    # Other B.Pharm Subjects
    "other_subjects__microbiology": {
        "exam_subject_id": "other_subjects",
        "name": "Pharmaceutical Microbiology",
        "pci_code": "BP301T",
        "semester": 3,
        "desc": "Morphology, staining, sterilization, microbiological assays, microbial contamination and cleanroom standards."
    },
    "other_subjects__biotechnology": {
        "exam_subject_id": "other_subjects",
        "name": "Pharmaceutical Biotechnology",
        "pci_code": "BP605T",
        "semester": 6,
        "desc": "Recombinant DNA technology, fermenters, monoclonal antibodies, vaccines and plant tissue culture."
    },
    "other_subjects__pharmaceutical_jurisprudence": {
        "exam_subject_id": "other_subjects",
        "name": "Pharmaceutical Jurisprudence & Ethics",
        "pci_code": "BP505T",
        "semester": 5,
        "desc": "Drugs & Cosmetics Act 1940, Pharmacy Act 1948, NDPS Act, DPCO, patent law and code of pharmaceutical ethics."
    },
    "other_subjects__pharmaceutical_management": {
        "exam_subject_id": "other_subjects",
        "name": "Pharmaceutical Marketing & Management",
        "pci_code": "BP803ET",
        "semester": 8,
        "desc": "Marketing principles, supply chain, inventory control, clinical research management and regulatory affairs."
    }
}

def migrate_baseline_database(db_path: Path = BASELINE_DB):
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()

    print(f"Connecting to database: {db_path}")

    # 1. Create syllabus_versions table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS syllabus_versions (
        version_id TEXT PRIMARY KEY,
        authority_name TEXT NOT NULL,
        title TEXT NOT NULL,
        effective_year INTEGER NOT NULL,
        status TEXT NOT NULL,
        created_at TIMESTAMP NOT NULL
    );
    """)

    # Seed baseline syllabus versions
    now_iso = datetime.datetime.now(timezone.utc).isoformat()
    cur.execute("""
    INSERT OR IGNORE INTO syllabus_versions (version_id, authority_name, title, effective_year, status, created_at)
    VALUES 
    ('nbems_gpat_2025', 'National Board of Examinations in Medical Sciences', 'NBEMS GPAT 2025 Indicative Pattern', 2025, 'ACTIVE', ?),
    ('pci_bpharm_2024', 'Pharmacy Council of India', 'PCI B.Pharm Curriculum Regulations 2024', 2024, 'ACTIVE', ?);
    """, (now_iso, now_iso))

    # 2. Create curriculum_subjects table (Level 2)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS curriculum_subjects (
        curriculum_subject_id TEXT PRIMARY KEY,
        exam_subject_id TEXT NOT NULL,
        name TEXT NOT NULL,
        pci_course_code TEXT,
        semester_recommended INTEGER,
        description TEXT,
        FOREIGN KEY (exam_subject_id) REFERENCES baseline_subjects(subject_id)
    );
    """)

    # Populate all 19 curriculum subjects
    for c_id, meta in CURRICULUM_METADATA.items():
        cur.execute("""
        INSERT OR REPLACE INTO curriculum_subjects 
        (curriculum_subject_id, exam_subject_id, name, pci_course_code, semester_recommended, description)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (c_id, meta["exam_subject_id"], meta["name"], meta["pci_code"], meta["semester"], meta["desc"]))

    # 3. Create units table (Level 3)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS units (
        unit_id TEXT PRIMARY KEY,
        curriculum_subject_id TEXT NOT NULL,
        unit_number INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        FOREIGN KEY (curriculum_subject_id) REFERENCES curriculum_subjects(curriculum_subject_id)
    );
    """)

    # Populate default units for each curriculum subject
    for c_id, meta in CURRICULUM_METADATA.items():
        unit_id = f"{c_id}__unit_1"
        cur.execute("""
        INSERT OR IGNORE INTO units (unit_id, curriculum_subject_id, unit_number, title, description)
        VALUES (?, ?, 1, ?, ?)
        """, (unit_id, c_id, meta["name"], meta["desc"]))

    # 4. Create learning_objectives table (Level 5)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS learning_objectives (
        objective_id TEXT PRIMARY KEY,
        topic_id TEXT NOT NULL,
        code TEXT NOT NULL,
        bloom_level TEXT NOT NULL,
        objective_statement TEXT NOT NULL,
        key_formula_or_rule TEXT,
        clinical_pearl TEXT,
        created_at TIMESTAMP NOT NULL,
        FOREIGN KEY (topic_id) REFERENCES baseline_topics(topic_id)
    );
    """)

    # 5. Create topic_content_links table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS topic_content_links (
        link_id TEXT PRIMARY KEY,
        topic_id TEXT NOT NULL,
        source_id TEXT NOT NULL,
        chunk_id TEXT,
        asset_type TEXT NOT NULL, -- 'BOOK_CHAPTER', 'NOTE', 'FLASHCARD', 'PYQ', 'DIAGRAM'
        relevance_score REAL DEFAULT 1.0,
        is_primary INTEGER DEFAULT 0,
        created_at TIMESTAMP NOT NULL,
        UNIQUE(topic_id, source_id, chunk_id)
    );
    """)

    # 6. Ensure curriculum_subject_id column exists on baseline_topics
    cur.execute("PRAGMA table_info(baseline_topics)")
    cols = [r[1] for r in cur.fetchall()]
    if "curriculum_subject_id" not in cols:
        print("Adding curriculum_subject_id column to baseline_topics...")
        cur.execute("ALTER TABLE baseline_topics ADD COLUMN curriculum_subject_id TEXT REFERENCES curriculum_subjects(curriculum_subject_id);")

    # Update curriculum_subject_id on baseline_topics based on unit_id prefix
    cur.execute("""
    UPDATE baseline_topics 
    SET curriculum_subject_id = unit_id
    WHERE unit_id IN (SELECT curriculum_subject_id FROM curriculum_subjects);
    """)
    updated_count = cur.rowcount

    conn.commit()

    # Verification checks
    cur.execute("PRAGMA integrity_check")
    integrity = cur.fetchone()[0]
    cur.execute("PRAGMA foreign_key_check")
    fk_violations = cur.fetchall()

    cur.execute("SELECT count(*) FROM curriculum_subjects")
    curr_count = cur.fetchone()[0]

    cur.execute("SELECT count(*) FROM baseline_topics WHERE curriculum_subject_id IS NOT NULL")
    mapped_topics = cur.fetchone()[0]

    conn.close()

    print("Migration finished successfully.")
    print(f"- Integrity check: {integrity}")
    print(f"- FK violations: {len(fk_violations)}")
    print(f"- Curriculum subjects populated: {curr_count}")
    print(f"- Baseline topics linked to curriculum subjects: {mapped_topics} / 221")

    return {
        "status": "SUCCESS",
        "integrity": integrity,
        "fk_violations": fk_violations,
        "curriculum_subjects": curr_count,
        "mapped_topics": mapped_topics
    }

if __name__ == "__main__":
    result = migrate_baseline_database()
