from db_setup import Database
import json

db = Database()

db.cursor.execute("""
SELECT id,face_coords FROM faces

""")
rows = db.cursor.fetchall()

for row in rows:
    print(row)

db.conn.commit()
db.conn.close()
