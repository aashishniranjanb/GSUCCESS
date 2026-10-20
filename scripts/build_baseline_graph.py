import json
from datetime import datetime, timezone

def main():
    with open('baseline/source_manifest.json', 'r', encoding='utf-8') as f:
        sources = json.load(f)

    with open('baseline/subjects.json', 'r', encoding='utf-8') as f:
        subjects = json.load(f)

    with open('baseline/topics.json', 'r', encoding='utf-8') as f:
        topics = json.load(f)

    nodes = []
    edges = []
    node_ids = set()

    # 1. Source Nodes
    for s in sources:
        nid = f"source__{s['source_id']}"
        nodes.append({
            "id": nid,
            "type": "Source",
            "name": s["title"],
            "metadata": {
                "filename": s["filename"],
                "authority_category": s["authority_category"],
                "sha256": s["sha256"]
            }
        })
        node_ids.add(nid)

    # 2. Subject Nodes
    for subj in subjects:
        nid = f"subject__{subj['subject_id']}"
        nodes.append({
            "id": nid,
            "type": "Subject",
            "name": subj["name"],
            "metadata": {
                "original_label": subj["original_label"],
                "status": subj["status"]
            }
        })
        node_ids.add(nid)

        # Edges from sources to subjects
        for sid in subj["source_ids"]:
            source_nid = f"source__{sid}"
            if source_nid in node_ids:
                edges.append({
                    "source": source_nid,
                    "target": nid,
                    "relationship": "CONTAINS",
                    "provenance": "SOURCE_DERIVED",
                    "evidence": "Syllabus mapping"
                })

    # 3. Unit Nodes & Topic Nodes
    unit_nodes = set()
    for t in topics:
        unit_nid = f"unit__{t['unit_id']}"
        if unit_nid not in unit_nodes:
            nodes.append({
                "id": unit_nid,
                "type": "Unit",
                "name": t.get("unit_name", t["unit_id"]),
                "metadata": {
                    "subject_id": t["subject_id"]
                }
            })
            node_ids.add(unit_nid)
            unit_nodes.add(unit_nid)

            # Edge from Subject to Unit
            subj_nid = f"subject__{t['subject_id']}"
            if subj_nid in node_ids:
                edges.append({
                    "source": subj_nid,
                    "target": unit_nid,
                    "relationship": "HAS_UNIT",
                    "provenance": "SOURCE_DERIVED",
                    "evidence": "Tracker subject section"
                })

        # Topic Node
        topic_nid = f"topic__{t['topic_id']}"
        nodes.append({
            "id": topic_nid,
            "type": "Topic",
            "name": t["name"],
            "metadata": {
                "unit_id": t["unit_id"],
                "subject_id": t["subject_id"],
                "extraction_status": t["extraction_status"],
                "existing_concept_id": t.get("existing_concept_id")
            }
        })
        node_ids.add(topic_nid)

        # Edge from Unit to Topic
        edges.append({
            "source": unit_nid,
            "target": topic_nid,
            "relationship": "HAS_TOPIC",
            "provenance": "SOURCE_DERIVED",
            "evidence": "Tracker topic row"
        })

        # Map to concept node if exists
        if t.get("existing_concept_id"):
            concept_nid = f"concept__{t['existing_concept_id']}"
            if concept_nid not in node_ids:
                nodes.append({
                    "id": concept_nid,
                    "type": "Concept",
                    "name": t["name"],
                    "metadata": {"database_concept_id": t["existing_concept_id"]}
                })
                node_ids.add(concept_nid)
            edges.append({
                "source": topic_nid,
                "target": concept_nid,
                "relationship": "MAPS_TO",
                "provenance": "EVIDENCE_SUPPORTED",
                "evidence": "Ontology string/token matching"
            })

    # Validate that every edge endpoint exists
    invalid_edges = []
    for e in edges:
        if e["source"] not in node_ids or e["target"] not in node_ids:
            invalid_edges.append(e)

    if invalid_edges:
        print(f"ERROR: Found {len(invalid_edges)} invalid edges with missing endpoints!")
        return

    graph_payload = {
        "version": "1.0.0",
        "build_timestamp": datetime.now(timezone.utc).isoformat(),
        "total_nodes": len(nodes),
        "total_edges": len(edges),
        "node_types": {
            "Source": len([n for n in nodes if n["type"] == "Source"]),
            "Subject": len([n for n in nodes if n["type"] == "Subject"]),
            "Unit": len([n for n in nodes if n["type"] == "Unit"]),
            "Topic": len([n for n in nodes if n["type"] == "Topic"]),
            "Concept": len([n for n in nodes if n["type"] == "Concept"])
        },
        "edge_relationships": {
            "CONTAINS": len([e for e in edges if e["relationship"] == "CONTAINS"]),
            "HAS_UNIT": len([e for e in edges if e["relationship"] == "HAS_UNIT"]),
            "HAS_TOPIC": len([e for e in edges if e["relationship"] == "HAS_TOPIC"]),
            "MAPS_TO": len([e for e in edges if e["relationship"] == "MAPS_TO"])
        },
        "nodes": nodes,
        "edges": edges
    }

    with open('baseline/baseline_graph.json', 'w', encoding='utf-8') as f:
        json.dump(graph_payload, f, indent=2)

    print(f"Successfully constructed baseline graph:")
    print(f"  Nodes: {len(nodes)} (Sources: {graph_payload['node_types']['Source']}, Subjects: {graph_payload['node_types']['Subject']}, Units: {graph_payload['node_types']['Unit']}, Topics: {graph_payload['node_types']['Topic']}, Concepts: {graph_payload['node_types']['Concept']})")
    print(f"  Edges: {len(edges)} (100% valid endpoints verified)")
    print(f"  Saved to baseline/baseline_graph.json")

if __name__ == "__main__":
    main()
