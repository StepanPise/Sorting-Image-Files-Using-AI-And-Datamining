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
