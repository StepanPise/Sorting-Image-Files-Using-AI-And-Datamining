from db_setup import Database

db = Database()

db.cursor.execute(
    "SELECT id, avg_embedding FROM people")

print("avgembedings:", db.cursor.fetchall())

db.cursor.execute("SELECT COUNT(*) FROM faces")
print("Faces:", db.cursor.fetchone())

db.cursor.execute("SELECT COUNT(*) FROM people")
print("People:", db.cursor.fetchone())

db.close()
