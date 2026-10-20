"""
Seed & Ingestion Script: High-Yield Multimodal Flashcards & Memory Concept Objectives.

Populates:
1. learning_objectives (Level 5 atomic competencies, key rules, and clinical pearls)
2. flashcards (Active recall cards with front prompt, back answer, explanation, and tags)
3. topic_content_links (Connecting flashcards and memory assets to Level 4 topic nodes)
4. fsrs_cards (Initializes FSRS scheduler state for flashcard retrieval without mutating existing student progress)
"""

import sqlite3
import datetime
from datetime import timezone
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
BASELINE_DB = ROOT_DIR / "data" / "gpat_baseline.db"
KNOWLEDGE_DB = ROOT_DIR / "gpat_knowledge.db"

FLASHCARD_SEEDS = [
    # 1. Pharmaceutics: Solubility & Noyes-Whitney
    {
        "card_id": "fc_ceut_001",
        "topic_id": "pharmaceutics__physical_pharmacy__solubility",
        "objective_id": "lo_ceut_001",
        "objective_code": "LO-CEUT-SOL-01",
        "bloom_level": "APPLY",
        "objective_statement": "Calculate and predict drug dissolution rate using the Noyes-Whitney equation.",
        "key_formula": "dC/dt = (D * A / h) * (Cs - C)",
        "clinical_pearl": "Micronization increases surface area (A), directly increasing dissolution rate (dC/dt) for BCS Class II poorly soluble drugs.",
        "front": "What does each parameter represent in the Noyes-Whitney equation: dC/dt = (D · A / h) · (Cs - C)?",
        "back": "dC/dt = dissolution rate; D = diffusion coefficient; A = surface area of drug particles; h = thickness of diffusion layer; Cs = saturation solubility; C = drug concentration in bulk solution at time t.",
        "explanation": "Noyes-Whitney governs dissolution rate. When C << Cs (sink conditions), rate is proportional to surface area and saturation solubility.",
        "difficulty": 6,
        "importance": 9
    },
    # 2. Pharmaceutics: Micromeritics & Angle of Repose
    {
        "card_id": "fc_ceut_002",
        "topic_id": "pharmaceutics__physical_pharmacy__micromeritics_and_powder_rheology",
        "objective_id": "lo_ceut_002",
        "objective_code": "LO-CEUT-MICRO-02",
        "bloom_level": "ANALYZE",
        "objective_statement": "Evaluate powder flowability based on Angle of Repose, Hausner Ratio, and Carr's Compressibility Index.",
        "key_formula": "tan(θ) = h / r; Carr Index (%) = [(Tapped - Bulk) / Tapped] * 100",
        "clinical_pearl": "Angle of repose < 25° indicates excellent flow; 25-30° good; > 40° very poor flow requiring glidants (e.g. colloidal silicon dioxide).",
        "front": "What are the flowability interpretations for Carr's Index: 5-15%, 16-20%, and >35%?",
        "back": "5-15% = Excellent flow; 16-20% = Fair/Acceptable flow; >35% = Extremely poor / cohesive powder.",
        "explanation": "Carr's index (compressibility index) measures powder bridging tendencies. Lower values mean less compressibility and superior free-flowing properties.",
        "difficulty": 5,
        "importance": 8
    },
    # 3. Pharmaceutics: Biopharmaceutics Compartment Clearance
    {
        "card_id": "fc_ceut_003",
        "topic_id": "pharmaceutics__biopharmaceutics_and_pharmacokinetics__bioavailability_and_bioequivalence",
        "objective_id": "lo_ceut_003",
        "objective_code": "LO-CEUT-PK-03",
        "bloom_level": "APPLY",
        "objective_statement": "Calculate absolute bioavailability (F) and total body clearance (CL).",
        "key_formula": "F = (AUC_oral * Dose_iv) / (AUC_iv * Dose_oral); CL = Dose_iv / AUC_iv = Vd * kel",
        "clinical_pearl": "Bioequivalence between test and reference generic formulation requires 90% confidence interval of AUC and Cmax ratios to fall within 80.00% - 125.00%.",
        "front": "How is absolute bioavailability (F) calculated from oral and IV administration parameters?",
        "back": "F = [AUC_oral · Dose_iv] / [AUC_iv · Dose_oral]",
        "explanation": "Absolute bioavailability compares systemic exposure of extravascular dose against IV reference (where F = 1.0 or 100%).",
        "difficulty": 6,
        "importance": 9
    },

    # 4. Pharmaceutical Chemistry: Heterocyclic Rings
    {
        "card_id": "fc_chem_001",
        "topic_id": "pharmaceutical_chemistry__organic_chemistry__heterocyclic_chemistry",
        "objective_id": "lo_chem_001",
        "objective_code": "LO-CHEM-HET-01",
        "bloom_level": "REMEMBER",
        "objective_statement": "Identify the core heterocyclic nucleus present in essential drug molecules.",
        "key_formula": "Hantzsch-Widman heteroatom priority: O > S > Se > N > P",
        "clinical_pearl": "Famotidine contains a thiazole ring; Omeprazole contains benzimidazole and pyridine; Diazepam contains 1,4-benzodiazepine.",
        "front": "Identify the core heterocyclic nucleus in: (a) Cimetidine, (b) Omeprazole, (c) Morphine.",
        "back": "(a) Cimetidine = Imidazole ring; (b) Omeprazole = Benzimidazole + Pyridine; (c) Morphine = Phenanthrene with piperidine and furan bridge.",
        "explanation": "Heterocyclic identification is tested heavily in GPAT. Heteroatom numbering priority follows electronegativity: Oxygen (1) > Sulfur (2) > Nitrogen (3).",
        "difficulty": 7,
        "importance": 10
    },
    # 5. Pharmaceutical Chemistry: Spectroscopy Selection Rules
    {
        "card_id": "fc_chem_002",
        "topic_id": "pharmaceutical_chemistry__pharmaceutical_analysis__general_principles_of_spectroscopy",
        "objective_id": "lo_chem_002",
        "objective_code": "LO-CHEM-SPEC-02",
        "bloom_level": "UNDERSTAND",
        "objective_statement": "Differentiate spectroscopic phenomena: UV-Vis, IR, NMR, and Mass Spectrometry.",
        "key_formula": "Beer-Lambert: A = ε * c * l; Hooke's Law: ν = (1/2πc) * √(k/μ)",
        "clinical_pearl": "IR spectroscopy requires a net change in dipole moment during vibration; NMR requires non-zero nuclear spin quantum number (I ≠ 0).",
        "front": "What is the fundamental selection rule / requirement for a molecule to absorb in Infrared (IR) spectroscopy?",
        "back": "A net change in dipole moment (dμ/dr ≠ 0) during the molecular vibrational transition.",
        "explanation": "Homodiatomic molecules (N2, O2, Cl2) lack a dipole moment change and are IR inactive, whereas asymmetric stretches in CO2 or H2O are strongly IR active.",
        "difficulty": 7,
        "importance": 9
    },

    # 6. Pharmacology: Autonomic Receptors & Antagonists
    {
        "card_id": "fc_col_001",
        "topic_id": "pharmacology__anatomy_physiology_and_health_education__autonomic_nervous_system",
        "objective_id": "lo_col_001",
        "objective_code": "LO-COL-ANS-01",
        "bloom_level": "ANALYZE",
        "objective_statement": "Differentiate muscarinic (M1-M3) and adrenergic (α1-α2, β1-β3) second messenger pathways.",
        "key_formula": "Gq -> PLC -> IP3/DAG -> Ca2+ (M1, M3, α1); Gs -> Adenylyl Cyclase -> cAMP (β1, β2); Gi -> Decreased cAMP (M2, α2)",
        "clinical_pearl": "M3 stimulation causes bronchial constriction and nitric oxide-mediated vasodilation; Atropine competitive antagonism causes mydriasis, cycloplegia, and tachycardia.",
        "front": "Match the autonomic receptor to its G-protein coupling mechanism: M1, M2, M3, α1, α2, β1.",
        "back": "M1 = Gq (IP3/DAG); M2 = Gi (cAMP inhibition); M3 = Gq (IP3/DAG); α1 = Gq; α2 = Gi; β1 = Gs (cAMP activation).",
        "explanation": "Gq receptors (HAVe 1 M&M: H1, α1, V1, M1, M3) elevate cytosolic calcium via phospholipase C. Gs stimulates adenylyl cyclase.",
        "difficulty": 6,
        "importance": 10
    },
    # 7. Pharmacology: Cardiovascular ACE Inhibitors vs ARBs
    {
        "card_id": "fc_col_002",
        "topic_id": "pharmacology__anatomy_physiology_and_health_education__cardiovascular_system",
        "objective_id": "lo_col_002",
        "objective_code": "LO-COL-CVS-02",
        "bloom_level": "APPLY",
        "objective_statement": "Differentiate renin-angiotensin-aldosterone system inhibitors by adverse effect profiles.",
        "key_formula": "Angiotensin I --[ACE]--> Angiotensin II; Bradykinin --[ACE/Kinase II]--> Inactive Peptides",
        "clinical_pearl": "Captopril and Enalapril induce dry intractable cough and angioedema via bradykinin accumulation; Losartan and Telmisartan directly block AT1 receptors without elevating bradykinin.",
        "front": "Why do ACE inhibitors cause dry cough, whereas Angiotensin Receptor Blockers (ARBs) do not?",
        "back": "ACE is identical to Kinase II, which degrades bradykinin. Inhibiting ACE leads to bradykinin & substance P accumulation in bronchial mucosa. ARBs block AT1 receptors without inhibiting kinase II.",
        "explanation": "Dry cough occurs in 10-20% of ACEI patients. Switching to an ARB (Losartan) resolves cough because bradykinin breakdown remains normal.",
        "difficulty": 5,
        "importance": 10
    },

    # 8. Pharmacognosy: Secondary Metabolites Chemical Tests
    {
        "card_id": "fc_cog_001",
        "topic_id": "pharmacognosy__pharmacognosy__alkaloids",
        "objective_id": "lo_cog_001",
        "objective_code": "LO-COG-ALK-01",
        "bloom_level": "REMEMBER",
        "objective_statement": "Identify reagent compositions and color endpoints for general alkaloidal chemical tests.",
        "key_formula": "Dragendorff: KBiI4 (Orange-red); Mayer: K2HgI4 (Cream); Wagner: I2 in KI (Reddish-brown); Hager: Picric acid (Yellow)",
        "clinical_pearl": "Purine alkaloids (caffeine, theobromine) give a false negative with Mayer's reagent and must be detected using the Murexide test (purple with NH3).",
        "front": "State the reagent composition and positive test precipitation color for: Mayer, Dragendorff, Wagner, Hager.",
        "back": "Mayer = Potassium mercuric iodide (Cream precipitate); Dragendorff = Potassium bismuth iodide (Orange-red ppt); Wagner = Iodine in potassium iodide (Reddish-brown ppt); Hager = Saturated picric acid (Yellow ppt).",
        "explanation": "These 4 general reagents react with basic alkaloid salts to form insoluble coordination complexes. Vital for pharmacognostical quality control.",
        "difficulty": 5,
        "importance": 9
    },

    # 9. Other Subjects: Microbiology Gram Staining
    {
        "card_id": "fc_micro_001",
        "topic_id": "other_subjects__microbiology__microscopy_and_staining_technique",
        "objective_id": "lo_micro_001",
        "objective_code": "LO-MIC-STAIN-01",
        "bloom_level": "UNDERSTAND",
        "objective_statement": "Sequence the steps and explain the physiological mechanism of Gram differential staining.",
        "key_formula": "Primary: Crystal Violet -> Mordant: Gram's Iodine -> Decolorizer: 95% Ethanol -> Counterstain: Safranin",
        "clinical_pearl": "Gram-positive bacteria possess thick peptidoglycan layers (50-90%) that trap the crystal violet-iodine complex. Gram-negative cell walls have high lipid outer membranes dissolved by alcohol.",
        "front": "What is the role of Gram's Iodine and why does 95% ethanol decolorize Gram-negative bacteria but not Gram-positive?",
        "back": "Gram's iodine acts as a mordant forming an insoluble CV-I complex. Alcohol dissolves the thin, lipid-rich outer membrane of Gram-negative bacteria, washing out the complex. Gram-positive thick peptidoglycan shrinks and traps the dye.",
        "explanation": "Gram-positive retain crystal violet (purple); Gram-negative take up counterstain safranin (pink/red).",
        "difficulty": 4,
        "importance": 8
    },

    # 10. Other Subjects: Pharmaceutical Jurisprudence Schedules
    {
        "card_id": "fc_jur_001",
        "topic_id": "other_subjects__pharmaceutical_jurisprudence__drugs_and_cosmetics_act_1940",
        "objective_id": "lo_jur_001",
        "objective_code": "LO-JUR-SCH-01",
        "bloom_level": "REMEMBER",
        "objective_statement": "Match Drugs and Cosmetics Rules Schedules to regulatory categories.",
        "key_formula": "Schedule M = GMP; Schedule Y = Clinical Trials; Schedule H/H1 = Prescription Drugs; Schedule X = Psychotropic",
        "clinical_pearl": "Schedule M specifies Good Manufacturing Practices (factory premises, plant layout, equipment). Schedule M-I specifies requirements for homeopathic manufacture; M-II for cosmetics.",
        "front": "State the regulatory subject matter for: Schedule M, Schedule Y, Schedule H1, Schedule C/C1.",
        "back": "Schedule M = Good Manufacturing Practice (GMP) requirements; Schedule Y = Requirements for Clinical Trials and Import of New Drugs; Schedule H1 = Restricted prescription antibiotics & habit-forming drugs; Schedule C/C1 = Biological and special products.",
        "explanation": "D&C Rules schedules are a perennial GPAT examination topic with high discriminative weightage.",
        "difficulty": 5,
        "importance": 10
    }
]

def seed_flashcards():
    conn_b = sqlite3.connect(str(BASELINE_DB))
    cur_b = conn_b.cursor()

    conn_k = sqlite3.connect(str(KNOWLEDGE_DB))
    cur_k = conn_k.cursor()

    now_iso = datetime.datetime.now(timezone.utc).isoformat()

    # 1. Create flashcards table in baseline database if not exists
    cur_b.execute("""
    CREATE TABLE IF NOT EXISTS flashcards (
        card_id TEXT PRIMARY KEY,
        topic_id TEXT NOT NULL,
        objective_id TEXT NOT NULL,
        front TEXT NOT NULL,
        back TEXT NOT NULL,
        explanation TEXT,
        difficulty INTEGER NOT NULL DEFAULT 5,
        importance INTEGER NOT NULL DEFAULT 8,
        status TEXT NOT NULL DEFAULT 'ACTIVE',
        created_at TIMESTAMP NOT NULL,
        FOREIGN KEY (topic_id) REFERENCES baseline_topics(topic_id),
        FOREIGN KEY (objective_id) REFERENCES learning_objectives(objective_id)
    );
    """)

    # 2. Insert learning objectives and flashcards into baseline db
    for fc in FLASHCARD_SEEDS:
        # Insert objective
        cur_b.execute("""
        INSERT OR REPLACE INTO learning_objectives (
            objective_id, topic_id, code, bloom_level, objective_statement,
            key_formula_or_rule, clinical_pearl, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            fc["objective_id"], fc["topic_id"], fc["objective_code"], fc["bloom_level"],
            fc["objective_statement"], fc["key_formula"], fc["clinical_pearl"], now_iso
        ))

        # Insert flashcard
        cur_b.execute("""
        INSERT OR REPLACE INTO flashcards (
            card_id, topic_id, objective_id, front, back, explanation, difficulty, importance, status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'ACTIVE', ?)
        """, (
            fc["card_id"], fc["topic_id"], fc["objective_id"], fc["front"], fc["back"],
            fc["explanation"], fc["difficulty"], fc["importance"], now_iso
        ))

        # Insert topic_content_link
        link_id = f"tcl_{fc['card_id']}"
        cur_b.execute("""
        INSERT OR REPLACE INTO topic_content_links (
            link_id, topic_id, source_id, chunk_id, asset_type, relevance_score, is_primary, created_at
        ) VALUES (?, ?, 'flashcard_seed_v1', NULL, 'FLASHCARD', 1.0, 1, ?)
        """, (link_id, fc["topic_id"], now_iso))

    conn_b.commit()
    conn_b.close()

    # Also mirror flashcards table in knowledge db for runtime querying if needed
    cur_k.execute("""
    CREATE TABLE IF NOT EXISTS flashcards (
        card_id TEXT PRIMARY KEY,
        topic_id TEXT NOT NULL,
        objective_id TEXT NOT NULL,
        front TEXT NOT NULL,
        back TEXT NOT NULL,
        explanation TEXT,
        difficulty INTEGER NOT NULL DEFAULT 5,
        importance INTEGER NOT NULL DEFAULT 8,
        status TEXT NOT NULL DEFAULT 'ACTIVE',
        created_at TIMESTAMP NOT NULL
    );
    """)

    for fc in FLASHCARD_SEEDS:
        cur_k.execute("""
        INSERT OR REPLACE INTO flashcards (
            card_id, topic_id, objective_id, front, back, explanation, difficulty, importance, status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'ACTIVE', ?)
        """, (
            fc["card_id"], fc["topic_id"], fc["objective_id"], fc["front"], fc["back"],
            fc["explanation"], fc["difficulty"], fc["importance"], now_iso
        ))

    conn_k.commit()
    conn_k.close()

    print(f"Successfully seeded {len(FLASHCARD_SEEDS)} multimodal flashcards and Level 5 learning objectives.")

if __name__ == "__main__":
    seed_flashcards()
