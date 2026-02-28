from pathlib import Path
import json
import cv2
import numpy as np
from insightface.app import FaceAnalysis


class FaceDetection:

    def __init__(self, photo_repo, face_repo):
        self.photo_repo = photo_repo
        self.face_repo = face_repo
        self._load_models()

    def process_photo(self, img_path: Path, photo_id: int) -> None:
        row = self.photo_repo.get_by_id(photo_id)

        # Check if photo exists in DB (not redundant)
        if row is None:
            print(
                f"Error: Photo with ID {photo_id} ({img_path.name}) was not found in DB. Skipping.")
            return
        # Check if photo has already been analyzed to prevent redundant processing
        if row.get("already_analyzed"):
            print(f"{img_path.name}: Already analyzed, skipping.")
            return

        try:
            rgb_image, faces = self._analyze_image(img_path)

            if faces:
                print(f"{img_path.name}: Faces found: {len(faces)}")
                self._extract_and_save_faces(photo_id, rgb_image, faces)
            else:
                print(f"{img_path.name}: No faces found")

            self.photo_repo.mark_analyzed(photo_id)

        except Exception as e:
            print(f"Error -> Image couldn't be analyzed: {img_path.name}: {e}")

    def _extract_and_save_faces(self, photo_id: int, rgb_image: np.ndarray, faces: list) -> None:

        img_h, img_w, _ = rgb_image.shape

        for face in faces:
            x1, y1, x2, y2 = face.bbox.astype(int)

            x1, y1 = max(0, int(x1)), max(0, int(y1))
            x2, y2 = min(img_w, int(x2)), min(img_h, int(y2))

            if x2 <= x1 or y2 <= y1:
                continue

            face_coords = json.dumps([[x1, y1, x2, y2]])

            if face.normed_embedding is None:
                continue
            face_encoding = face.normed_embedding

            self.face_repo.add(photo_id, face_encoding.tobytes(), face_coords)

    def _analyze_image(self, img_path: Path):
        image = cv2.imread(str(img_path))
        if image is None:
            raise ValueError("Image could not be read")

        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        faces = self.face_app.get(image)

        print(f"{img_path.name}: Detected faces = {len(faces)}")

        return rgb_image, faces

    def _load_models(self) -> None:
        self.face_app = FaceAnalysis(
            name='buffalo_s', allowed_modules=['detection', 'recognition'])
        self.face_app.prepare(ctx_id=-1, det_size=(640, 640))
