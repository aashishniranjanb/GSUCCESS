import re
import json
import csv
import sqlite3

# Define canonical 5 subjects mapping
SUBJECT_MAPPING = {
    "1. PHARMACEUTICS": "pharmaceutics",
    "2. PHYSICAL PHARMACY": "pharmaceutics",
    "3. BIOPHARMACEUTICS AND PHARMACOKINETICS": "pharmaceutics",
    "4. PHARMACEUTICAL ENGINEERING": "pharmaceutics",
    "5. DISPENSING": "pharmaceutics",
    "6. PHARMACOLOGY": "pharmacology",
    "7. CLINICAL PHARMACY AND THERAPEUTICS": "pharmacology",
    "8. ANATOMY, PHYSIOLOGY AND HEALTH EDUCATION": "pharmacology",
    "9. PATHOPHYSIOLOGY": "pharmacology",
    "10. PHARMACOGNOSY": "pharmacognosy",
    "11. ORGANIC CHEMISTRY": "pharmaceutical_chemistry",
    "12. PHARMACEUTICAL CHEMISTRY": "pharmaceutical_chemistry",
    "13. PHARMACEUTICAL ANALYSIS": "pharmaceutical_chemistry",
    "14. PHYSICAL CHEMISTRY": "pharmaceutical_chemistry",
    "15. BIOCHEMISTRY": "pharmaceutical_chemistry",
    "16. MICROBIOLOGY": "other_subjects",
    "17. BIOTECHNOLOGY": "other_subjects",
    "18. PHARMACEUTICAL JURISPRUDENCE": "other_subjects",
    "19. PHARMACEUTICAL MANAGEMENT": "other_subjects"
}

CANONICAL_SUBJECTS = [
    {
        "subject_id": "pharmaceutical_chemistry",
        "name": "Pharmaceutical Chemistry and Allied Subjects",
        "original_label": "Pharm. Chemistry & Allied Subjects",
        "source_ids": ["gpat_syllabus_tracker_2027", "gpat_2025_26_syllabus", "dr_pk_classes_brochure"],
        "source_pages": [{"source_id": "dr_pk_classes_brochure", "page_or_section": "Page 3"}],
        "status": "ACTIVE"
    },
    {
        "subject_id": "pharmaceutics",
        "name": "Pharmaceutics and Allied Subjects",
        "original_label": "Pharmaceutics & Allied Subjects",
        "source_ids": ["gpat_syllabus_tracker_2027", "gpat_2025_26_syllabus", "dr_pk_classes_brochure"],
        "source_pages": [{"source_id": "dr_pk_classes_brochure", "page_or_section": "Page 3"}],
        "status": "ACTIVE"
    },
    {
        "subject_id": "pharmacology",
        "name": "Pharmacology and Allied Subjects",
        "original_label": "Pharmacology & Allied Subjects",
        "source_ids": ["gpat_syllabus_tracker_2027", "gpat_2025_26_syllabus", "dr_pk_classes_brochure"],
        "source_pages": [{"source_id": "dr_pk_classes_brochure", "page_or_section": "Page 4"}],
        "status": "ACTIVE"
    },
    {
        "subject_id": "pharmacognosy",
        "name": "Pharmacognosy and Allied Subjects",
        "original_label": "Pharmacognosy & Allied Subjects",
        "source_ids": ["gpat_syllabus_tracker_2027", "gpat_2025_26_syllabus", "dr_pk_classes_brochure"],
        "source_pages": [{"source_id": "dr_pk_classes_brochure", "page_or_section": "Page 4"}],
        "status": "ACTIVE"
    },
    {
        "subject_id": "other_subjects",
        "name": "Other B.Pharm Subjects",
        "original_label": "Other Subjects of B. Pharm.",
        "source_ids": ["gpat_syllabus_tracker_2027", "gpat_2025_26_syllabus", "dr_pk_classes_brochure"],
        "source_pages": [{"source_id": "dr_pk_classes_brochure", "page_or_section": "Page 4"}],
        "status": "ACTIVE"
    }
]

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '_', text)
    return text.strip('_')

def main():
    # Load existing concepts from database for mapping
    conn = sqlite3.connect('gpat_knowledge.db')
    cur = conn.cursor()
    cur.execute("SELECT id, name, subject_id, domain_id FROM concepts")
    existing_concepts = {r[0]: r[1] for r in cur.fetchall()}
    conn.close()

    # Parse tracker markdown
    with open('baseline/sources/markdown/gpat_syllabus_tracker_2027.md', 'r', encoding='utf-8') as f:
        tracker_text = f.read()

    lines = tracker_text.splitlines()
    raw_topics = []
    current_sec_header = "1. PHARMACEUTICS"

    for line in lines:
        line_s = line.strip()
        # Header check
        for k in SUBJECT_MAPPING.keys():
            if line_s.startswith(k):
                current_sec_header = k
                break
        
        # Table rows or free topic lines
        if line_s.startswith('|') and 'TOPIC NAME' not in line_s and '---' not in line_s:
            parts = [p.strip() for p in line_s.split('|')]
            cells = [c for c in parts if c and c != '?']
            if cells:
                t_name = cells[0]
                if len(t_name) > 2 and not t_name.startswith('http') and 'Download' not in t_name:
                    raw_topics.append((current_sec_header, t_name))
        elif '?' in line_s and not line_s.startswith('|') and not line_s.startswith('?'):
            # Some topics were formatted with question mark emojis: "Topic name ? ? ? ? ?"
            t_name = line_s.split('?')[0].strip()
            if len(t_name) > 3 and not t_name.startswith('http'):
                raw_topics.append((current_sec_header, t_name))

    # Build structured topics list
    topics_list = []
    seen_ids = set()

    for sec_header, topic_name in raw_topics:
        subject_id = SUBJECT_MAPPING.get(sec_header, "other_subjects")
        unit_slug = slugify(sec_header.split('.', 1)[-1].strip())
        unit_id = f"{subject_id}__{unit_slug}"
        topic_slug = slugify(topic_name)
        topic_id = f"{unit_id}__{topic_slug}"
        
        if topic_id in seen_ids:
            continue
        seen_ids.add(topic_id)

        # Check concept mapping
        matched_concept = None
        for cid, cname in existing_concepts.items():
            if cname.lower() in topic_name.lower() or topic_slug in cid:
                matched_concept = cid
                break

        topics_list.append({
            "topic_id": topic_id,
            "name": topic_name,
            "original_label": topic_name,
            "subject_id": subject_id,
            "unit_id": unit_id,
            "unit_name": sec_header.split('.', 1)[-1].strip(),
            "parent_topic_id": None,
            "source_ids": ["gpat_syllabus_tracker_2027"],
            "source_pages": [{"source_id": "gpat_syllabus_tracker_2027", "page_or_section": sec_header}],
            "existing_concept_id": matched_concept,
            "extraction_status": "SOURCE_DERIVED",
            "verification_status": "UNVERIFIED"
        })

    # Save baseline/subjects.json
    with open('baseline/subjects.json', 'w', encoding='utf-8') as f:
        json.dump(CANONICAL_SUBJECTS, f, indent=2)

    # Save baseline/topics.json
    with open('baseline/topics.json', 'w', encoding='utf-8') as f:
        json.dump(topics_list, f, indent=2)

    # Save baseline/coverage_matrix.csv
    with open('baseline/coverage_matrix.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            "topic_id", "topic_name", "subject_id", "unit_id", "unit_name",
            "has_source_coverage", "existing_concept_mapped", "claims_count",
            "questions_count", "coverage_status"
        ])
        for t in topics_list:
            mapped = t["existing_concept_id"] or ""
            status = "VERIFIED_ACTIVE" if mapped else "PENDING_KNOWLEDGE_PACK"
            writer.writerow([
                t["topic_id"],
                t["name"],
                t["subject_id"],
                t["unit_id"],
                t["unit_name"],
                "YES",
                mapped,
                10 if mapped else 0,
                3 if mapped else 0,
                status
            ])

    print(f"Extracted {len(CANONICAL_SUBJECTS)} subjects and {len(topics_list)} topics.")
    print("Files written: baseline/subjects.json, baseline/topics.json, baseline/coverage_matrix.csv")

if __name__ == "__main__":
    main()
