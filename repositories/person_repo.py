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

    # Create person and return id
    def create_person(self, name, avg_embedding_bytes):
        self.cursor.execute(
            "INSERT INTO people (name, avg_embedding) VALUES (%s, %s) RETURNING id",
            (name, avg_embedding_bytes)
        )
        new_id = self.cursor.fetchone()['id']
        self.conn.commit()
        return new_id

    def get_all_people_data(self):
        self.cursor.execute("SELECT id, name, avg_embedding FROM people")
        return self.cursor.fetchall()

    def update_embedding(self, person_id, avg_embedding_bytes):
        self.cursor.execute(
            "UPDATE people SET avg_embedding = %s WHERE id = %s",
            (avg_embedding_bytes, person_id)
        )
        self.conn.commit()
