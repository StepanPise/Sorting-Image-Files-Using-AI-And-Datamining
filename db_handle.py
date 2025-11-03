from db_setup import Database
import json

db = Database()

db.cursor.execute("""
    SELECT p.name, ph.path
    FROM people p
    JOIN faces f ON f.person_id = p.id
    JOIN photos ph ON ph.id = f.photo_id
    ORDER BY p.name
""")
rows = db.cursor.fetchall()

for row in rows:
    print(row)

db.conn.commit()
db.conn.close()
