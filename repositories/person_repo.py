from .base_repo import BaseRepository


class PersonRepository(BaseRepository):

    def get_all(self):
        self.cursor.execute("SELECT * FROM people")
        return self.cursor.fetchall()
