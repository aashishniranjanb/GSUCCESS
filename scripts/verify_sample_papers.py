import sqlite3
import json

conn = sqlite3.connect("data/gpat_baseline.db")
cur = conn.cursor()

years = [2025, 2018, 2012]
for y in years:
    print(f"==================== GPAT {y} ====================")
    # Total published
    cur.execute("SELECT count(*) FROM baseline_questions WHERE pyq_year = ?", (y,))
    pub_cnt = cur.fetchone()[0]
    
    # Total quarantined
    cur.execute("SELECT count(*) FROM pyq_review_queue WHERE pyq_year = ?", (y,))
    quar_cnt = cur.fetchone()[0]
    
    print(f"Published: {pub_cnt} | Quarantined: {quar_cnt} | Total: {pub_cnt + quar_cnt}")
    
    # Sample published
    cur.execute("""
        SELECT original_q_number, source_page, question_text, options_json, correct_option, answer_status
        FROM baseline_questions
        WHERE pyq_year = ?
        ORDER BY original_q_number ASC
        LIMIT 3
    """, (y,))
    rows = cur.fetchall()
    print("Sample Published Questions:")
    for r in rows:
        opts = json.loads(r[3])
        correct_letter = chr(ord('a') + r[4]) if r[4] is not None and 0 <= r[4] < len(opts) else str(r[4])
        print(f"  Q{r[0]} (Page {r[1]}, Key: {correct_letter}): {r[2][:70]}...")
        for idx, o in enumerate(opts):
            print(f"    ({chr(ord('a')+idx)}) {o[:50]}")
            
    # Sample quarantined
    cur.execute("""
        SELECT original_q_number, issue_type, raw_text
        FROM pyq_review_queue
        WHERE pyq_year = ?
        ORDER BY original_q_number ASC
        LIMIT 2
    """, (y,))
    q_rows = cur.fetchall()
    if q_rows:
        print("Sample Quarantined Items:")
        for qr in q_rows:
            raw_snip = (qr[2][:60] if qr[2] else 'None').replace('\n', ' ')
            print(f"  Q{qr[0]} [{qr[1]}]: {raw_snip}...")

conn.close()
