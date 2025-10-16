import sqlite3
from pathlib import *

conn = sqlite3.connect("photo_ai.db")
cursor = conn.cursor()


# for p in Path().iterdir():
#     print(p)

my_dir = Path("Directory")

print("Existuje složka?:", my_dir.exists())

new_file = my_dir / "new_file.txt"
print(new_file.parent.parent)

conn.commit()
conn.close()
