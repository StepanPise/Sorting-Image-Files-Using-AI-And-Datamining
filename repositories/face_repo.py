from .base_repo import BaseRepository


class FaceRepository(BaseRepository):

    def get_all(self):
        self.cursor.execute("SELECT * FROM faces")
        return self.cursor.fetchall()
