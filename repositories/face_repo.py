from .base_repo import BaseRepository


class FaceRepository(BaseRepository):

    def get_all(self):
        self.cursor.execute("SELECT * FROM faces")
        return self.cursor.fetchall()

    def get_faces_by_person_id(self, person_id):
        self.cursor.execute("""
            SELECT f.face_coords, p.path
            FROM faces f
            JOIN photos p ON p.id = f.photo_id
            WHERE f.person_id = %s
        """, (person_id,))
        return self.cursor.fetchall()

    def add(self, photo_id, embedding_bytes, face_coords):
        self.cursor.execute(
            """
                INSERT INTO faces (photo_id, embedding, face_coords, person_id)
                VALUES (%s, %s, %s, NULL)
                """,
            (photo_id, embedding_bytes, face_coords)
        )
        self.conn.commit()

    def get_all_embeddings(self):
        self.cursor.execute("SELECT id, embedding FROM faces")
        return self.cursor.fetchall()

    def update_person_id(self, face_id, person_id):
        self.cursor.execute(
            "UPDATE faces SET person_id = %s WHERE id = %s",
            (person_id, face_id)
        )
        self.conn.commit()
