import json
import sqlite3
import re
from typing import Dict, Any, List

# Stopwords that frequently cause false matches
STOPWORDS = {
    "and", "with", "from", "system", "general", "allied", "basic", "drugs", "pharmacy",
    "study", "visible", "medicine", "crude", "extract", "heat", "transfer", "base", "acid",
    "water", "solution", "preparation", "methods", "type", "order", "class", "effect",
    "identification", "analysis", "chemical", "physical", "organic", "action", "properties"
}

class EnhancedTopicClassifier:
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
            # Only keep discriminative topic terms
            topic_terms = [w for w in clean_name.split() if len(w) > 3 and w not in STOPWORDS]
            
            domain_phrases = []
            
            # --- PHARMACOLOGY ---
            if "autonomic" in clean_name or "cholinergic" in clean_name:
                domain_phrases.extend(["acetylcholine", "muscarinic receptor", "nicotinic receptor", "atropine", "physostigmine", "neostigmine", "pilocarpine", "bethanechol", "pralidoxime", "myasthenia gravis"])
            elif "adrenergic" in clean_name or "sympathomimetic" in clean_name:
                domain_phrases.extend(["catecholamine", "epinephrine", "norepinephrine", "isoprenaline", "propranolol", "atenolol", "metoprolol", "prazosin", "clonidine", "salbutamol", "terbutaline", "dobutamine"])
            elif "cardiovascular" in clean_name or "heart" in clean_name:
                domain_phrases.extend(["cardiac glycoside", "digoxin", "digitoxin", "amiodarone", "quinidine", "lignocaine", "verapamil", "diltiazem", "nifedipine", "amlodipine", "captopril", "enalapril", "losartan", "nitroglycerin", "antiarrhythmic", "antianginal", "congestive heart failure"])
            elif "diuretic" in clean_name:
                domain_phrases.extend(["loop diuretic", "furosemide", "torsemide", "hydrochlorothiazide", "spironolactone", "acetazolamide", "loop of henle", "thick ascending limb", "collecting duct"])
            elif "central nervous system" in clean_name or "sedative" in clean_name or "antiepileptic" in clean_name:
                domain_phrases.extend(["barbiturate", "phenobarbitone", "benzodiazepine", "diazepam", "lorazepam", "chlorpromazine", "haloperidol", "clozapine", "fluoxetine", "imipramine", "levodopa", "carbidopa", "phenytoin", "carbamazepine", "valproate", "ethosuximide", "opioid receptor", "morphine", "naloxone", "antiepileptic"])
            elif "chemotherapy" in clean_name or "antibacterial" in clean_name:
                domain_phrases.extend(["penicillin", "cephalosporin", "tetracycline", "doxycycline", "aminoglycoside", "gentamicin", "macrolide", "erythromycin", "azithromycin", "fluoroquinolone", "ciprofloxacin", "nalidixic acid", "sulfonamide", "cotrimoxazole", "antitubercular", "isoniazid", "rifampicin", "antiviral", "acyclovir", "antimalarial", "chloroquine", "artemisinin"])
            elif "endocrine" in clean_name or "diabetes" in clean_name:
                domain_phrases.extend(["insulin", "hypoglycemic", "metformin", "glibenclamide", "acarbose", "thyroxine", "propylthiouracil", "carbimazole", "corticosteroid", "prednisolone", "dexamethasone"])

            # --- PHARMACEUTICS ---
            elif "tablets" in clean_name:
                domain_phrases.extend(["tablet compression", "capping", "lamination", "mottling", "friability test", "disintegration time", "dissolution apparatus", "tablet binder", "granulation", "punch and die"])
            elif "capsules" in clean_name:
                domain_phrases.extend(["hard gelatin capsule", "soft gelatin capsule", "bloom strength", "rotosort", "rotoweigh", "capsule shell", "plasticizer glycerol"])
            elif "suspension" in clean_name or "emulsion" in clean_name:
                domain_phrases.extend(["stokes law", "sedimentation velocity", "creaming", "cracking", "phase inversion", "flocculated suspension", "deflocculated", "zeta potential", "hlb value", "surfactant span", "surfactant tween"])
            elif "ophthalmic" in clean_name:
                domain_phrases.extend(["ophthalmic solution", "eye drop", "isotonicty", "lacrimal fluid", "sodium chloride equivalent", "boric acid buffer"])
            elif "parenteral" in clean_name or "sterilization" in clean_name:
                domain_phrases.extend(["autoclave sterilization", "pyrogen test", "limulus amebocyte lysate", "lal test", "depyrogenation", "hepa filter", "laminar airflow", "water for injection"])
            elif "engineering" in clean_name or "distillation" in clean_name or "drying" in clean_name:
                domain_phrases.extend(["mccabe thiele", "reflux ratio", "tray dryer", "spray dryer", "fluidized bed dryer", "freeze dryer", "lyophilization", "ball mill", "hammer mill", "kozeny carman"])

            # --- PHARMACEUTICAL CHEMISTRY ---
            elif "chromatography" in clean_name:
                domain_phrases.extend(["high performance liquid chromatography", "hplc", "gas chromatography", "retention time", "retention volume", "rf value", "stationary phase", "van deemter equation", "theoretical plates"])
            elif "spectroscopy" in clean_name:
                domain_phrases.extend(["beer lambert law", "uv visible spectroscopy", "infrared spectroscopy", "ftir", "nmr spectroscopy", "chemical shift pmr", "mass spectrometry", "molecular ion peak", "chromophore", "auxochrome", "bathochromic shift"])
            elif "titration" in clean_name or "volumetric" in clean_name:
                domain_phrases.extend(["edta titration", "complexometric titration", "non aqueous titration", "perchloric acid", "karl fischer titration", "diazotization titration", "ceric ammonium sulphate"])
            elif "organic" in clean_name or "reactions" in clean_name or "stereochemistry" in clean_name:
                domain_phrases.extend(["diels alder reaction", "sn1 reaction", "sn2 reaction", "e1 reaction", "e2 elimination", "markovnikov", "wittig reaction", "beckmann rearrangement", "enantiomer", "diastereomer", "optical rotation", "hammett constant", "conformational isomers"])
            elif "heterocyclic" in clean_name:
                domain_phrases.extend(["pyridine ring", "pyrrole", "thiophene", "furan", "quinoline ring", "isoquinoline", "indole ring", "imidazole ring", "pyrimidine ring"])

            # --- PHARMACOGNOSY ---
            elif "alkaloids" in clean_name:
                domain_phrases.extend(["mayer reagent", "dragendorff reagent", "wagner reagent", "hager reagent", "tropane alkaloid", "indole alkaloid", "quinoline alkaloid", "isoquinoline alkaloid", "cinchona bark", "belladonna", "ergot alkaloid", "rauvolfia serpentina", "reserpine", "vinca rosea", "quinine"])
            elif "glycosides" in clean_name:
                domain_phrases.extend(["keller kiliani test", "borntrager test", "legal test", "baljet test", "anthraquinone glycoside", "cardiac glycoside", "saponin glycoside", "senna leaf", "aloe vera", "digitalis purpurea", "liquorice glycyrrhiza", "chikusetsu saponin", "diosgenin"])
            elif "volatile" in clean_name or "terpenoids" in clean_name:
                domain_phrases.extend(["volatile oil", "monoterpenoid", "sesquiterpenoid", "eugenol", "menthol", "camphor", "clove oil", "cinnamon bark", "peppermint oil", "taxol diterpenoid"])
            elif "tannins" in clean_name or "resins" in clean_name:
                domain_phrases.extend(["goldbeater skin test", "hydrolysable tannin", "condensed tannin", "catechin", "podophyllum resin", "cannabis resin", "myrrh", "asafoetida"])

            # --- OTHER B.PHARM SUBJECTS ---
            elif "jurisprudence" in clean_name or "acts" in clean_name:
                domain_phrases.extend(["drugs and cosmetics act", "schedule m gmp", "schedule c", "schedule h", "schedule x", "pharmacy act 1948", "pharmacy council of india", "cdsco", "magic remedies act"])
            elif "microbiology" in clean_name:
                domain_phrases.extend(["gram staining", "acid fast staining", "bacterial spore", "pasteurization", "endotoxin", "minimum inhibitory concentration", "nutrient agar"])
            elif "anatomy" in clean_name or "physiology" in clean_name:
                domain_phrases.extend(["iris of eye", "retina", "cornea", "erythrocyte", "leukocyte", "platelet", "cardiac muscle", "action potential neuron", "glomerular filtration"])

            # Remove any empty or stopword phrases
            filtered_phrases = [p.lower() for p in (domain_phrases + topic_terms) if len(p) > 2 and p not in STOPWORDS]
            
            rules.append({
                "topic_id": tid,
                "topic_name": name,
                "subject_id": sid,
                "phrases": filtered_phrases
            })

        return rules

    def classify_question(self, stem: str, options: List[str]) -> Dict[str, Any]:
        corpus = (stem + " " + " ".join(options)).lower()
        
        matches = []
        for r in self.rules:
            matched = []
            score = 0
            for phrase in r["phrases"]:
                if " " in phrase:
                    if phrase in corpus:
                        matched.append(phrase)
                        score += 5 # High signal for multi-word domain terminology
                else:
                    # Single word match requires word boundary check
                    if re.search(rf"\b{re.escape(phrase)}\b", corpus):
                        matched.append(phrase)
                        score += 2
                        
            if score > 0:
                matches.append({
                    "subject_id": r["subject_id"],
                    "topic_id": r["topic_id"],
                    "topic_name": r["topic_name"],
                    "score": score,
                    "matched": matched
                })

        matches.sort(key=lambda x: -x["score"])

        if not matches:
            return {
                "decision": "UNMAPPED_PYQ",
                "subject_id": None,
                "topic_id": "UNMAPPED_PYQ",
                "topic_name": "Unmapped Question Pool",
                "confidence_score": 0,
                "score_components": {},
                "matched_terms": [],
                "is_ambiguous": False,
                "rationale": "No specific syllabus or domain terminology matched."
            }

        top = matches[0]
        # Ambiguity check
        is_ambiguous = False
        runner_up = 0
        if len(matches) > 1:
            runner_up = matches[1]["score"]
            if runner_up >= top["score"] - 1 and matches[1]["subject_id"] != top["subject_id"]:
                is_ambiguous = True

        # Stricter thresholds calibrated for high precision:
        # Score >= 5 and not ambiguous -> CONFIDENT_MATCH
        # Score 3..4 or ambiguous -> NEEDS_REVIEW
        # Score < 3 -> UNMAPPED_PYQ
        if top["score"] >= 5 and not is_ambiguous:
            decision = "CONFIDENT_MATCH"
        elif top["score"] >= 3 or is_ambiguous:
            decision = "NEEDS_REVIEW"
        else:
            decision = "UNMAPPED_PYQ"

        return {
            "decision": decision,
            "subject_id": top["subject_id"] if decision != "UNMAPPED_PYQ" else None,
            "topic_id": top["topic_id"] if decision != "UNMAPPED_PYQ" else "UNMAPPED_PYQ",
            "topic_name": top["topic_name"] if decision != "UNMAPPED_PYQ" else "Unmapped Question Pool",
            "confidence_score": top["score"],
            "score_components": {"top_score": top["score"], "runner_up_score": runner_up},
            "matched_terms": top["matched"],
            "is_ambiguous": is_ambiguous,
            "rationale": f"Matched: {', '.join(top['matched'][:4])} (score {top['score']})"
        }
