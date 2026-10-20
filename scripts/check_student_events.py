import sqlite3

conn = sqlite3.connect('gpat_knowledge.db')
cur = conn.cursor()
cur.execute("SELECT date(timestamp), event_type, count(*) FROM learning_events WHERE user_id='student_01' GROUP BY date(timestamp), event_type")
print("student_01 events:", cur.fetchall())
conn.close()
