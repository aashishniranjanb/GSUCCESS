"""
BASELINE Database Migration v1 — Additive schema for GPAT 2027 knowledge baseline.
Creates baseline_* tables alongside existing tables. Never drops or alters existing tables.
Idempotent: safe to run multiple times.
"""
import sqlite3
import sys
import os
from datetime import datetime, timezone

DB_PATH = os.environ.get("GPAT_DB_PATH", "gpat_knowledge.db")

MIGRATION_SQL = """
-- Baseline sources: immutable PDF provenance
CREATE TABLE IF NOT EXISTS baseline_sources (
    source_id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    original_path TEXT,
    sha256 TEXT NOT NULL,
    size_bytes INTEGER NOT NULL,
    title TEXT,
    authority_category TEXT NOT NULL CHECK (authority_category IN (
        'OFFICIAL_SYLLABUS', 'STANDARD_TEXTBOOK', 'THIRD_PARTY_GUIDE',
        'COACHING_MATERIAL', 'QUESTION_PAPER', 'ANSWER_KEY', 'USER_MATERIAL'
    )),
    conversion_status TEXT DEFAULT 'PENDING' CHECK (conversion_status IN (
        'PENDING', 'SUCCESS', 'PARTIAL', 'FAILED'
    )),
    conversion_tool TEXT,
    conversion_version TEXT,
    markdown_output_path TEXT,
    page_count_estimate INTEGER,
    warnings_json TEXT DEFAULT '[]',
    created_at TEXT NOT NULL,
    UNIQUE(sha256)
);

-- Baseline builds: versioned pipeline runs
CREATE TABLE IF NOT EXISTS baseline_builds (
    build_id TEXT PRIMARY KEY,
    version TEXT NOT NULL,
    build_timestamp TEXT NOT NULL,
    source_count INTEGER NOT NULL DEFAULT 0,
    subject_count INTEGER NOT NULL DEFAULT 0,
    topic_count INTEGER NOT NULL DEFAULT 0,
    chunk_count INTEGER NOT NULL DEFAULT 0,
    graph_node_count INTEGER NOT NULL DEFAULT 0,
    graph_edge_count INTEGER NOT NULL DEFAULT 0,
    embedding_model TEXT,
    embedding_dimensions INTEGER,
    parameters_json TEXT DEFAULT '{}',
    status TEXT DEFAULT 'RUNNING' CHECK (status IN ('RUNNING', 'COMPLETED', 'FAILED')),
    completed_at TEXT
);

-- Baseline subjects
CREATE TABLE IF NOT EXISTS baseline_subjects (
    subject_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    original_label TEXT,
    source_ids_json TEXT NOT NULL DEFAULT '[]',
    source_pages_json TEXT NOT NULL DEFAULT '[]',
    status TEXT DEFAULT 'ACTIVE',
    created_at TEXT NOT NULL,
    build_id TEXT,
    FOREIGN KEY (build_id) REFERENCES baseline_builds(build_id)
);

-- Baseline topics: granular syllabus entries
CREATE TABLE IF NOT EXISTS baseline_topics (
    topic_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    original_label TEXT,
    subject_id TEXT NOT NULL,
    unit_id TEXT,
    parent_topic_id TEXT,
    source_ids_json TEXT NOT NULL DEFAULT '[]',
    source_pages_json TEXT NOT NULL DEFAULT '[]',
    existing_concept_id TEXT,
    extraction_status TEXT DEFAULT 'SOURCE_DERIVED' CHECK (extraction_status IN (
        'SOURCE_DERIVED', 'INFERRED', 'MERGED'
    )),
    verification_status TEXT DEFAULT 'UNVERIFIED' CHECK (verification_status IN (
        'UNVERIFIED', 'VERIFIED', 'DISPUTED'
    )),
    created_at TEXT NOT NULL,
    build_id TEXT,
    FOREIGN KEY (subject_id) REFERENCES baseline_subjects(subject_id),
    FOREIGN KEY (parent_topic_id) REFERENCES baseline_topics(topic_id),
    FOREIGN KEY (existing_concept_id) REFERENCES concepts(id),
    FOREIGN KEY (build_id) REFERENCES baseline_builds(build_id)
);

-- Baseline weightage evidence: separate from facts
CREATE TABLE IF NOT EXISTS baseline_weightage_evidence (
    evidence_id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    source_filename TEXT,
    page_or_section TEXT,
    subject_id TEXT,
    topic_id TEXT,
    reported_value REAL,
    reported_unit TEXT,
    total_context TEXT,
    stated_year TEXT,
    methodology TEXT,
    authority_status TEXT NOT NULL CHECK (authority_status IN (
        'OFFICIAL_VERIFIED', 'OFFICIAL_HISTORICAL', 'THIRD_PARTY_ESTIMATE',
        'HISTORICAL_PATTERN', 'MODEL_INFERRED', 'UNKNOWN'
    )),
    confidence TEXT DEFAULT 'LOW' CHECK (confidence IN ('HIGH', 'MEDIUM', 'LOW', 'UNKNOWN')),
    exact_quote TEXT,
    notes TEXT,
    created_at TEXT NOT NULL,
    build_id TEXT,
    FOREIGN KEY (source_id) REFERENCES baseline_sources(source_id),
    FOREIGN KEY (build_id) REFERENCES baseline_builds(build_id)
);

-- Baseline claims: atomic facts with evidence
CREATE TABLE IF NOT EXISTS baseline_claims (
    claim_id TEXT PRIMARY KEY,
    statement TEXT NOT NULL,
    claim_type TEXT,
    topic_id TEXT,
    source_id TEXT NOT NULL,
    source_block_id TEXT,
    page_number INTEGER,
    supporting_quote TEXT,
    verification_status TEXT DEFAULT 'EXTRACTED' CHECK (verification_status IN (
        'EXTRACTED', 'REVIEW_REQUIRED', 'VERIFIED', 'PUBLISHED', 'REJECTED', 'OUTDATED'
    )),
    created_at TEXT NOT NULL,
    build_id TEXT,
    FOREIGN KEY (topic_id) REFERENCES baseline_topics(topic_id),
    FOREIGN KEY (source_id) REFERENCES baseline_sources(source_id),
    FOREIGN KEY (build_id) REFERENCES baseline_builds(build_id)
);

-- Baseline chunks: retrieval-indexed text segments
CREATE TABLE IF NOT EXISTS baseline_chunks (
    chunk_id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    source_hash TEXT NOT NULL,
    page_or_range TEXT,
    heading_path TEXT,
    content TEXT NOT NULL,
    content_type TEXT DEFAULT 'paragraph',
    subject_id TEXT,
    topic_ids_json TEXT DEFAULT '[]',
    verification_status TEXT DEFAULT 'AUTO_EXTRACTED',
    embedding_model TEXT,
    embedding_version TEXT,
    created_at TEXT NOT NULL,
    build_id TEXT,
    FOREIGN KEY (source_id) REFERENCES baseline_sources(source_id),
    FOREIGN KEY (build_id) REFERENCES baseline_builds(build_id)
);

-- Baseline graph edges: relationships with provenance
CREATE TABLE IF NOT EXISTS baseline_graph_edges (
    edge_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_node TEXT NOT NULL,
    target_node TEXT NOT NULL,
    relationship TEXT NOT NULL CHECK (relationship IN (
        'CONTAINS', 'HAS_TOPIC', 'HAS_UNIT', 'MAPS_TO',
        'SUPPORTED_BY', 'DERIVED_FROM', 'HAS_CHUNK',
        'PREREQUISITE_OF', 'RELATED_TO'
    )),
    provenance TEXT DEFAULT 'SOURCE_DERIVED' CHECK (provenance IN (
        'SOURCE_DERIVED', 'EVIDENCE_SUPPORTED', 'INFERRED'
    )),
    evidence TEXT,
    source_id TEXT,
    created_at TEXT NOT NULL,
    build_id TEXT,
    FOREIGN KEY (build_id) REFERENCES baseline_builds(build_id),
    UNIQUE(source_node, target_node, relationship)
);

-- Index for fast topic lookups
CREATE INDEX IF NOT EXISTS idx_baseline_topics_subject ON baseline_topics(subject_id);
CREATE INDEX IF NOT EXISTS idx_baseline_topics_unit ON baseline_topics(unit_id);
CREATE INDEX IF NOT EXISTS idx_baseline_chunks_source ON baseline_chunks(source_id);
CREATE INDEX IF NOT EXISTS idx_baseline_chunks_topic ON baseline_chunks(topic_ids_json);
CREATE INDEX IF NOT EXISTS idx_baseline_weightage_source ON baseline_weightage_evidence(source_id);
CREATE INDEX IF NOT EXISTS idx_baseline_graph_edges_source ON baseline_graph_edges(source_node);
CREATE INDEX IF NOT EXISTS idx_baseline_graph_edges_target ON baseline_graph_edges(target_node);
"""


def run_migration(db_path: str, dry_run: bool = False):
    """Run the baseline migration. If dry_run=True, prints SQL without executing."""
    if dry_run:
        print("=== DRY RUN — SQL that would be executed ===")
        print(MIGRATION_SQL)
        return

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")

    # Verify integrity first
    cur = conn.cursor()
    cur.execute("PRAGMA integrity_check")
    integrity = cur.fetchone()[0]
    if integrity != "ok":
        print(f"ERROR: Database integrity check failed: {integrity}")
        conn.close()
        sys.exit(1)

    # Snapshot learner data counts for post-migration verification
    learner_tables = [
        "student_attempts", "fsrs_cards", "learning_events",
        "study_sessions", "study_session_items", "synced_client_events",
        "student_misconceptions"
    ]
    pre_counts = {}
    for t in learner_tables:
        try:
            cur.execute(f"SELECT count(*) FROM [{t}]")
            pre_counts[t] = cur.fetchone()[0]
        except Exception:
            pre_counts[t] = -1

    # Run migration
    conn.executescript(MIGRATION_SQL)
    conn.commit()

    # Verify learner data unchanged
    post_counts = {}
    for t in learner_tables:
        try:
            cur.execute(f"SELECT count(*) FROM [{t}]")
            post_counts[t] = cur.fetchone()[0]
        except Exception:
            post_counts[t] = -1

    # Final integrity check
    cur.execute("PRAGMA integrity_check")
    post_integrity = cur.fetchone()[0]

    # List new tables created
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'baseline_%' ORDER BY name")
    baseline_tables = [r[0] for r in cur.fetchall()]

    conn.close()

    print(f"Migration completed on: {db_path}")
    print(f"Post-migration integrity: {post_integrity}")
    print(f"Baseline tables: {baseline_tables}")
    print(f"\nLearner data verification (pre -> post):")
    all_ok = True
    for t in learner_tables:
        status = "OK" if pre_counts[t] == post_counts[t] else "CHANGED!"
        if status != "OK":
            all_ok = False
        print(f"  {t}: {pre_counts[t]} -> {post_counts[t]}  [{status}]")

    if not all_ok:
        print("\nWARNING: Learner data counts changed during migration!")
        sys.exit(1)
    else:
        print("\nAll learner data preserved. Migration successful.")


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    db = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else DB_PATH
    run_migration(db, dry_run=dry_run)
