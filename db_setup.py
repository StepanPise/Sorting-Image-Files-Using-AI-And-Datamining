import psycopg2
import psycopg2.extras
from typing import List, Tuple, Optional
import numpy as np
import json


class Database:

    def __init__(self):
        self.conn = psycopg2.connect(
            host="localhost",
            port=5433,
            dbname="postgres",
            user="myuser",
            password="mysecretpassword"
        )

        self.cursor = self.conn.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor
        )
        print("Connected to PostgreSQL")

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
        INSERT INTO photos 
        (path, filename, hash, already_analyzed, location_data, time_data, width, height)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """, (path, filename, hash, already_analyzed, location_data, time_data, width, height))

        photo_id = self.cursor.fetchone()["id"]
        self.conn.commit()
        return photo_id

    def get_photos(self):
        self.cursor.execute("SELECT * FROM photos")
        return self.cursor.fetchall()

    def delete_photo(self, photo_id: int) -> None:
        self.cursor.execute("DELETE FROM photos WHERE id = %s", (photo_id,))
        self.conn.commit()

    def update_photo(self, photo_id: int, **kwargs):
        if not kwargs:
            return

        columns = ", ".join(f"{col} = %s" for col in kwargs)
        values = list(kwargs.values())
        values.append(photo_id)

        query = f"UPDATE photos SET {columns} WHERE id = %s"
        self.cursor.execute(query, values)
        self.conn.commit()

    # -------------------------
    # TAGS
    # -------------------------

    def insert_tag(self, name: str) -> int:
        self.cursor.execute("""
        INSERT INTO tags (name) VALUES (%s)
        RETURNING id
        """, (name,))
        tag_id = self.cursor.fetchone()["id"]
        self.conn.commit()
        return tag_id

    def get_tags(self):
        self.cursor.execute("SELECT * FROM tags")
        return self.cursor.fetchall()

    def delete_tag(self, tag_id: int) -> None:
        self.cursor.execute("DELETE FROM tags WHERE id = %s", (tag_id,))
        self.conn.commit()

    # -------------------------
    # PEOPLE
    # -------------------------

    def insert_person(self, name: str, avg_embedding: Optional[np.ndarray] = None) -> int:
        self.cursor.execute("SELECT id FROM people WHERE name = %s", (name,))
        existing = self.cursor.fetchone()
        if existing:
            return existing["id"]

        if avg_embedding is not None:
            if isinstance(avg_embedding, np.ndarray):
                avg_bytes = avg_embedding.tobytes()
            elif isinstance(avg_embedding, bytes):
                avg_bytes = avg_embedding
            else:
                raise ValueError(
                    f"avg_embedding must be np.ndarray or bytes, got {type(avg_embedding)}")

            self.cursor.execute(
                "INSERT INTO people (name, avg_embedding) VALUES (%s, %s) RETURNING id",
                (name, psycopg2.Binary(avg_bytes))
            )
        else:
            self.cursor.execute(
                "INSERT INTO people (name) VALUES (%s) RETURNING id",
                (name,)
            )

        person_id = self.cursor.fetchone()["id"]
        self.conn.commit()
        return person_id

    def get_people(self):
        self.cursor.execute("SELECT * FROM people")
        return self.cursor.fetchall()

    def delete_person(self, person_id: int) -> None:
        self.cursor.execute("DELETE FROM people WHERE id = %s", (person_id,))
        self.conn.commit()

    # -------------------------
    # FACES
    # -------------------------

    def insert_face(self, photo_id: int, embedding: bytes,
                    face_coords=None, person_id=None) -> int:

        face_coords_str = json.dumps(face_coords or [])

        self.cursor.execute("""
            INSERT INTO faces (photo_id, embedding, face_coords, person_id)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (photo_id, psycopg2.Binary(embedding), face_coords_str, person_id))

        face_id = self.cursor.fetchone()["id"]
        self.conn.commit()
        return face_id

    def get_faces(self):
        self.cursor.execute("SELECT * FROM faces")
        rows = self.cursor.fetchall()
        for row in rows:
            if isinstance(row['embedding'], memoryview):
                row['embedding'] = row['embedding'].tobytes()
        return rows

    def delete_face(self, face_id: int) -> None:
        self.cursor.execute("DELETE FROM faces WHERE id = %s", (face_id,))
        self.conn.commit()

    # -------------------------
    # PHOTO_TAGS
    # -------------------------

    def add_tag_to_photo(self, photo_id: int, tag_id: int) -> None:
        self.cursor.execute("""
        INSERT INTO photo_tags (photo_id, tag_id)
        VALUES (%s, %s)
        """, (photo_id, tag_id))
        self.conn.commit()

    def get_photo_tags(self):
        self.cursor.execute("SELECT * FROM photo_tags")
        return self.cursor.fetchall()

    def remove_tag_from_photo(self, photo_id: int, tag_id: int) -> None:
        self.cursor.execute("""
        DELETE FROM photo_tags WHERE photo_id = %s AND tag_id = %s
        """, (photo_id, tag_id))
        self.conn.commit()

    # -------------------------
    # CLOSE
    # -------------------------

    def close(self) -> None:
        self.conn.close()
        print("Pripojeni k databazi uzavreno")
