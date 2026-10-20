import sqlite3

conn = sqlite3.connect('gpat_knowledge.db')
cur = conn.cursor()
cur.execute("SELECT date(created_at), count(*), sum(is_correct) FROM student_attempts WHERE student_id='student_01' GROUP BY date(created_at)")
print("attempts by date:", cur.fetchall())
cur.execute("SELECT count(*) FROM fsrs_cards WHERE student_id='student_01'")
print("total fsrs cards:", cur.fetchone()[0])
cur.execute("SELECT count(*) FROM fsrs_cards WHERE student_id='student_01' AND due <= datetime('now')")
print("due fsrs cards:", cur.fetchone()[0])
conn.close()
