class BaseRepository:

    def __init__(self, db_instance):
        self.db = db_instance
        self.cursor = db_instance.cursor
        self.conn = db_instance.conn

    def wipe_database(self):
        self.cursor.execute(
            "TRUNCATE TABLE photos, people, faces, system_preferences RESTART IDENTITY CASCADE;")
        self.conn.commit()
