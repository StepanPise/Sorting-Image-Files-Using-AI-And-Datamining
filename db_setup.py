import sqlite3

conn = sqlite3.connect("photo_ai.db")
cursor = conn.cursor()

# PHOTOS
cursor.execute("""
CREATE TABLE IF NOT EXISTS photos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT NOT NULL,
    filename TEXT NOT NULL,
    location_data TEXT,
    time_data TEXT,
    width INTEGER,
    height INTEGER
)
""")

# TAGS
cursor.execute("""
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
)
""")

# PHOTO_TAGS (many-to-many)
cursor.execute("""
CREATE TABLE IF NOT EXISTS photo_tags (
    photo_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    FOREIGN KEY(photo_id) REFERENCES photos(id),
    FOREIGN KEY(tag_id) REFERENCES tags(id)
)
""")

# FACES (randos)
cursor.execute("""
CREATE TABLE IF NOT EXISTS faces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    photo_id INTEGER NOT NULL,
    embedding BLOB NOT NULL,
    person_id INTEGER,
    FOREIGN KEY(photo_id) REFERENCES photos(id),
    FOREIGN KEY(person_id) REFERENCES people(id)
)
""")

# PEOPLE (identified faces)
cursor.execute("""
CREATE TABLE IF NOT EXISTS people (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
)
""")

conn.commit()
conn.close()
print("✅ Databaze uspesne vytvorena: photo_ai.db")
