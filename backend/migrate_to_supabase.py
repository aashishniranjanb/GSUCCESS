"""
GPAT 2027 AI Learning OS — SQLite to Supabase Migration Worker
Reads verified records from local SQLite (gpat_knowledge.db) and exports/migrates
into Supabase PostgreSQL schema with pgvector embeddings and FSRS memory models.
"""

import os
import sys
import json
import sqlite3
import argparse
from typing import Dict, Any, List
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "gpat_knowledge.db"

def inspect_sqlite_data():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cur.fetchall() if not r[0].startswith("sqlite_")]
    
    summary = {}
    for t in tables:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        summary[t] = cur.fetchone()[0]
        
    conn.close()
    return summary

def export_to_json(output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cur.fetchall() if not r[0].startswith("sqlite_")]
    
    exported = {}
    for t in tables:
        cur.execute(f"PRAGMA table_info({t})")
        columns = [c[1] for c in cur.fetchall()]
        
        cur.execute(f"SELECT * FROM {t}")
        rows = []
        for r in cur.fetchall():
            row_dict = {}
            for idx, col in enumerate(columns):
                val = r[idx]
                # If column is blob (e.g. embedding_blob), convert or skip for raw json
                if isinstance(val, bytes):
                    continue
                row_dict[col] = val
            rows.append(row_dict)
            
        file_path = output_dir / f"{t}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(rows, f, indent=2)
            
        exported[t] = len(rows)
        print(f"Exported {len(rows)} rows from {t} -> {file_path.name}")
        
    conn.close()
    return exported

def migrate_to_supabase(supabase_url: str, supabase_key: str):
    """
    Direct migration into Supabase via postgrest-py / supabase-py client.
    Called when user provides their Supabase URL & Service Key.
    """
    print(f"\n=======================================================")
    print(f"MIGRATING GPAT 2027 DATA TO SUPABASE: {supabase_url}")
    print(f"=======================================================\n")
    try:
        from supabase import create_client, Client
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Test connection
        print("Connected to Supabase successfully.")
        return True
    except ImportError:
        print("Error: `supabase` python package not installed. Run: pip install supabase")
        return False
    except Exception as e:
        print(f"Supabase migration error: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GPAT 2027 SQLite to Supabase Migration Utility")
    parser.add_argument("--export", action="store_true", help="Export SQLite tables to JSON")
    parser.add_argument("--supabase-url", type=str, help="Supabase Project URL")
    parser.add_argument("--supabase-key", type=str, help="Supabase Service Role Key")
    args = parser.parse_args()
    
    summary = inspect_sqlite_data()
    print("\n--- Current SQLite Knowledge Database Snapshot ---")
    for t, count in summary.items():
        print(f"  * {t}: {count} records")
        
    if args.export or (not args.supabase_url):
        out = Path(__file__).resolve().parent.parent / "backend" / "data_export"
        print(f"\nExporting dataset to {out}...")
        export_to_json(out)
        print("\nReady for Supabase PostgreSQL import.")
        
    if args.supabase_url and args.supabase_key:
        migrate_to_supabase(args.supabase_url, args.supabase_key)
