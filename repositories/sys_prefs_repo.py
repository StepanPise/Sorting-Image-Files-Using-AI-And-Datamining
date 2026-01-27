from .base_repo import BaseRepository


class SystemPrefsRepository(BaseRepository):

    def save_pref(self, key, value):
        self.cursor.execute("""
            INSERT INTO system_preferences (key, value)
            VALUES (%s, %s)
            ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
        """, (key, str(value)))
        self.connection.commit()

    def load_pref(self, key, default=None):
        self.cursor.execute(
            "SELECT value FROM system_preferences WHERE key=%s", (key,))
        res = self.cursor.fetchone()
        if res is None:
            return default
        val = res[0]
        if val.lower() in ("true", "false"):
            return val.lower() == "true"
        try:
            return int(val)
        except ValueError:
            try:
                return float(val)
            except ValueError:
                return val

# face_detection = bool
# window_width = int
# window_height = int
# ....
