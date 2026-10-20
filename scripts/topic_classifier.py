import json
import sqlite3
import re
from typing import Dict, Any, List, Tuple

class TopicClassifier:
    """
    Deterministic, explainable topic classifier for GPAT question papers.
    Uses:
    - 5 canonical GPAT subjects
    - 221 syllabus topics from baseline_topics
    - Domain dictionary of high-signal terminology, drug suffixes, chemical moieties, dosage forms
    """
    def __init__(self, db_path: str = "data/gpat_baseline.db"):
        self.db_path = db_path
        self.rules = self._load_rules()

    def _load_rules(self) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT topic_id, name, subject_id, original_label FROM baseline_topics")
        rows = cur.fetchall()
        conn.close()

        rules = []
        for tid, name, sid, label in rows:
            clean_name = re.sub(r'[^a-zA-Z0-9\s]', ' ', name).lower()
            topic_terms = [w for w in clean_name.split() if len(w) > 3 and w not in ["and", "with", "from", "system", "general", "allied", "basic", "drugs", "pharmacy", "study"]]
            
            # Domain-grounded terminology
            domain_terms = []
            
            # 1. Pharmacology & Therapeutics
            if "autonomic" in clean_name or "cholinergic" in clean_name or "parasympathetic" in clean_name:
                domain_terms.extend(["acetylcholine", "muscarinic", "nicotinic", "atropine", "physostigmine", "neostigmine", "pilocarpine", "bethanechol", "pralidoxime", "myasthenia"])
            elif "adrenergic" in clean_name or "sympathomimetic" in clean_name:
                domain_terms.extend(["catecholamine", "epinephrine", "norepinephrine", "isoprenaline", "propranolol", "atenolol", "metoprolol", "prazosin", "clonidine", "salbutamol", "terbutaline", "dobutamine"])
            elif "cardiovascular" in clean_name or "heart" in clean_name:
                domain_terms.extend(["digoxin", "digitoxin", "amiodarone", "quinidine", "lignocaine", "verapamil", "diltiazem", "nifedipine", "amlodipine", "captopril", "enalapril", "losartan", "nitroglycerin", "arrhythmia", "angina", "hypertension"])
            elif "diuretic" in clean_name:
                domain_terms.extend(["furosemide", "torsemide", "hydrochlorothiazide", "spironolactone", "acetazolamide", "mannitol", "loop of henle", "nephron", "collecting duct"])
            elif "central nervous system" in clean_name or "sedative" in clean_name or "cns" in clean_name:
                domain_terms.extend(["barbiturate", "phenobarbitone", "benzodiazepine", "diazepam", "lorazepam", "chlorpromazine", "haloperidol", "clozapine", "fluoxetine", "imipramine", "levodopa", "carbidopa", "phenytoin", "carbamazepine", "valproate", "ethosuximide", "morphine", "codeine", "naloxone"])
            elif "chemotherapy" in clean_name or "antibacterial" in clean_name or "antibiotics" in clean_name:
                domain_terms.extend(["penicillin", "cephalosporin", "tetracycline", "doxycycline", "streptomycin", "gentamicin", "erythromycin", "azithromycin", "ciprofloxacin", "nalidixic acid", "sulfonamide", "cotrimoxazole", "isoniazid", "rifampicin", "acyclovir", "chloroquine", "artemisinin"])
            elif "endocrine" in clean_name or "hormone" in clean_name or "diabetes" in clean_name:
                domain_terms.extend(["insulin", "metformin", "glibenclamide", "acarbose", "thyroxine", "propylthiouracil", "carbimazole", "prednisolone", "dexamethasone", "hydrocortisone", "estrogen", "progesterone", "testosterone"])

            # 2. Pharmaceutics & Dosage Forms
            elif "tablet" in clean_name or "compression" in clean_name:
                domain_terms.extend(["capping", "lamination", "mottling", "friability", "disintegration", "dissolution", "binder", "lubricant", "glidant", "diluent", "granulation", "punch", "die"])
            elif "capsule" in clean_name:
                domain_terms.extend(["gelatin", "bloom strength", "rotosort", "hard gelatin", "soft gelatin", "plasticizer", "glycerol", "sorbitol"])
            elif "suspension" in clean_name or "emulsion" in clean_name:
                domain_terms.extend(["stokes", "sedimentation", "creaming", "cracking", "phase inversion", "flocculated", "deflocculated", "zeta potential", "surfactant", "hlb value", "spans", "tweens"])
            elif "ophthalmic" in clean_name:
                domain_terms.extend(["eye drop", "isotonicty", "lacrimal", "corneal", "contact lens", "sodium chloride equivalent", "boric acid"])
            elif "parenteral" in clean_name or "sterilization" in clean_name:
                domain_terms.extend(["autoclave", "pyrogen", "limulus amebocyte lysate", "lal test", "depyrogenation", "hepa filter", "laminar airflow", "water for injection", "wfi"])
            elif "engineering" in clean_name or "distillation" in clean_name or "drying" in clean_name:
                domain_terms.extend(["mccabe thiele", "reflux ratio", "tray dryer", "spray dryer", "fluidized bed", "freeze dryer", "lyophilization", "ball mill", "hammer mill", "reynolds number", "heat exchanger"])

            # 3. Pharmaceutical Chemistry & Analysis
            elif "chromatography" in clean_name:
                domain_terms.extend(["hplc", "gas chromatography", "retention time", "retention volume", "rf value", "stationary phase", "mobile phase", "van deemter", "theoretical plates", "kovats"])
            elif "spectroscopy" in clean_name or "optical" in clean_name:
                domain_terms.extend(["beer lambert", "uv visible", "infrared", "ftir", "nmr", "chemical shift", "mass spectrometry", "molecular ion", "chromophore", "auxochrome", "bathochromic", "hypsochromic"])
            elif "titration" in clean_name or "volumetric" in clean_name or "assay" in clean_name:
                domain_terms.extend(["edta", "complexometric", "non aqueous titration", "perchloric acid", "karl fischer", "diazotization", "ceric ammonium", "indicator"])
            elif "organic" in clean_name or "reaction" in clean_name or "stereochemistry" in clean_name:
                domain_terms.extend(["diels alder", "sn1", "sn2", "e1", "e2", "markovnikov", "wittig", "beckmann", "enantiomer", "diastereomer", "optical rotation", "conformation", "chair form", "hammett"])
            elif "heterocyclic" in clean_name:
                domain_terms.extend(["pyridine", "pyrrole", "thiophene", "furan", "quinoline", "isoquinoline", "indole", "imidazole", "pyrimidine", "purine"])

            # 4. Pharmacognosy & Phytochemistry
            elif "alkaloid" in clean_name:
                domain_terms.extend(["mayer", "dragendorff", "wagner", "hager", "tropane", "indole", "quinoline", "isoquinoline", "purine", "cinchona", "belladonna", "ergot", "rauvolfia", "reserpine", "vinca", "quinine", "opium"])
            elif "glycoside" in clean_name:
                domain_terms.extend(["keller kiliani", "borntrager", "legal test", "baljet", "anthraquinone", "cardiac glycoside", "saponin", "flavonoid", "senna", "aloe", "digitalis", "liquorice", "diosgenin"])
            elif "volatile oil" in clean_name or "terpene" in clean_name:
                domain_terms.extend(["terpenoid", "monoterpene", "sesquiterpene", "eugenol", "menthol", "camphor", "clove", "cinnamon", "peppermint", "hydrodistillation"])
            elif "tannin" in clean_name or "resin" in clean_name:
                domain_terms.extend(["goldbeater", "hydrolysable", "condensed", "catechin", "podophyllum", "cannabis", "myrrh", "asafoetida"])

            # 5. Other B.Pharm Subjects (Jurisprudence, Microbiology, etc.)
            elif "jurisprudence" in clean_name or "act" in clean_name or "schedule" in clean_name:
                domain_terms.extend(["drugs and cosmetics act", "schedule m", "schedule c", "schedule h", "schedule x", "pharmacy act", "pci", "drec", "narcotic drugs", "magic remedies", "cdsco", "form 20", "form 21"])
            elif "microbiology" in clean_name or "staining" in clean_name:
                domain_terms.extend(["gram stain", "acid fast", "spore", "pasteurization", "endotoxin", "minimum inhibitory concentration", "mic", "agar", "bacterial growth"])

            all_terms = set(topic_terms + domain_terms)
            rules.append({
                "topic_id": tid,
                "topic_name": name,
                "subject_id": sid,
                "terms": [t.lower() for t in all_terms if len(t) > 2]
            })

        return rules

    def classify_question(self, stem: str, options: List[str]) -> Dict[str, Any]:
        """
        Scores text against all topic rules.
        Returns explainable classification decision.
        """
        corpus = (stem + " " + " ".join(options)).lower()
        
        matches = []
        for r in self.rules:
            matched_terms = []
            score = 0
            for term in r["terms"]:
                # Check for whole-word boundary where appropriate
                if len(term) <= 4:
                    if re.search(rf"\b{re.escape(term)}\b", corpus):
                        matched_terms.append(term)
                        score += 1
                else:
                    if term in corpus:
                        matched_terms.append(term)
                        # Multi-word exact phrase match gets higher weight
                        score += 3 if " " in term else 2
                        
            if score > 0:
                matches.append({
                    "subject_id": r["subject_id"],
                    "topic_id": r["topic_id"],
                    "topic_name": r["topic_name"],
                    "score": score,
                    "matched_terms": matched_terms
                })

        matches.sort(key=lambda m: -m["score"])

        if not matches:
            return {
                "decision": "UNMAPPED_PYQ",
                "subject_id": None,
                "topic_id": "UNMAPPED_PYQ",
                "confidence_score": 0,
                "score_components": {},
                "matched_terms": [],
                "rationale": "No specific syllabus or domain terminology matched."
            }

        top = matches[0]
        # Ambiguity check: is runner-up score equal or close in different subject?
        is_ambiguous = False
        if len(matches) > 1:
            second = matches[1]
            if second["score"] == top["score"] and second["subject_id"] != top["subject_id"]:
                is_ambiguous = True

        # Decision threshold calibrated:
        # Score >= 4 and not ambiguous: CONFIDENT_MATCH
        # Score 2..3 or ambiguous: NEEDS_REVIEW
        # Score < 2: UNMAPPED_PYQ
        if top["score"] >= 4 and not is_ambiguous:
            decision = "CONFIDENT_MATCH"
        elif top["score"] >= 2 or is_ambiguous:
            decision = "NEEDS_REVIEW"
        else:
            decision = "UNMAPPED_PYQ"

        return {
            "decision": decision,
            "subject_id": top["subject_id"] if decision != "UNMAPPED_PYQ" else None,
            "topic_id": top["topic_id"] if decision != "UNMAPPED_PYQ" else "UNMAPPED_PYQ",
            "topic_name": top["topic_name"] if decision != "UNMAPPED_PYQ" else "Unmapped Question Pool",
            "confidence_score": top["score"],
            "score_components": {"top_score": top["score"], "runner_up_score": matches[1]["score"] if len(matches) > 1 else 0},
            "matched_terms": top["matched_terms"],
            "is_ambiguous": is_ambiguous,
            "rationale": f"Matched terms: {', '.join(top['matched_terms'][:5])} (score {top['score']})"
        }
