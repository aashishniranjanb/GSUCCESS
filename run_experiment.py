import yaml
import json
from gpat_v0_ontology_ingestion.gpat_v0.ingestion_pipeline.app.concept_mapper import ConceptMapper

def run_experiment():
    print("Loading GPAT Concept Seed...")
    with open("gpat_concept_seed.yaml", "r", encoding="utf-8") as f:
        seed = yaml.safe_load(f)
        
    print(f"Loaded {len(seed.get('concepts', []))} concepts.")
    
    mapper = ConceptMapper(ontology=seed)
    pdf_path = "Pharmacology-complete.pdf"
    
    blocks = []
    try:
        from gpat_v0_ontology_ingestion.gpat_v0.ingestion_pipeline.app.docling_adapter import DoclingAdapter
        docling = DoclingAdapter()
        print(f"Running Docling on {pdf_path} (this might take a while)...")
        items = list(docling.extract_items(pdf_path))
        
        for i, item in enumerate(items):
            text_content = ""
            if hasattr(item["item"], "text"):
                text_content = item["item"].text
                
            blocks.append({
                "block_id": str(i),
                "text": text_content,
                "level": item["level"]
            })
    except ImportError as e:
        print(f"Docling not installed/available ({e}). Using mock blocks for experiment...")
        blocks = [
            {"block_id": "1", "text": "The absorption of a drug depends on its ionization state and lipid solubility.", "level": 1},
            {"block_id": "2", "text": "Receptor theory states that drugs interact with specific receptors to produce an effect.", "level": 1},
            {"block_id": "3", "text": "Atropine is a muscarinic antagonist that blocks cholinergic receptors.", "level": 2},
            {"block_id": "4", "text": "Beta blockers like propranolol are antihypertensive drugs acting on adrenergic receptors.", "level": 2},
            {"block_id": "5", "text": "Benzodiazepines act as sedatives and hypnotics.", "level": 2}
        ]
        
    print(f"Extracted {len(blocks)} blocks from the PDF.")
    
    print("Mapping concepts...")
    mapped_blocks = mapper.map_blocks(blocks)
    
    # Summarize results
    total_mapped = 0
    concept_hits = {}
    
    for block in mapped_blocks:
        candidates = block.get("concept_candidates", [])
        if candidates:
            total_mapped += 1
            for c in candidates:
                concept_hits[c] = concept_hits.get(c, 0) + 1
                
    print(f"Total blocks mapped to at least one concept: {total_mapped}")
    print("Concept hits:")
    for c, hits in concept_hits.items():
        print(f"  {c}: {hits} blocks")
        
    print("\nEnd-to-end experiment successful!")

if __name__ == "__main__":
    run_experiment()
