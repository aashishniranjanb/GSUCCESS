import sqlite3

conn = sqlite3.connect('gpat_knowledge.db')
cur = conn.cursor()
cur.execute("PRAGMA table_info(learning_events)")
for r in cur.fetchall():
    print(r)
cur.execute("SELECT * FROM learning_events LIMIT 3")
for r in cur.fetchall():
    print(r)
conn.close()
