# Universal Content & Syllabus Data Dictionary

**Date:** 2026-10-18  
**Standards:** ANSI SQL, SQLite 3.35+, PostgreSQL Compatibility Mode

---

## 1. Syllabus & Hierarchy Entities

### `syllabus_versions`
Tracks official regulatory curriculum versions and revision timelines.
```sql
CREATE TABLE syllabus_versions (
    version_id TEXT PRIMARY KEY,        -- e.g., 'pci_bpharm_2024', 'nbems_gpat_2025'
    authority_name TEXT NOT NULL,       -- 'Pharmacy Council of India' / 'NBEMS'
    title TEXT NOT NULL,
    effective_year INTEGER NOT NULL,    -- 2024, 2025, 2027
    status TEXT NOT NULL,               -- 'ACTIVE', 'SUPERSEDED', 'DRAFT'
    source_document_id TEXT,
    created_at TIMESTAMP NOT NULL
);
```

### `subjects` (Level 1: Exam Grouping)
Official scoring buckets designated by the GPAT examination conducting body.
```sql
CREATE TABLE subjects (
    subject_id TEXT PRIMARY KEY,        -- 'pharmaceutical_chemistry', 'pharmaceutics', 'pharmacology', 'pharmacognosy', 'other_subjects'
    name TEXT NOT NULL,
    nbems_question_quota INTEGER,       -- 38, 38, 28, 10, 11
    nbems_marks_quota INTEGER,          -- 152, 152, 112, 40, 44
    display_order INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'ACTIVE'
);
```

### `curriculum_subjects` (Level 2: Academic Disciplines)
Individual university courses per PCI B.Pharm regulations.
```sql
CREATE TABLE curriculum_subjects (
    curriculum_subject_id TEXT PRIMARY KEY, -- 'physical_pharmacy', 'biopharmaceutics', 'organic_chemistry'
    exam_subject_id TEXT NOT NULL REFERENCES subjects(subject_id),
    name TEXT NOT NULL,
    pci_course_code TEXT,                   -- 'BP302T', 'BP102T', 'BP405T'
    semester_recommended INTEGER,           -- 1 to 8
    description TEXT
);
```

### `units` (Level 3: Chapters / Pedagogical Units)
Distinct syllabus modules within an academic course.
```sql
CREATE TABLE units (
    unit_id TEXT PRIMARY KEY,               -- 'pharmaceutics__physical_pharmacy__unit_1_solubility'
    curriculum_subject_id TEXT NOT NULL REFERENCES curriculum_subjects(curriculum_subject_id),
    unit_number INTEGER NOT NULL,           -- 1 to 5
    title TEXT NOT NULL,
    description TEXT
);
```

### `baseline_topics` (Level 4: Core Topics)
Canonical topic registry with backward-compatible slug IDs.
```sql
CREATE TABLE baseline_topics (
    topic_id TEXT PRIMARY KEY,              -- 'pharmaceutics__physical_pharmacy__solubility'
    name TEXT NOT NULL,
    original_label TEXT,
    subject_id TEXT NOT NULL REFERENCES subjects(subject_id),
    curriculum_subject_id TEXT REFERENCES curriculum_subjects(curriculum_subject_id),
    unit_id TEXT REFERENCES units(unit_id),
    parent_topic_id TEXT REFERENCES baseline_topics(topic_id),
    source_ids_json TEXT NOT NULL,          -- JSON Array of source IDs
    source_pages_json TEXT NOT NULL,        -- JSON Array of page objects
    existing_concept_id TEXT,
    extraction_status TEXT NOT NULL,        -- 'SOURCE_DERIVED', 'EXPERT_CURATED'
    verification_status TEXT NOT NULL,      -- 'VERIFIED', 'UNVERIFIED', 'NEEDS_REVIEW'
    created_at TIMESTAMP NOT NULL,
    build_id TEXT
);
```

### `learning_objectives` (Level 5: Atomic Competencies)
Specific measurable skills required for active recall and flashcards.
```sql
CREATE TABLE learning_objectives (
    objective_id TEXT PRIMARY KEY,          -- 'lo_sol_001_temperature_effect'
    topic_id TEXT NOT NULL REFERENCES baseline_topics(topic_id),
    code TEXT NOT NULL,                     -- 'LO-SOL-01'
    bloom_level TEXT NOT NULL,              -- 'REMEMBER', 'UNDERSTAND', 'APPLY', 'ANALYZE'
    objective_statement TEXT NOT NULL,
    key_formula_or_rule TEXT,
    clinical_or_formulation_pearl TEXT,
    created_at TIMESTAMP NOT NULL
);
```

---

## 2. Content & Source Provenance Entities

### `content_sources`
Tracks original immutable PDF documents, books, and question papers.
```sql
CREATE TABLE content_sources (
    source_id TEXT PRIMARY KEY,             -- 'gpat_2025_qp_answer_key', 'kdt_pharmacology_8th'
    filename TEXT NOT NULL,
    sha256 TEXT UNIQUE NOT NULL,
    size_bytes INTEGER NOT NULL,
    title TEXT NOT NULL,
    edition TEXT,
    author_or_institution TEXT,
    source_type TEXT NOT NULL,              -- 'OFFICIAL_SYLLABUS', 'REFERENCE_BOOK', 'DPP', 'NOTES', 'QUESTION_PAPER'
    authority_level TEXT NOT NULL,          -- 'OFFICIAL', 'EDUCATIONAL_REFERENCE', 'THIRD_PARTY_ESTIMATE'
    rights_status TEXT NOT NULL,            -- 'PUBLIC_GOVERNMENT_RECORD', 'ACADEMIC_FAIR_USE', 'RESTRICTED'
    conversion_tool TEXT NOT NULL,          -- 'markitdown', 'tesseract-ocr-5.x'
    conversion_status TEXT NOT NULL,        -- 'SUCCESS', 'PARTIAL', 'FAILED'
    markdown_path TEXT,
    created_at TIMESTAMP NOT NULL
);
```

### `content_chunks`
Extracted textual and tabular passages linked to sources.
```sql
CREATE TABLE content_chunks (
    chunk_id TEXT PRIMARY KEY,              -- 'chk_gpat25_001'
    source_id TEXT NOT NULL REFERENCES content_sources(source_id),
    page_number INTEGER,
    section_heading TEXT,
    content_text TEXT NOT NULL,
    content_type TEXT NOT NULL,             -- 'TEXT', 'TABLE', 'EXPLANATION_RATIONALE'
    verification_status TEXT NOT NULL,      -- 'VERIFIED', 'UNVERIFIED', 'DISPUTED'
    embedding_blob BLOB,                    -- 384-dimensional dense float vector
    created_at TIMESTAMP NOT NULL
);
```

### `topic_content_links`
Normalized many-to-many relationship connecting syllabus topics to content assets.
```sql
CREATE TABLE topic_content_links (
    link_id TEXT PRIMARY KEY,
    topic_id TEXT NOT NULL REFERENCES baseline_topics(topic_id),
    source_id TEXT NOT NULL REFERENCES content_sources(source_id),
    chunk_id TEXT REFERENCES content_chunks(chunk_id),
    asset_type TEXT NOT NULL,               -- 'BOOK_CHAPTER', 'CLASS_NOTE', 'DPP_QUESTION', 'PYQ_EVIDENCE'
    relevance_score REAL DEFAULT 1.0,
    is_primary_reference INTEGER DEFAULT 0,
    created_at TIMESTAMP NOT NULL,
    UNIQUE(topic_id, source_id, chunk_id)
);
```

### `question_topic_links`
Traceable links between questions and one or more syllabus topics.
```sql
CREATE TABLE question_topic_links (
    link_id TEXT PRIMARY KEY,
    question_id TEXT NOT NULL,
    topic_id TEXT NOT NULL REFERENCES baseline_topics(topic_id),
    association_type TEXT NOT NULL,         -- 'PRIMARY_TOPIC', 'PREREQUISITE_TOPIC', 'SECONDARY_TOPIC'
    confidence_score REAL NOT NULL,
    reviewer_id TEXT,                       -- NULL if algorithmic, reviewer ID if verified
    review_decision TEXT NOT NULL,          -- 'APPROVED', 'PROPOSED', 'FLAGGED'
    created_at TIMESTAMP NOT NULL,
    UNIQUE(question_id, topic_id)
);
```
