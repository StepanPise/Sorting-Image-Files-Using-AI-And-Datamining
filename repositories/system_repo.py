from .base_repo import BaseRepository


class SystemRepository(BaseRepository):

    def get_all_preferences(self):
        self.cursor.execute("SELECT key, value FROM system_preferences")
        rows = self.cursor.fetchall()

        return {row['key']: row['value'] for row in rows}

    def set_preference(self, key: str, value: str):
        query = """
            INSERT INTO system_preferences (key, value) 
            VALUES (%s, %s) 
            ON CONFLICT (key) 
            DO UPDATE SET value = EXCLUDED.value
        """
        self.cursor.execute(query, (key, str(value)))
        self.conn.commit()

    def wipe_database(self):
        self.cursor.execute(
            "TRUNCATE TABLE photos, people, faces RESTART IDENTITY CASCADE;")
        self.conn.commit()
        return True
