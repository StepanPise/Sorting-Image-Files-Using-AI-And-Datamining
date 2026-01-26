from .base_repo import BaseRepository


class PhotoRepository(BaseRepository):

    def get_all(self):
        self.cursor.execute("SELECT * FROM photos")
        return self.cursor.fetchall()

    def get_by_hash(self, hash_val):
        self.cursor.execute(
            "SELECT * FROM photos WHERE hash = %s", (hash_val,))
        return self.cursor.fetchone()

    def insert_photo(self, **kwargs):
        self.cursor.execute(
            """
            INSERT INTO photos (path, filename, hash, location_data, time_data, width, height)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (kwargs["path"], kwargs["filename"], kwargs["hash"], kwargs["location_data"],
             kwargs["time_data"], kwargs["width"], kwargs["height"])
        )
        self.conn.commit()

    def update_photo(self, photo_id, **kwargs):
        self.cursor.execute(
            "UPDATE photos SET path=%s, filename=%s WHERE id=%s",
            (kwargs["path"], kwargs["filename"], photo_id)
        )
        self.conn.commit()

    def mark_analyzed(self, photo_id):
        self.cursor.execute(
            "UPDATE photos SET already_analyzed = 1 WHERE id = %s",
            (photo_id,)
        )
        self.conn.commit()

    # def mark_scanned(self, photo_id):
    #     self.cursor.execute(
    #         "UPDATE photos SET metadata_scanned = 1 WHERE id = %s",
    #         (photo_id,)
    #     )
    #     self.conn.commit()
