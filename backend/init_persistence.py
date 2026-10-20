"""
Schema Initializer for GPAT 2027 Persistent Sessions and Learning Event Log.
Creates:
- study_sessions (one canonical session per user per calendar day)
- study_session_items (ordered questions in that day's session)
- learning_events (append-only audit log of all learning telemetry)
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "gpat_knowledge.db"

def init_persistence_schema(db_path: Path = DB_PATH):
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    
    # 1. Canonical Daily Sessions
    cur.execute("""
    CREATE TABLE IF NOT EXISTS study_sessions (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        session_date TEXT NOT NULL,
        target_minutes INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'active', -- 'active', 'completed', 'abandoned'
        started_at TEXT,
        completed_at TEXT,
        created_at TEXT NOT NULL,
        UNIQUE(user_id, session_date)
    );
    """)
    
    # 2. Ordered Session Items
    cur.execute("""
    CREATE TABLE IF NOT EXISTS study_session_items (
        id TEXT PRIMARY KEY,
        session_id TEXT NOT NULL,
        question_id TEXT NOT NULL,
        concept_id TEXT,
        sequence INTEGER NOT NULL,
        source_type TEXT NOT NULL, -- 'due_fsrs', 'weakness_repair', 'high_yield', 'new_application'
        status TEXT NOT NULL DEFAULT 'pending', -- 'pending', 'presented', 'answered', 'skipped'
        presented_at TEXT,
        answered_at TEXT,
        is_correct INTEGER,
        FOREIGN KEY(session_id) REFERENCES study_sessions(id),
        FOREIGN KEY(question_id) REFERENCES questions(id)
    );
    """)
    
    # 3. Append-Only Learning Event Stream
    cur.execute("""
    CREATE TABLE IF NOT EXISTS learning_events (
        event_id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        event_type TEXT NOT NULL, -- 'SESSION_STARTED', 'QUESTION_SHOWN', 'QUESTION_ANSWERED', 'HINT_USED', 'MISCONCEPTION_DETECTED', 'FSRS_REVIEWED', 'SESSION_COMPLETED'
        question_id TEXT,
        concept_id TEXT,
        timestamp TEXT NOT NULL,
        payload_json TEXT
    );
    """)
    
    conn.commit()
    conn.close()
    print("Persistence schema (study_sessions, study_session_items, learning_events) initialized successfully.")

if __name__ == "__main__":
    init_persistence_schema()
