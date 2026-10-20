import sqlite3
import json
import random

DB_PATH = "gpat_knowledge.db"

# Canonical high-yield question templates grounded in verified textbook concepts and claims
TEMPLATES = [
    # 1. Competitive Antagonism
    {
        "concept_id": "pd_antagonism",
        "question_type": "mcq_mechanistic",
        "difficulty": 7,
        "question_text": "In the presence of a competitive antagonist, what change is observed in the agonist log dose-response curve?",
        "options": [
            "Parallel shift to the right with unchanged maximum response (Emax)",
            "Parallel shift to the left with increased maximum response",
            "Downward shift with significant reduction of maximum response (Emax)",
            "Irreversible suppression of agonist efficacy with no curve shift"
        ],
        "correct_option": 0,
        "distractor_reasons": {
            "1": "Agonist potency decreases in competitive antagonism, so the curve shifts right, not left.",
            "2": "Reduction of Emax is characteristic of noncompetitive or irreversible antagonism.",
            "3": "Irreversible suppression occurs with noncompetitive antagonists (e.g., phenoxybenzamine)."
        },
        "explanation": "Competitive antagonists bind reversibly to the same receptor site as the agonist. The antagonism can be completely overcome by increasing agonist concentration, causing a parallel rightward shift of the dose-response curve without altering Emax.",
        "source_page": 11,
        "cue": "Competitive = Rightward parallel shift + unchanged Emax (surmountable)"
    },
    # 2. Atropine in Glaucoma
    {
        "concept_id": "ans_antimuscarinics",
        "question_type": "mcq_clinical",
        "difficulty": 7,
        "question_text": "Why is Atropine strictly contraindicated in patients suffering from narrow-angle glaucoma?",
        "options": [
            "It causes cycloplegia and mydriasis, crowding the iris into the iridocorneal angle and precipitating acute angle closure",
            "It directly constricts the canal of Schlemm by contracting the ciliary muscle",
            "It causes profound miosis, blocking aqueous humor secretion from the ciliary body",
            "It stimulates alpha-1 adrenergic receptors in the sphincter pupillae"
        ],
        "correct_option": 0,
        "distractor_reasons": {
            "1": "Atropine relaxes the ciliary muscle rather than contracting it.",
            "2": "Atropine causes mydriasis (pupillary dilation), not miosis.",
            "3": "Atropine is an antimuscarinic agent with no direct action on adrenergic alpha-1 receptors."
        },
        "explanation": "Atropine blocks M3 muscarinic receptors in the sphincter pupillae causing mydriasis and relaxation of the ciliary muscle. In narrow-angle glaucoma, the dilated iris folds back and occludes the trabecular meshwork, causing a sharp, dangerous rise in intraocular pressure.",
        "source_page": 19,
        "cue": "Atropine = Mydriasis + cycloplegia -> contraindicated in narrow-angle glaucoma"
    },
    # 3. Digoxin Mechanism of Action
    {
        "concept_id": "cvs_cardiac_glycosides",
        "question_type": "mcq_mechanistic",
        "difficulty": 8,
        "question_text": "What is the primary cellular mechanism by which Digoxin produces a positive inotropic effect in congestive heart failure?",
        "options": [
            "Inhibition of membrane-bound Na+/K+ ATPase, leading to increased intracellular calcium via Na+/Ca2+ exchange",
            "Direct stimulation of beta-1 adrenergic receptors in ventricular myocardium",
            "Selective activation of the sarcoplasmic reticulum Ca2+ ATPase (SERCA2)",
            "Blockade of L-type voltage-gated calcium channels in cardiac myocytes"
        ],
        "correct_option": 0,
        "distractor_reasons": {
            "1": "Beta-1 stimulation is the mechanism of dobutamine and epinephrine, not cardiac glycosides.",
            "2": "Digoxin does not stimulate SERCA directly; it elevates free cytosolic Ca2+ by altering Na+ gradients.",
            "3": "Blockade of L-type Ca2+ channels is the mechanism of calcium channel blockers (verapamil/diltiazem)."
        },
        "explanation": "Digoxin binds and inhibits the sarcolemmal Na+/K+ ATPase pump, causing intracellular Na+ accumulation. This diminishes the sodium gradient that drives the Na+/Ca2+ exchanger (NCX), resulting in increased cytosolic Ca2+ and enhanced myocardial contractility.",
        "source_page": 29,
        "cue": "Digoxin = Na+/K+ ATPase inhibition -> Increased intracellular Ca2+ -> Positive inotropy"
    },
    # 4. Furosemide Mechanism of Action
    {
        "concept_id": "cvs_diuretics",
        "question_type": "mcq_mechanistic",
        "difficulty": 7,
        "question_text": "Which transport system in the nephron is selectively inhibited by the high-ceiling loop diuretic Furosemide?",
        "options": [
            "Na+/K+/2Cl- cotransporter in the thick ascending limb of the loop of Henle",
            "Na+/Cl- symporter in the early distal convoluted tubule",
            "Epithelial sodium channel (ENaC) in the cortical collecting duct",
            "Carbonic anhydrase enzyme in the proximal convoluted tubule"
        ],
        "correct_option": 0,
        "distractor_reasons": {
            "1": "The Na+/Cl- cotransporter in the distal convoluted tubule is inhibited by thiazide diuretics.",
            "2": "ENaC in the collecting tubule is blocked by potassium-sparing diuretics (amiloride, triamterene).",
            "3": "Carbonic anhydrase in the proximal tubule is inhibited by acetazolamide."
        },
        "explanation": "Furosemide acts on the luminal Na+/K+/2Cl- symporter (NKCC2) in the medullary and cortical thick ascending limb of Henle's loop, blocking the reabsorption of Na+, K+, and Cl-, and abolishing the corticomedullary osmotic gradient.",
        "source_page": 33,
        "cue": "Loop Diuretics (Furosemide) = NKCC2 inhibition in Thick Ascending Limb of Henle"
    },
    # 5. Levodopa + Carbidopa Rationale
    {
        "concept_id": "cns_antiparkinsonian",
        "question_type": "mcq_clinical",
        "difficulty": 8,
        "question_text": "What is the pharmacological rationale for combining Carbidopa with Levodopa in Parkinson's disease therapy?",
        "options": [
            "Carbidopa inhibits peripheral DOPA-decarboxylase, preventing peripheral conversion of levodopa and reducing systemic adverse effects",
            "Carbidopa crosses the blood-brain barrier to enhance central dopamine synthesis",
            "Carbidopa directly stimulates post-synaptic striatal D2 dopamine receptors",
            "Carbidopa inhibits monoamine oxidase type B (MAO-B) in brain tissue"
        ],
        "correct_option": 0,
        "distractor_reasons": {
            "1": "Carbidopa is polar and does NOT cross the blood-brain barrier; its action is strictly peripheral.",
            "2": "Direct D2 stimulation is performed by dopamine agonists like bromocriptine, pramipexole, and ropinirole.",
            "3": "Inhibition of central MAO-B is the mechanism of selegiline and rasagiline."
        },
        "explanation": "Because dopamine cannot cross the blood-brain barrier, its precursor levodopa is administered. Peripheral DOPA-decarboxylase rapidly degrades levodopa before it reaches the brain. Carbidopa, a peripheral-only decarboxylase inhibitor, allows higher levels of intact levodopa to cross the BBB while drastically reducing peripheral cardiac and emetic side effects.",
        "source_page": 95,
        "cue": "Carbidopa = Peripheral DOPA decarboxylase inhibitor -> increases CNS Levodopa bioavailability"
    },
    # 6. Benzodiazepine Mechanism
    {
        "concept_id": "cns_gaba_sedative_hypnotics",
        "question_type": "mcq_mechanistic",
        "difficulty": 8,
        "question_text": "How do Benzodiazepines modulate GABA-A receptor channel kinetics compared to Barbiturates?",
        "options": [
            "Benzodiazepines increase the frequency of chloride channel opening, whereas barbiturates prolong the duration of channel opening",
            "Benzodiazepines prolong the duration of chloride channel opening without affecting opening frequency",
            "Benzodiazepines directly open the chloride channel in the complete absence of GABA",
            "Benzodiazepines block GABA reuptake into presynaptic neuronal terminals"
        ],
        "correct_option": 0,
        "distractor_reasons": {
            "1": "Prolonging channel opening duration is the characteristic action of barbiturates, not benzodiazepines.",
            "2": "Direct opening of chloride channels at high doses is seen with barbiturates, explaining their greater toxicity and lower therapeutic index.",
            "3": "GABA reuptake inhibition is the mechanism of tiagabine."
        },
        "explanation": "Benzodiazepines act allosterically on GABA-A receptors to increase the frequency of chloride ion channel opening events in response to GABA. Barbiturates increase the duration that open channels remain conductive and can directly activate channels at anesthetic concentrations.",
        "source_page": 93,
        "cue": "Benzodiazepines = FREQUENCY of GABA chloride channel opening; Barbiturates = DURATION"
    },
    # 7. Phenytoin Kinetics & Mechanism
    {
        "concept_id": "cns_antiepileptics",
        "question_type": "mcq_mechanistic",
        "difficulty": 8,
        "question_text": "Phenytoin controls generalized tonic-clonic seizures primarily by which mechanism, and what is its kinetic profile?",
        "options": [
            "Use-dependent prolongation of voltage-gated sodium channel inactivation; exhibits saturation (zero-order) kinetics at therapeutic doses",
            "T-type calcium channel blockade in thalamic neurons; exhibits strict first-order linear elimination",
            "Irreversible inhibition of GABA-transaminase enzyme; exhibits rapid zero-order renal excretion",
            "Blockade of NMDA glutamate receptors; exhibits negligible plasma protein binding"
        ],
        "correct_option": 0,
        "distractor_reasons": {
            "1": "T-type calcium channel blockade in thalamic neurons is the mechanism of ethosuximide for absence seizures.",
            "2": "GABA-transaminase inhibition is the mechanism of vigabatrin.",
            "3": "Phenytoin is highly bound to plasma albumin (~90%) and does not act via NMDA receptor blockade."
        },
        "explanation": "Phenytoin slows the rate of recovery of voltage-activated Na+ channels from the inactivated state. In addition, its hepatic elimination enzymes become saturated within or near the therapeutic range, shifting from first-order to zero-order (Michaelis-Menten) elimination kinetics.",
        "source_page": 92,
        "cue": "Phenytoin = Prolongs Na+ channel inactivation + Zero-order saturation kinetics"
    },
    # 8. ACE Inhibitors (Captopril / Enalapril)
    {
        "concept_id": "cvs_ace_inhibitors_and_arbs",
        "question_type": "mcq_clinical",
        "difficulty": 7,
        "question_text": "Why do ACE inhibitors like Captopril and Enalapril frequently cause a persistent dry cough, while ARBs like Losartan do not?",
        "options": [
            "ACE (kininase II) normally degrades bradykinin; its inhibition leads to bradykinin and substance P accumulation in bronchial tissue",
            "ACE inhibitors stimulate bronchial beta-2 adrenergic receptors causing reflex bronchospasm",
            "ACE inhibitors induce direct allergic degranulation of pulmonary mast cells",
            "ARBs selectively activate pulmonary neutral endopeptidase to clear inflammatory peptides"
        ],
        "correct_option": 0,
        "distractor_reasons": {
            "1": "Beta-2 stimulation causes bronchodilation, not dry cough.",
            "2": "The cough is a class effect mediated by kinins, not an IgE-mediated allergic degranulation.",
            "3": "ARBs block AT1 receptors and have no effect on kininase II, so bradykinin levels remain normal."
        },
        "explanation": "Angiotensin-Converting Enzyme is identical to kininase II, the enzyme that metabolizes bradykinin. Inhibiting ACE leads to bradykinin and substance P accumulation in the respiratory tract, causing cough. ARBs antagonize AT1 receptors without inhibiting kininase II.",
        "source_page": 14,
        "cue": "ACE inhibitors = Prevent bradykinin breakdown -> Dry cough + Angioedema"
    },
    # 9. Pralidoxime in Organophosphate Poisoning
    {
        "concept_id": "ans_organophosphate_poisoning",
        "question_type": "mcq_clinical",
        "difficulty": 9,
        "question_text": "What is the crucial biochemical reason that Pralidoxime (2-PAM) must be administered promptly in organophosphate poisoning?",
        "options": [
            "It reactivates phosphorylated acetylcholinesterase before the covalent bond undergoes irreversible chemical 'aging'",
            "It is a competitive antagonist of acetylcholine at central muscarinic receptors",
            "It accelerates the spontaneous hydrolysis of organophosphate molecules in blood",
            "It neutralizes organophosphates by chelating their alkyl phosphate groups"
        ],
        "correct_option": 0,
        "distractor_reasons": {
            "1": "Pralidoxime is an oxime reactivator of acetylcholinesterase, not a muscarinic antagonist (Atropine is the antagonist).",
            "2": "It does not degrade free circulating pesticide; it attacks the phosphorylated enzyme site.",
            "3": "It acts via nucleophilic oxime attack on the phosphorus atom, not simple chemical chelation."
        },
        "explanation": "Pralidoxime possesses an oxime group with high nucleophilic affinity for the phosphorus atom in phosphorylated acetylcholinesterase. If given early, it breaks the phosphorus-enzyme bond. However, if 'aging' (loss of an alkyl group) occurs, the enzyme becomes permanently refractory to reactivation.",
        "source_page": 20,
        "cue": "Pralidoxime (2-PAM) = Cholinesterase reactivator -> ineffective after enzyme aging"
    },
    # 10. Beta Blockers (Propranolol) in Asthma
    {
        "concept_id": "ans_beta_blockers",
        "question_type": "mcq_clinical",
        "difficulty": 7,
        "question_text": "Why is non-selective beta-blocker therapy (e.g. Propranolol) hazardous in patients with bronchial asthma or COPD?",
        "options": [
            "Blockade of beta-2 adrenergic receptors in bronchial smooth muscle prevents sympathetic bronchodilation and provokes bronchospasm",
            "Blockade of beta-1 receptors in the heart leads to severe pulmonary edema",
            "It stimulates pulmonary muscarinic M3 receptors causing excessive mucus hypersecretion",
            "It inhibits pulmonary surfactant production by type II alveolar cells"
        ],
        "correct_option": 0,
        "distractor_reasons": {
            "1": "Cardiac beta-1 blockade decreases heart rate and cardiac output, but does not directly cause airway bronchoconstriction.",
            "2": "Propranolol has no agonist activity at cholinergic muscarinic receptors.",
            "3": "Surfactant production is not directly impaired by clinical beta-adrenergic blockade."
        },
        "explanation": "Normal bronchial tone is maintained in part by sympathetic tone acting on beta-2 receptors to promote bronchodilation. Nonselective beta blockers like propranolol block both beta-1 and beta-2 receptors, precipitating life-threatening bronchospasm in asthmatic individuals.",
        "source_page": 29,
        "cue": "Nonselective Beta Blockers (Propranolol) = Beta-2 blockade -> bronchospasm in asthma"
    },
    # 11. Biotransformation Phase I vs Phase II
    {
        "concept_id": "pk_biotransformation",
        "question_type": "mcq_mechanistic",
        "difficulty": 7,
        "question_text": "Which of the following drug biotransformation reactions is classified as a Phase II conjugation reaction?",
        "options": [
            "Glucuronidation mediated by UDP-glucuronosyltransferase",
            "Aromatic hydroxylation mediated by Cytochrome P450 3A4",
            "Oxidative deamination mediated by Monoamine Oxidase",
            "Reductive cleavage of azo bonds by bacterial azoreductases"
        ],
        "correct_option": 0,
        "distractor_reasons": {
            "1": "Aromatic hydroxylation is a Phase I functionalization reaction.",
            "2": "Oxidative deamination is a Phase I oxidation reaction.",
            "3": "Azo reduction is a Phase I reduction reaction."
        },
        "explanation": "Phase I reactions (oxidation, reduction, hydrolysis) introduce or expose polar functional groups (-OH, -NH2, -SH, -COOH). Phase II reactions (glucuronidation, sulfation, acetylation, glutathione conjugation) couple an endogenous molecule to yield polar, water-soluble excretable conjugates.",
        "source_page": 8,
        "cue": "Phase I = Oxidation/Reduction/Hydrolysis; Phase II = Glucuronidation/Sulfation/Conjugation"
    },
    # 12. Volume of Distribution (Vd)
    {
        "concept_id": "pk_volume_of_distribution",
        "question_type": "mcq_mechanistic",
        "difficulty": 7,
        "question_text": "A drug with extensive tissue binding and high lipid solubility will typically exhibit which characteristic?",
        "options": [
            "An apparent Volume of Distribution (Vd) far exceeding the total anatomical body water volume (> 42 L)",
            "An apparent Volume of Distribution restricted strictly to the intravascular plasma volume (~ 3 L)",
            "Very rapid renal clearance unaffected by urinary pH",
            "A low elimination half-life due to rapid glomerular filtration"
        ],
        "correct_option": 0,
        "distractor_reasons": {
            "1": "Restricted Vd (~ 3–5 L) is seen with drugs that are strongly plasma-protein bound or have very high molecular weights (e.g., heparin).",
            "2": "Drugs with high tissue binding generally have low free plasma concentrations, resulting in slower renal clearance.",
            "3": "Extensive tissue distribution prolongs the terminal elimination half-life rather than decreasing it."
        },
        "explanation": "The apparent volume of distribution (Vd = Dose / Plasma Concentration) is a mathematical proportionality factor. When a drug is sequestered in peripheral tissues (e.g., chloroquine, digoxin), plasma concentration is very low, making the calculated Vd enormous (often hundreds of liters).",
        "source_page": 6,
        "cue": "High tissue binding / lipid solubility -> Enormous Vd (> 42 L, e.g. Chloroquine ~ 10,000 L)"
    },
    # 13. Dale's Vasomotor Reversal
    {
        "concept_id": "ans_adrenergic_antagonists",
        "question_type": "mcq_mechanistic",
        "difficulty": 8,
        "question_text": "What classic pharmacological phenomenon is observed when Adrenaline (Epinephrine) is administered following pretreatment with an alpha-adrenergic blocker such as Phenoxybenzamine?",
        "options": [
            "Dale's vasomotor reversal: the pressor (hypertensive) response is converted to a pure depressor (hypotensive) response",
            "Marked potentiation of the hypertensive response due to uninhibited beta-1 cardiac stimulation",
            "Complete abolition of both vascular and cardiac actions with zero change in blood pressure",
            "Severe reflexive bradycardia mediated by muscarinic M2 receptor activation"
        ],
        "correct_option": 0,
        "distractor_reasons": {
            "1": "Beta-1 increases cardiac output, but vasodilatory beta-2 receptor stimulation in skeletal muscle vascular beds causes net blood pressure to drop when vasoconstrictor alpha-1 receptors are blocked.",
            "2": "Adrenaline still activates beta-1 and beta-2 receptors; it is not abolished.",
            "3": "Blood pressure drops rather than rises, so reflex tachycardia occurs, not bradycardia."
        },
        "explanation": "Adrenaline stimulates both alpha (vasoconstrictor) and beta-2 (vasodilator) adrenergic receptors. When alpha receptors are blocked by an alpha antagonist, the unmasked beta-2 receptor activation causes vasodilation, reversing the normal rise in BP to a fall (Dale's vasomotor reversal). Noradrenaline does not show this reversal because it has negligible beta-2 activity.",
        "source_page": 142,
        "cue": "Dale's Vasomotor Reversal: Adrenaline + Alpha Blocker -> Fall in BP (Unmasked Beta-2 Vasodilation)"
    },
    # 14. Propylthiouracil vs Carbimazole in Thyroid Storm
    {
        "concept_id": "endo_thyroid_drugs",
        "question_type": "mcq_clinical",
        "difficulty": 8,
        "question_text": "Why is Propylthiouracil (PTU) preferred over Methimazole/Carbimazole in the acute emergency management of severe hyperthyroidism (Thyroid Storm)?",
        "options": [
            "It rapidly inhibits the peripheral deiodination of T4 to active T3 in addition to blocking thyroid peroxidase",
            "It directly destroys pre-formed thyroid follicles releasing colloidal thyroxine",
            "It has a significantly longer half-life and crosses placental barriers more freely",
            "It acts as a competitive antagonist directly at nuclear thyroid hormone receptors (TR-alpha/beta)"
        ],
        "correct_option": 0,
        "distractor_reasons": {
            "1": "Thionamides do not destroy follicles; radioactive iodine (I-131) destroys thyroid tissue.",
            "2": "PTU has a shorter half-life and crosses the placenta less readily (preferred in 1st trimester pregnancy).",
            "3": "PTU does not block thyroid nuclear receptors; it inhibits hormone synthesis and peripheral conversion."
        },
        "explanation": "Both PTU and methimazole inhibit thyroid peroxidase (TPO) to block iodination and coupling. However, only Propylthiouracil (PTU) also inhibits peripheral 5'-deiodinase, preventing the conversion of T4 into the much more potent T3, providing faster clinical benefit during acute thyroid storm.",
        "source_page": 254,
        "cue": "PTU = Blocks Thyroid Peroxidase + Inhibits Peripheral T4 -> T3 conversion (Thyroid Storm choice)"
    },
    # 15. Metformin Mechanism of Action
    {
        "concept_id": "endo_antidiabetic_drugs",
        "question_type": "mcq_mechanistic",
        "difficulty": 7,
        "question_text": "What is the primary molecular mechanism responsible for the antihyperglycemic effect of the biguanide Metformin?",
        "options": [
            "Activation of AMP-activated protein kinase (AMPK), suppressing hepatic gluconeogenesis and enhancing peripheral glucose uptake",
            "Closure of ATP-sensitive K+ channels on pancreatic beta cells, triggering insulin exocytosis",
            "Inhibition of sodium-glucose cotransporter-2 (SGLT2) in the proximal renal tubules",
            "Selective agonism of peroxisome proliferator-activated receptor gamma (PPAR-gamma)"
        ],
        "correct_option": 0,
        "distractor_reasons": {
            "1": "Closure of ATP-sensitive K+ channels is the insulin secretagogue mechanism of Sulfonylureas (e.g., Glimepiride).",
            "2": "Inhibition of SGLT2 is the mechanism of Gliflozins (e.g., Dapagliflozin, Empagliflozin).",
            "3": "PPAR-gamma agonism is the mechanism of Thiazolidinediones (e.g., Pioglitazone)."
        },
        "explanation": "Metformin activates AMPK (AMP-activated protein kinase) in hepatocytes and skeletal muscle. This leads to downregulation of key gluconeogenic enzymes (reducing hepatic glucose output) and increases GLUT4 translocation, enhancing insulin sensitivity without causing hypoglycemia or weight gain.",
        "source_page": 278,
        "cue": "Metformin (Biguanide) = AMPK activation -> Decreased hepatic gluconeogenesis (Euglycemic)"
    }
]

def init_question_bank(db_path: str = DB_PATH):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS questions (
        id TEXT PRIMARY KEY,
        concept_id TEXT NOT NULL,
        question_type TEXT NOT NULL,
        difficulty INTEGER NOT NULL,
        question_text TEXT NOT NULL,
        options_json TEXT NOT NULL,
        correct_option INTEGER NOT NULL,
        distractor_reasons_json TEXT NOT NULL,
        explanation TEXT NOT NULL,
        source_page INTEGER NOT NULL,
        cue TEXT,
        FOREIGN KEY (concept_id) REFERENCES concepts(id)
    );
    """)
    
    for idx, t in enumerate(TEMPLATES, 1):
        q_id = f"q_gpat_{idx:03d}"
        cur.execute("""
        INSERT OR REPLACE INTO questions 
        (id, concept_id, question_type, difficulty, question_text, options_json, correct_option, distractor_reasons_json, explanation, source_page, cue)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            q_id,
            t["concept_id"],
            t["question_type"],
            t["difficulty"],
            t["question_text"],
            json.dumps(t["options"]),
            t["correct_option"],
            json.dumps(t["distractor_reasons"]),
            t["explanation"],
            t["source_page"],
            t["cue"]
        ))
        
    conn.commit()
    print(f"Populated {len(TEMPLATES)} active-recall questions into questions table.")
    conn.close()

if __name__ == "__main__":
    init_question_bank()
