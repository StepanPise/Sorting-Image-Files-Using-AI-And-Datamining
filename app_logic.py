from pathlib import Path
from PIL import Image, ImageOps
import json
import time

from db_setup import Database
from metadata_handle import PhotoMetadata
from face_clustering import assign_person_ids
from face_detection import FaceDetection
from repositories.photo_repo import PhotoRepository
from repositories.face_repo import FaceRepository
from repositories.person_repo import PersonRepository


class PhotoController:
    def __init__(self):
        self.db = Database()
        self.photo_repo = PhotoRepository(self.db)
        self.face_repo = FaceRepository(self.db)
        self.person_repo = PersonRepository(self.db)
        self.face_detector = FaceDetection(self.photo_repo, self.face_repo)

    def analyze_folder(self, folder_path, detect_faces=True):
        input_folder = Path(folder_path)

        # 1. Get metadata
        self._scan_metadata(input_folder)

        # 2. Face detection
        if detect_faces:
            self.face_detector.process_faces(input_folder)
            assign_person_ids()

    def _scan_metadata(self, input_folder: Path):
        for path in input_folder.iterdir():
            if path.is_file() and path.suffix.lower() in [".jpg", ".jpeg", ".png"]:
                filename = path.name
                path_str = str(path)
                hash_val = self.face_detector.compute_hash(path)
                time_data = PhotoMetadata.get_date(path)
                location_data = PhotoMetadata.get_location(path)
                width, height = PhotoMetadata.get_size(path)

                # Check if photo with this hash exists to prevent duplication
                exists = self.photo_repo.get_by_hash(hash_val)

                if exists:
                    self.photo_repo.update_photo(
                        photo_id=exists["id"], path=path_str, filename=filename)
                else:
                    self.photo_repo.insert_photo(
                        path=path_str, filename=filename, hash=hash_val,
                        location_data=location_data, time_data=time_data,
                        width=width, height=height
                    )

    def get_person_thumbnail(self, person_id):

        rows = self.face_repo.get_faces_by_person_id(person_id)

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

# =========================================================================
#  WRAPPER METODS FOR UI (app.py)
# =========================================================================

    def get_all_people(self):
        return self.person_repo.get_all_with_faces()

    def update_person_name(self, person_id, new_name):
        self.person_repo.update_name(person_id, new_name)
