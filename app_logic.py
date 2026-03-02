from pathlib import Path
from tokenize import String
from PIL import Image, ImageOps
import json
import hashlib

import shutil
import os
from datetime import datetime

from db_setup import Database
from metadata_handle import PhotoMetadata
from face_clustering import FaceClustering
from face_detection import FaceDetection
from repositories.photo_repo import PhotoRepository
from repositories.face_repo import FaceRepository
from repositories.person_repo import PersonRepository
from structures import FilterCriteria


class PhotoController:
    def __init__(self):
        self.db = Database()
        self.photo_repo = PhotoRepository(self.db)
        self.face_repo = FaceRepository(self.db)
        self.person_repo = PersonRepository(self.db)

        self.criteria = FilterCriteria()

        self.face_detector = FaceDetection(self.photo_repo, self.face_repo)
        self.face_clustering = FaceClustering(self.face_repo, self.person_repo)
        self.current_batch_ids = set()

    def analyze_folder(self, folder_path, detect_faces=True, callback=None):

        self.current_batch_ids.clear()

        input_folder = Path(folder_path)

        image_paths = [
            p for p in input_folder.rglob("*")
            if p.is_file() and p.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]
        ]

        total_photos = len(image_paths)

        if total_photos == 0:
            if callback:
                callback(1.0, "No photos found")
            return

        for i, img_path in enumerate(image_paths):
            # 1. Get metadata
            photo_id = self._scan_metadata(img_path)

            # add current batch photo ids
            if photo_id:
                self.current_batch_ids.add(photo_id)

            # 2. Face detection
            if detect_faces:
                self.face_detector.process_photo(img_path, photo_id)

            if callback:
                callback(i/total_photos, i/total_photos)

        # 2. Face clustering
        if detect_faces:
            self.face_clustering.resolve_identities()

        # Keep if callbacks??
        if callback:
            callback(1.0, "Done!")

    def _scan_metadata(self, path):
        filename = path.name
        path_str = str(path)
        hash_val = self.compute_hash(path)
        time_data = PhotoMetadata.get_date(path)
        width, height = PhotoMetadata.get_size(path)
        location_data = PhotoMetadata.get_location(path)

        if location_data:
            location_data_city, location_data_country = location_data
        else:
            location_data_city, location_data_country = None, None

        # Check if photo with this hash exists to prevent duplication
        exists = self.photo_repo.get_by_hash(hash_val)

        if exists:
            self.photo_repo.update_photo(
                photo_id=exists["id"], path=path_str, filename=filename, location_data_city=location_data_city, location_data_country=location_data_country)
            return exists["id"]
        else:
            new_id = self.photo_repo.insert_photo(
                path=path_str, filename=filename, hash=hash_val,
                location_data_city=location_data_city, time_data=time_data,
                width=width, height=height, location_data_country=location_data_country)
            return new_id

    def get_person_thumbnail(self, person_id):
        rows = self.face_repo.get_faces_by_person_id(person_id)

        if not rows:
            return None

        biggest_area = -1
        biggest_face = None
        biggest_photo_path = None

        for row in rows:
            try:
                raw_coords = row["face_coords"]
                coords = None

                if isinstance(raw_coords, str):
                    coords = json.loads(raw_coords)
                    if isinstance(coords, str):
                        coords = json.loads(coords)
                else:
                    coords = raw_coords

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

        if biggest_face is None or biggest_photo_path is None:
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

    def export_photos(self, photos_list, base_target_folder):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        export_folder_name = f"Export_{timestamp}"

        final_target_folder = os.path.join(
            base_target_folder, export_folder_name)

        if not os.path.exists(final_target_folder):
            os.makedirs(final_target_folder)

        count = 0
        errors = 0

        for photo in photos_list:
            src = photo['path']
            filename = photo['filename']
            dst = os.path.join(final_target_folder, filename)

            # Prevent dupliacation
            if os.path.exists(dst):
                base, ext = os.path.splitext(filename)
                dst = os.path.join(final_target_folder,
                                   f"{base}_{photo['id']}{ext}")

            try:
                shutil.copy2(src, dst)
                count += 1
            except Exception as e:
                print(f"Error copying {src}: {e}")
                errors += 1

        return count, errors

    def compute_hash(self, path: Path) -> str:
        BUF_SIZE = 65536  # 64KB
        sha256 = hashlib.sha256()
        with open(path, "rb") as f:
            while chunk := f.read(BUF_SIZE):
                sha256.update(chunk)
        return sha256.hexdigest()

# =========================================================================
#  WRAPPER METODS FOR UI (app.py)
# =========================================================================

    def get_all_people(self, subset_ids=None):
        return self.person_repo.get_all_with_faces(subset_ids)

    def update_person_name(self, person_id, new_name):
        self.person_repo.update_name(person_id, new_name)

    def get_photos_from_repo_for_gallery(self):
        photos = self.photo_repo.get_photos(self.criteria)
        return photos

    def load_location_tree(self, subset_ids=None):
        return self.photo_repo.get_unique_locations(subset_ids)
