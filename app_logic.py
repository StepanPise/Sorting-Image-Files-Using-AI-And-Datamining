from pathlib import Path
from PIL import Image, ImageOps
import json
import time

from db_setup import Database
from metadata_handle import PhotoMetadata
from face_clustering import assign_person_ids
from face_detection import process_faces, compute_hash


class PhotoController:
    def __init__(self):
        self.db = Database()

    def analyze_folder(self, folder_path, detect_faces=True):
        """Main scanning process."""
        input_folder = Path(folder_path)

        # 1. Get metadata
        self._scan_metadata(input_folder)

        # 2. Face detection
        if detect_faces:
            process_faces(input_folder)
            assign_person_ids()

    def _scan_metadata(self, input_folder: Path):
        """Private method for file scanning."""
        for path in input_folder.iterdir():
            if path.is_file() and path.suffix.lower() in [".jpg", ".jpeg", ".png"]:
                filename = path.name
                path_str = str(path)
                hash_val = compute_hash(path)
                time_data = PhotoMetadata.get_date(path)
                location_data = PhotoMetadata.get_location(path)
                width, height = PhotoMetadata.get_size(path)

                # Check if photo with this hash exists to prevent duplication
                self.db.cursor.execute(
                    "SELECT id FROM photos WHERE hash = %s", (hash_val,))
                exists = self.db.cursor.fetchone()

                if exists:
                    self.db.update_photo(
                        photo_id=exists["id"], path=path_str, filename=filename)
                else:
                    self.db.insert_photo(path=path_str, filename=filename, hash=hash_val,
                                         location_data=location_data, time_data=time_data,
                                         width=width, height=height)

    def get_all_people(self):
        """Returns list of people (data), not UI elements."""
        self.db.cursor.execute("""
            SELECT p.id, p.name
            FROM people p
            JOIN faces f ON f.person_id = p.id
            JOIN photos ph ON ph.id = f.photo_id
            GROUP BY p.id, p.name
            ORDER BY p.name;
        """)
        return self.db.cursor.fetchall()

    def update_person_name(self, person_id, new_name):
        self.db.cursor.execute(
            "UPDATE people SET name = %s WHERE id = %s", (new_name, person_id))
        self.db.conn.commit()

    def get_person_thumbnail(self, person_id):
        """Returns PIL Image object (cropped face) or None."""
        self.db.cursor.execute(
            """
            SELECT f.face_coords, p.path
            FROM faces f
            JOIN photos p ON p.id = f.photo_id
            WHERE f.person_id = %s
            """,
            (person_id,)
        )
        rows = self.db.cursor.fetchall()
        if not rows:
            return None

        # Find the biggest face for thumbnail
        biggest_area = -1
        biggest_face = None
        biggest_photo_path = None

        for row in rows:
            try:
                coords = json.loads(json.loads(row["face_coords"]))
                if not coords:
                    continue
                left, top, right, bottom = coords[0]
                area = (right - left) * (bottom - top)
                if area > biggest_area:
                    biggest_area = area
                    biggest_face = (left, top, right, bottom)
                    biggest_photo_path = row["path"]
            except Exception:
                continue

        if not biggest_face:
            return None

        try:
            img = Image.open(biggest_photo_path)
            left, top, right, bottom = biggest_face
            MARGIN = 30
            img_crop = img.crop((
                max(0, left - MARGIN),
                max(0, top - MARGIN),
                min(img.width, right + MARGIN),
                min(img.height, bottom + MARGIN)
            ))
            return ImageOps.exif_transpose(img_crop)
        except Exception:
            return None

    def close(self):
        self.db.close()
