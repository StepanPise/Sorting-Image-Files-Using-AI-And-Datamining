from .base_repo import BaseRepository


class PersonRepository(BaseRepository):

    def get_all(self):
        self.cursor.execute("SELECT * FROM people")
        return self.cursor.fetchall()

    def get_all_with_faces(self):
        self.cursor.execute("""
            SELECT p.id, p.name
            FROM people p
            JOIN faces f ON f.person_id = p.id
            JOIN photos ph ON ph.id = f.photo_id
            GROUP BY p.id, p.name
            ORDER BY p.name;
        """)
        return self.cursor.fetchall()

    def update_name(self, person_id, new_name):
        self.cursor.execute(
            "UPDATE people SET name = %s WHERE id = %s",
            (new_name, person_id)
        )
        self.conn.commit()
