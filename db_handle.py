from db_setup import Database

db = Database()

db.cursor.execute("SELECT COUNT(*) FROM photos")
print("Images:", db.cursor.fetchall())

db.cursor.execute("SELECT COUNT(*) FROM faces")
print("Faces:", db.cursor.fetchone())

db.cursor.execute("SELECT COUNT(*) FROM people")
print("People:", db.cursor.fetchone())

db.close()
