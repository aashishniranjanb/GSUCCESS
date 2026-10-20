import sqlite3

MIGRATIONS = [
    ("quality_status", "TEXT DEFAULT 'PUBLISHED'"),
    ("raw_text", "TEXT"),
    ("original_q_number", "INTEGER"),
    ("answer_status", "TEXT DEFAULT 'VERIFIED'"),
    ("answer_source_page", "INTEGER"),
    ("rights_status", "TEXT DEFAULT 'ACADEMIC_FAIR_USE'")
]

def migrate_db(db_path):
    print(f"Checking migrations on {db_path}...")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(baseline_questions)")
    existing_cols = [c[1] for c in cur.fetchall()]
    
    for col_name, col_type in MIGRATIONS:
        if col_name not in existing_cols:
            print(f"Adding column {col_name} ({col_type}) to {db_path}")
            cur.execute(f"ALTER TABLE baseline_questions ADD COLUMN {col_name} {col_type}")
            
    # Also create review queue table if not exists in baseline db
    cur.execute("""
    CREATE TABLE IF NOT EXISTS pyq_review_queue (
        review_id TEXT PRIMARY KEY,
        question_id TEXT,
        paper_id TEXT,
        pyq_year INTEGER,
        original_q_number INTEGER,
        source_page INTEGER,
        issue_type TEXT,
        details_json TEXT,
        raw_text TEXT,
        status TEXT DEFAULT 'PENDING_REVIEW',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()
    print(f"Migrations on {db_path} complete.")

if __name__ == '__main__':
    migrate_db("data/gpat_baseline.db")
    migrate_db("gpat_knowledge.db")
