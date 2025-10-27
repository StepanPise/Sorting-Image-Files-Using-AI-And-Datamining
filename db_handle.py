import sqlite3

conn = sqlite3.connect("photo_ai.db")
cursor = conn.cursor()

# cursor.execute("SELECT id FROM faces")

cursor.execute("SELECT filename FROM photos")


rows = cursor.fetchall()

for row in rows:
    print(row)

conn.commit()
conn.close()
