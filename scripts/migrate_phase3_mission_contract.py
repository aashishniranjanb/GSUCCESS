import sqlite3

MIGRATIONS_SESSIONS = [
    ("planner_version", "TEXT DEFAULT 'phase3-v1'")
]

MIGRATIONS_ITEMS = [
    ("reason_codes", "TEXT DEFAULT 'HIGH_YIELD_CONCEPT'"),
    ("candidate_type", "TEXT DEFAULT 'NEW_LEARNING'"),
    ("estimated_seconds", "INTEGER DEFAULT 150")
]

def migrate_db(db_path):
    print(f"Applying Phase 3 mission contract migrations to {db_path}...")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # 1. study_sessions
    cur.execute("PRAGMA table_info(study_sessions)")
    s_cols = [c[1] for c in cur.fetchall()]
    for col, col_def in MIGRATIONS_SESSIONS:
        if col not in s_cols:
            print(f"  Adding {col} to study_sessions")
            cur.execute(f"ALTER TABLE study_sessions ADD COLUMN {col} {col_def}")

    # 2. study_session_items
    cur.execute("PRAGMA table_info(study_session_items)")
    i_cols = [c[1] for c in cur.fetchall()]
    for col, col_def in MIGRATIONS_ITEMS:
        if col not in i_cols:
            print(f"  Adding {col} to study_session_items")
            cur.execute(f"ALTER TABLE study_session_items ADD COLUMN {col} {col_def}")

    conn.commit()
    conn.close()
    print(f"Migrations on {db_path} complete.")

if __name__ == '__main__':
    migrate_db("gpat_knowledge.db")
