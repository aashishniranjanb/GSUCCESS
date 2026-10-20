import sqlite3
import json

def audit_db():
    conn = sqlite3.connect('gpat_knowledge.db')
    cur = conn.cursor()
    
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [r[0] for r in cur.fetchall()]
    print(f"Total tables: {len(tables)}")
    
    table_counts = {}
    for t in tables:
        try:
            cur.execute(f"SELECT count(*) FROM [{t}]")
            table_counts[t] = cur.fetchone()[0]
        except Exception as e:
            table_counts[t] = str(e)
            
    for t, c in sorted(table_counts.items()):
        print(f"  {t}: {c}")
        
    print("\n--- Integrity and Constraints ---")
    cur.execute("PRAGMA foreign_key_check")
    fk = cur.fetchall()
    print(f"PRAGMA foreign_key_check: {len(fk)} violations ({fk})")
    
    cur.execute("PRAGMA integrity_check")
    ic = cur.fetchall()
    print(f"PRAGMA integrity_check: {ic}")
    
    print("\n--- Claim Verification Status ---")
    cur.execute("SELECT verification_status, count(*) FROM candidate_claims GROUP BY verification_status")
    for r in cur.fetchall():
        print(f"  {r[0]}: {r[1]}")
        
    print("\n--- Question Verification Status ---")
    cur.execute("SELECT verification_status, count(*) FROM generated_questions GROUP BY verification_status")
    for r in cur.fetchall():
        print(f"  {r[0]}: {r[1]}")
        
    print("\n--- Provenance Linking ---")
    cur.execute("SELECT count(*) FROM candidate_claims WHERE source_block_id IS NULL OR source_block_id = ''")
    print(f"  Claims with missing source_block_id: {cur.fetchone()[0]}")
    
    cur.execute("""
        SELECT count(c.id) 
        FROM candidate_claims c 
        LEFT JOIN content_blocks b ON c.source_block_id = b.id 
        WHERE b.id IS NULL AND c.source_block_id IS NOT NULL AND c.source_block_id != ''
    """)
    print(f"  Claims with unresolvable source_block_id: {cur.fetchone()[0]}")
    
    cur.execute("SELECT count(*) FROM generated_questions WHERE evidence_block_id IS NULL OR evidence_block_id = ''")
    print(f"  Questions with missing evidence_block_id: {cur.fetchone()[0]}")

    cur.execute("""
        SELECT count(q.id) 
        FROM generated_questions q 
        LEFT JOIN content_blocks b ON q.evidence_block_id = b.id 
        WHERE b.id IS NULL AND q.evidence_block_id IS NOT NULL AND q.evidence_block_id != ''
    """)
    print(f"  Questions with unresolvable evidence_block_id: {cur.fetchone()[0]}")

    print("\n--- Mock Exams & Blueprints ---")
    cur.execute("SELECT id, blueprint_id, total_questions, duration_minutes, is_submitted FROM mock_exam_sessions")
    print("Mock exam sessions:", cur.fetchall())
    
    print("\n--- Student Progress & FSRS Records ---")
    cur.execute("SELECT count(*) FROM student_fsrs_state")
    print(f"  FSRS cards: {cur.fetchone()[0]}")
    cur.execute("SELECT count(*) FROM student_attempts")
    print(f"  Student attempts: {cur.fetchone()[0]}")
    cur.execute("SELECT count(*) FROM learning_events")
    print(f"  Learning events: {cur.fetchone()[0]}")
    cur.execute("SELECT count(*) FROM synced_client_events")
    print(f"  Synced client events: {cur.fetchone()[0]}")

    conn.close()

if __name__ == '__main__':
    audit_db()
