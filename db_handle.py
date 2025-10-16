import sqlite3

conn = sqlite3.connect("photo_ai.db")
cursor = conn.cursor()


photo_data = (
    "C:/images/holiday/beach.jpg",  # path
    "beach.jpg",                     # filename
    "Spain",                         # location_data
    "2025-07-18 15:32",              # time_data
    1920,                            # width
    1080                             # height
)

cursor.execute("""
INSERT INTO photos (path, filename, location_data, time_data, width, height)
VALUES (?, ?, ?, ?, ?, ?)
""", photo_data)

cursor.execute("SELECT filename FROM photos")


rows = cursor.fetchall()

for row in rows:
    print(row)

conn.commit()
conn.close()
