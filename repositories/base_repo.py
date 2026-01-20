class BaseRepository:

    def __init__(self, db_instance):
        self.db = db_instance
        self.cursor = db_instance.cursor
        self.conn = db_instance.conn
