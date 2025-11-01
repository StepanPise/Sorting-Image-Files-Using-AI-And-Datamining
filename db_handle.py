import sqlite3

conn = sqlite3.connect("photo_ai.db")
cursor = conn.cursor()

# cursor.execute("SELECT id FROM faces")

cursor.execute("""
    SELECT p.name, ph.path
    FROM people p
    JOIN faces f ON f.person_id = p.id
    JOIN photos ph ON ph.id = f.photo_id
    ORDER BY p.name
""")

rows = cursor.fetchall()

for row in rows:
    print(row)

conn.commit()
conn.close()
