from pathlib import Path
import json
import hashlib
import cv2
import torch
from retinaface import RetinaFace
from facenet_pytorch import InceptionResnetV1
import torchvision.transforms as transforms

import concurrent.futures


class FaceDetection:

    def __init__(self, photo_repo, face_repo):
        self.photo_repo = photo_repo
        self.face_repo = face_repo
        self.resnet = InceptionResnetV1(pretrained='vggface2').eval()

    def process_faces(self, input_folder: Path):
        image_paths = [
            p for p in input_folder.iterdir()
            if p.is_file() and p.suffix.lower() in [".jpg", ".jpeg", ".png"]
        ]

        # with concurrent.futures.ProcessPoolExecutor() as executor:
        #     executor.map(process_photo, image_paths)

        # with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        #     list(executor.map(process_photo, image_paths))

        for img_path in image_paths:
            self.process_photo(img_path)

    def analyze_image(self, img_path: Path):
        image = cv2.imread(str(img_path))
        if image is None:
            raise ValueError("Image could not be read")

        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        faces = RetinaFace.detect_faces(str(img_path))
        print(f"{img_path.name}: Detected faces = {faces}")

        return rgb_image, faces

    def process_photo(self, img_path: Path):
        file_hash = self.compute_hash(img_path)

        row = self.photo_repo.get_by_hash(file_hash)

        if not row:
            print(f"{img_path.name}: Photo not found in DB, skipping.")
            return

        photo_id = row["id"]
        already_analyzed = row["already_analyzed"]

        if already_analyzed:
            print(f"{img_path.name}: Already analyzed, skipping.")
            return

        try:
            rgb_image, faces = self.analyze_image(img_path)

            if not faces:
                print(f"{img_path.name}: No faces found")
                self.photo_repo.mark_analyzed(photo_id)
                return

            print(f"{img_path.name}: Faces found: {list(faces.keys())}")

            for key, face in faces.items():
                x1, y1, x2, y2 = face["facial_area"]
                face_img = rgb_image[y1:y2, x1:x2]
                face_coords = json.dumps(
                    [[int(x1), int(y1), int(x2), int(y2)]])
                face_encoding = self.compute_embedding(face_img)

                self.face_repo.add(
                    photo_id, face_encoding.tobytes(), face_coords)

            self.photo_repo.mark_analyzed(photo_id)

        except Exception as e:
            print(f"Error -> Image couldn't be analyzed: {img_path.name}: {e}")

    # Hash verification prevents processing the same image even if its in diff folder

    def compute_hash(self, path: Path) -> str:

        BUF_SIZE = 65536  # 64KB
        sha256 = hashlib.sha256()
        with open(path, "rb") as f:
            while chunk := f.read(BUF_SIZE):
                sha256.update(chunk)
        return sha256.hexdigest()

    def compute_embedding(self, face_img):
        """
        face_img = RGB numpy array
        """
        import torchvision.transforms as transforms
        transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((160, 160)),
            transforms.ToTensor(),
            transforms.Normalize([0.5], [0.5])
        ])
        face_tensor = transform(face_img).unsqueeze(0)  # [1,3,160,160]
        with torch.no_grad():
            embedding = resnet(face_tensor)  # [1,512]
        return embedding.squeeze(0).numpy()  # 512-dim vector
