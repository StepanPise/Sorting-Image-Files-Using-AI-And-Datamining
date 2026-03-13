from .base_repo import BaseRepository


class PersonRepository(BaseRepository):

    def get_all(self):
        self.cursor.execute("SELECT * FROM people")
        return self.cursor.fetchall()

    def get_all_with_faces(self, subset_ids=None, min_photos=1):
        query = """
                SELECT p.id, p.name
                FROM people p
                JOIN faces f ON p.id = f.person_id
                JOIN (
                    SELECT person_id, COUNT(DISTINCT photo_id) as total_photos
                    FROM faces
                    GROUP BY person_id
                ) t1 ON t1.person_id = p.id
                WHERE t1.total_photos >= %s
            """

        params = [min_photos]

        if subset_ids is not None:
            if len(subset_ids) == 0:
                query += " AND 1=0 "
            else:
                query += " AND f.photo_id = ANY(%s) "
                params.append(list(subset_ids))

        query += " GROUP BY p.id, p.name ORDER BY COUNT(DISTINCT f.photo_id) DESC "

        self.cursor.execute(query, tuple(params))
        return self.cursor.fetchall()

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

    def update_name(self, person_id, new_name):
        self.cursor.execute(
            "UPDATE people SET name = %s WHERE id = %s",
            (new_name, person_id)
        )
        self.conn.commit()
