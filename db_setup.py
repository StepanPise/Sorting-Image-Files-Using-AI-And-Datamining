import sqlite3
from sqlite3 import Connection, Cursor
from typing import List, Tuple, Optional
import numpy as np


class Database:
    DB_PATH: str = "photo_ai.db"

    def __init__(self):
        self.conn: Connection = sqlite3.connect(self.DB_PATH)
        self.cursor: Cursor = self.conn.cursor()
        self.conn.row_factory = sqlite3.Row
        self.create_tables()

    def create_tables(self) -> None:
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS photos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT NOT NULL,
            filename TEXT NOT NULL,
            hash TEXT UNIQUE NOT NULL,
            already_analyzed INTEGER DEFAULT 0,
            location_data TEXT,
            time_data TEXT,
            width INTEGER,
            height INTEGER
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS photo_tags (
            photo_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            FOREIGN KEY(photo_id) REFERENCES photos(id),
            FOREIGN KEY(tag_id) REFERENCES tags(id)
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS people (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            avg_embedding BLOB
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS faces (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            photo_id INTEGER NOT NULL,
            embedding BLOB NOT NULL,
            person_id INTEGER,
            FOREIGN KEY(photo_id) REFERENCES photos(id),
            FOREIGN KEY(person_id) REFERENCES people(id)
        )
        """)

        self.conn.commit()
        print("Databaze a tabulky byly uspesne vytvoreny")

    # -------------------------
    # PHOTOS
    # -------------------------

    def insert_photo(self, path: str, filename: str, hash: str,
                     already_analyzed: int = 0,
                     location_data: Optional[str] = None,
                     time_data: Optional[str] = None,
                     width: Optional[int] = None,
                     height: Optional[int] = None) -> int:
        self.cursor.execute("""
        INSERT INTO photos (path, filename, hash, already_analyzed, location_data, time_data, width, height)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (path, filename, hash, already_analyzed, location_data, time_data, width, height))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_photos(self) -> List[sqlite3.Row]:
        self.cursor.execute("SELECT * FROM photos")
        return self.cursor.fetchall()

    def delete_photo(self, photo_id: int) -> None:
        self.cursor.execute("DELETE FROM photos WHERE id = ?", (photo_id,))
        self.conn.commit()

    def update_photo(self, photo_id: int, **kwargs):
        """
        kwargs: column name = new value
        """
        if not kwargs:
            return

        columns = ", ".join(f"{col} = ?" for col in kwargs)
        values = list(kwargs.values())
        values.append(photo_id)  # pro WHERE id = ?

        query = f"UPDATE photos SET {columns} WHERE id = ?"
        self.cursor.execute(query, values)
        self.conn.commit()

    # -------------------------
    # TAGS
    # -------------------------

    def insert_tag(self, name: str) -> int:
        self.cursor.execute("INSERT INTO tags (name) VALUES (?)", (name,))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_tags(self) -> List[sqlite3.Row]:
        self.cursor.execute("SELECT * FROM tags")
        return self.cursor.fetchall()

    def delete_tag(self, tag_id: int) -> None:
        self.cursor.execute("DELETE FROM tags WHERE id = ?", (tag_id,))
        self.conn.commit()

    # -------------------------
    # PEOPLE
    # -------------------------

    def insert_person(self, name: str, avg_embedding: Optional[np.ndarray] = None) -> int:
        if avg_embedding is not None:
            avg_bytes = avg_embedding.tobytes()
            self.cursor.execute(
                "INSERT INTO people (name, avg_embedding) VALUES (?, ?)",
                (name, avg_bytes)
            )
        else:
            self.cursor.execute(
                "INSERT INTO people (name) VALUES (?)", (name,))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_people(self) -> List[sqlite3.Row]:
        self.cursor.execute("SELECT * FROM people")
        return self.cursor.fetchall()

    def delete_person(self, person_id: int) -> None:
        self.cursor.execute("DELETE FROM people WHERE id = ?", (person_id,))
        self.conn.commit()

    # -------------------------
    # FACES
    # -------------------------
    def insert_face(self, photo_id: int, embedding: bytes, person_id: Optional[int] = None) -> int:
        self.cursor.execute("""
        INSERT INTO faces (photo_id, embedding, person_id)
        VALUES (?, ?, ?)
        """, (photo_id, embedding, person_id))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_faces(self) -> List[sqlite3.Row]:
        self.cursor.execute("SELECT * FROM faces")
        return self.cursor.fetchall()

    def delete_face(self, face_id: int) -> None:
        self.cursor.execute("DELETE FROM faces WHERE id = ?", (face_id,))
        self.conn.commit()

    # -------------------------
    # PHOTO_TAGS
    # -------------------------
    def add_tag_to_photo(self, photo_id: int, tag_id: int) -> None:
        self.cursor.execute("""
        INSERT INTO photo_tags (photo_id, tag_id) VALUES (?, ?)
        """, (photo_id, tag_id))
        self.conn.commit()

    def get_photo_tags(self) -> List[sqlite3.Row]:
        self.cursor.execute("SELECT * FROM photo_tags")
        return self.cursor.fetchall()

    def remove_tag_from_photo(self, photo_id: int, tag_id: int) -> None:
        self.cursor.execute("""
        DELETE FROM photo_tags WHERE photo_id = ? AND tag_id = ?
        """, (photo_id, tag_id))
        self.conn.commit()

    # -------------------------
    # CLOSE
    # -------------------------
    def close(self) -> None:
        self.conn.close()
        print("Pripojeni k databazi uzavreno")


if __name__ == "__main__":
    db = Database()
    db.close()
