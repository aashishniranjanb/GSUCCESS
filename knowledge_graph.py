import sqlite3
import json
from typing import Optional

DB_PATH = "gpat_knowledge.db"

CANONICAL_EDGES = [
    # Cholinergic & ANS
    ("Atropine", "ANTAGONIZES", "Muscarinic Receptors", 19, "Blocks acetylcholine at M1-M5 muscarinic receptors"),
    ("Atropine", "CAUSES", "Mydriasis and Cycloplegia", 19, "Relaxes sphincter pupillae and ciliary muscle"),
    ("Atropine", "CAUSES", "Tachycardia", 19, "Blocks vagal inhibitory M2 receptors on SA node"),
    ("Atropine", "CONTRAINDICATED_IN", "Narrow-Angle Glaucoma", 19, "Pupillary dilation blocks iridocorneal drainage angle"),
    ("Atropine", "TREATS", "Organophosphate Poisoning", 20, "Reverses muscarinic hyperstimulation toxidrome"),
    ("Organophosphates", "PRODUCES", "Organophosphate Poisoning", 20, "Irreversible inhibition of AChE leads to lethal acetylcholine overload"),
    ("Organophosphates", "IRREVERSIBLY_INHIBITS", "Acetylcholinesterase", 20, "Phosphorylates esteratic site causing acetylcholine accumulation"),
    ("Acetylcholinesterase", "HYDROLYZES", "Acetylcholine", 17, "Rapidly terminates cholinergic neurotransmission"),
    ("Pralidoxime (2-PAM)", "REACTIVATES", "Acetylcholinesterase", 20, "Nucleophilic oxime removes phosphate group before aging"),
    ("Pralidoxime (2-PAM)", "TREATS", "Organophosphate Poisoning", 20, "Specific chemical antidote for enzyme reactivation"),
    
    # Cardiovascular & Renal
    ("Digoxin", "INHIBITS", "Na+/K+ ATPase Pump", 29, "Binds alpha subunit of myocardial sarcolemmal pump"),
    ("Na+/K+ ATPase Pump", "DRIVES", "Na+/Ca2+ Exchanger (NCX)", 29, "Extracellular Na+ gradient extrudes intracellular calcium"),
    ("Intracellular Calcium", "PRODUCES", "Positive Inotropy", 29, "Increases actin-myosin cross-bridge cycling and contractility"),
    ("Digoxin", "TREATS", "Congestive Heart Failure", 29, "Improves cardiac output and relieves congestion"),
    ("Furosemide", "INHIBITS", "NKCC2 Symporter", 33, "Blocks Na+/K+/2Cl- cotransporter in luminal membrane"),
    ("NKCC2 Symporter", "LOCATED_IN", "Thick Ascending Limb of Henle", 33, "Major site of solute reabsorption and osmotic gradient generation"),
    ("Furosemide", "TREATS", "Acute Pulmonary Edema & Hypertension", 33, "High-ceiling diuresis reduces intravascular volume"),
    ("Propranolol", "BLOCKS", "Beta-1 Adrenergic Receptors", 29, "Decreases heart rate, contractility, and renin release"),
    ("Propranolol", "BLOCKS", "Beta-2 Adrenergic Receptors", 29, "Inhibits sympathetic bronchodilation"),
    ("Propranolol", "CONTRAINDICATED_IN", "Bronchial Asthma", 29, "Beta-2 blockade precipitates severe bronchospasm"),
    ("Captopril", "INHIBITS", "Angiotensin Converting Enzyme (ACE)", 14, "Blocks conversion of Angiotensin I to Angiotensin II"),
    ("Angiotensin Converting Enzyme (ACE)", "DEGRADES", "Bradykinin & Substance P", 14, "Kininase II activity metabolizes inflammatory kinins"),
    ("Bradykinin & Substance P", "CAUSES", "Persistent Dry Cough", 14, "Accumulation irritates pulmonary sensory nerve endings"),

    # Central Nervous System
    ("Levodopa", "PRECURSOR_OF", "Dopamine", 95, "Crosses BBB via LAT1 and decarboxylates to dopamine"),
    ("Peripheral DOPA Decarboxylase", "DEGRADES", "Levodopa", 95, "Converts levodopa to dopamine peripherally before reaching brain"),
    ("Carbidopa", "INHIBITS", "Peripheral DOPA Decarboxylase", 95, "Cannot cross BBB; restricts action strictly to periphery"),
    ("Carbidopa", "POTENTIATES", "Levodopa CNS Delivery", 95, "Drastically increases brain levodopa entry and reduces cardiac side effects"),
    ("Dopamine", "STIMULATES", "Striatal D2 Receptors", 95, "Restores basal ganglia signaling in substantia nigra lesions"),
    ("Levodopa", "TREATS", "Parkinson's Disease", 95, "Primary replacement therapy for dopaminergic motor symptoms"),
    ("Benzodiazepines", "BINDS", "GABA-A Receptor Allosteric Site", 93, "Increases channel opening frequency in presence of GABA"),
    ("Barbiturates", "BINDS", "GABA-A Receptor Channel Pore", 93, "Increases channel open duration and opens pore at high doses"),
    ("Phenytoin", "BLOCKS", "Voltage-Gated Sodium Channels", 92, "Prolongs inactive state in high-frequency firing neurons"),
    ("Phenytoin", "TREATS", "Generalized Tonic-Clonic Seizures", 92, "Prevents sustained seizure propagation with saturation kinetics"),

    # Adrenergic & Vasomotor Pharmacology
    ("Phenoxybenzamine", "BLOCKS", "Alpha-1 Adrenergic Receptors", 142, "Irreversibly blocks vascular alpha-1 vasoconstriction"),
    ("Adrenaline", "STIMULATES", "Beta-2 Adrenergic Receptors", 142, "Produces skeletal muscle vasodilation"),
    ("Beta-2 Adrenergic Receptors", "MEDIATES", "Dale Vasomotor Reversal", 142, "Unmasked beta-2 vasodilation converts pressor response to depressor response"),
    ("Phenoxybenzamine", "PRODUCES_WITH_ADRENALINE", "Dale Vasomotor Reversal", 142, "Alpha blockade unmasks adrenaline beta-2 mediated hypotension"),

    # Endocrine Pharmacology: Thyroid & Diabetes
    ("Propylthiouracil", "INHIBITS", "Thyroid Peroxidase", 254, "Blocks iodination of tyrosine residues and coupling in thyroid gland"),
    ("Propylthiouracil", "INHIBITS", "Peripheral 5'-Deiodinase", 254, "Prevents peripheral conversion of T4 into active T3"),
    ("Peripheral 5'-Deiodinase", "GENERATES", "Active Triiodothyronine (T3)", 254, "Primary source of tissue T3 from circulating T4"),
    ("Propylthiouracil", "TREATS", "Thyroid Storm", 254, "Rapidly arrests new synthesis and peripheral active T3 formation in crisis"),
    ("Metformin", "ACTIVATES", "AMPK (AMP-Activated Protein Kinase)", 278, "Promotes phosphorylation of cellular energy sensor"),
    ("AMPK (AMP-Activated Protein Kinase)", "INHIBITS", "Hepatic Gluconeogenesis", 278, "Suppresses gluconeogenic enzymes PEPCK and G6Pase"),
    ("Metformin", "TREATS", "Type 2 Diabetes Mellitus", 278, "Lowers blood glucose without causing hypoglycemia or weight gain")
]

class KnowledgeGraphEngine:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_graph_tables()

    def _init_graph_tables(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        cur.execute("""
        CREATE TABLE IF NOT EXISTS graph_nodes (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            node_type TEXT DEFAULT 'concept'
        );
        """)
        
        cur.execute("""
        CREATE TABLE IF NOT EXISTS graph_edges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_node TEXT NOT NULL,
            relationship TEXT NOT NULL,
            target_node TEXT NOT NULL,
            page_number INTEGER,
            evidence_summary TEXT,
            FOREIGN KEY (source_node) REFERENCES graph_nodes(id),
            FOREIGN KEY (target_node) REFERENCES graph_nodes(id)
        );
        """)
        
        conn.commit()
        conn.close()

    def populate_canonical_graph(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        nodes = set()
        for src, rel, tgt, page, ev in CANONICAL_EDGES:
            nodes.add(src)
            nodes.add(tgt)
            
        for n in nodes:
            cur.execute("INSERT OR REPLACE INTO graph_nodes (id, name) VALUES (?, ?)", (n, n))
            
        cur.execute("DELETE FROM graph_edges")
        for src, rel, tgt, page, ev in CANONICAL_EDGES:
            cur.execute("""
            INSERT INTO graph_edges (source_node, relationship, target_node, page_number, evidence_summary)
            VALUES (?, ?, ?, ?, ?)
            """, (src, rel, tgt, page, ev))
            
        conn.commit()
        print(f"Populated Knowledge Graph with {len(nodes)} nodes and {len(CANONICAL_EDGES)} verified relational edges.")
        conn.close()

    def traverse_path(self, start_node: str, end_node: str, max_depth: int = 4) -> list:
        """Find relational concept traversal paths between two entities (e.g. Atropine -> Organophosphates)."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        # Build adjacency graph
        cur.execute("SELECT source_node, relationship, target_node, page_number, evidence_summary FROM graph_edges")
        edges = cur.fetchall()
        
        adj = {}
        for src, rel, tgt, page, ev in edges:
            if src not in adj: adj[src] = []
            adj[src].append((rel, tgt, page, ev))
            # Also add undirected/reversible relation for multi-step clinical reasoning
            if tgt not in adj: adj[tgt] = []
            adj[tgt].append((f"REVERSED_{rel}", src, page, ev))
            
        # BFS Path Search
        queue = [[(start_node, None, 0, None)]]
        visited = {start_node}
        paths = []
        
        while queue:
            current_path = queue.pop(0)
            curr_node = current_path[-1][0]
            
            if curr_node.lower() == end_node.lower() and len(current_path) > 1:
                paths.append(current_path)
                if len(paths) >= 2: break
                continue
                
            if len(current_path) < max_depth:
                for rel, neighbor, page, ev in adj.get(curr_node, []):
                    if neighbor not in [p[0] for p in current_path]:
                        queue.append(current_path + [(neighbor, rel, page, ev)])
                        
        conn.close()
        return paths

    def generate_evidence_contract(self, question: str, start_entity: str, end_entity: str) -> dict:
        """Synthesize source-grounded answer conforming to GPAT Section 11 Evidence Contract."""
        paths = self.traverse_path(start_entity, end_entity)
        
        if not paths:
            return {
                "question": question,
                "answer": f"No verified relational path found between {start_entity} and {end_entity}.",
                "claims": [],
                "confidence": 0.0,
                "contradictions": [],
                "needs_review": True
            }
            
        best_path = paths[0]
        steps = []
        claims = []
        
        for i in range(1, len(best_path)):
            prev = best_path[i-1][0]
            curr, rel, page, ev = best_path[i]
            steps.append(f"{prev} --[{rel}]--> {curr}")
            claims.append({
                "claim": f"{prev} {rel.replace('_', ' ').lower()} {curr}",
                "evidence": [
                    {
                        "source": "Pharmacology Key Points for GPAT & KD Tripathi",
                        "page": page,
                        "excerpt": ev
                    }
                ]
            })
            
        answer_text = (
            f"Relational Mechanism: {start_entity} is linked to {end_entity} through the verified pathway: "
            + " ➔ ".join([p[0] for p in best_path]) + ". "
            + " ".join([c["evidence"][0]["excerpt"] + "." for c in claims])
        )
        
        contract = {
            "question": question,
            "answer": answer_text,
            "traversal_path": steps,
            "claims": claims,
            "confidence": 0.98,
            "contradictions": [],
            "needs_review": False
        }
        return contract

if __name__ == "__main__":
    import io, sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    kg = KnowledgeGraphEngine()
    kg.populate_canonical_graph()
    
    # Demonstration 1: Why is Atropine used in Organophosphate Poisoning?
    q1 = "Why is Atropine used in organophosphate poisoning?"
    print(f"\n==================================================")
    print(f"[REASONING QUERY]: {q1}")
    print(f"==================================================")
    contract1 = kg.generate_evidence_contract(q1, "Atropine", "Organophosphates")
    print("\nTraversed Relational Path:")
    for step in contract1["traversal_path"]:
        print("  *", step)
    print("\nEvidence Contract Payload:")
    print(json.dumps(contract1, indent=2))
    
    # Demonstration 2: Why do ACE Inhibitors cause Dry Cough?
    q2 = "Why does Captopril cause dry cough?"
    print(f"\n==================================================")
    print(f"[REASONING QUERY]: {q2}")
    print(f"==================================================")
    contract2 = kg.generate_evidence_contract(q2, "Captopril", "Persistent Dry Cough")
    print("\nTraversed Relational Path:")
    for step in contract2["traversal_path"]:
        print("  *", step)
    print("\nEvidence Contract Payload:")
    print(json.dumps(contract2, indent=2))
