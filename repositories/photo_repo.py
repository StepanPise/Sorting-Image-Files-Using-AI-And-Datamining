from .base_repo import BaseRepository


class PhotoRepository(BaseRepository):

    def get_all(self):
        self.cursor.execute("SELECT * FROM photos")
        return self.cursor.fetchall()
