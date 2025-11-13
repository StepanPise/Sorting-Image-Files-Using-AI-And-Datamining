from pathlib import Path
import json
import hashlib
import cv2
import torch
from retinaface import RetinaFace
from facenet_pytorch import InceptionResnetV1
from db_setup import Database
import torchvision.transforms as transforms


db = Database()
resnet = InceptionResnetV1(pretrained='vggface2').eval()


def process_faces(input_folder: Path):
    image_paths = [
        p for p in input_folder.iterdir()
        if p.is_file() and p.suffix.lower() in [".jpg", ".jpeg", ".png"]
    ]

    for img_path in image_paths:
        process_photo(img_path)


def analyze_image(img_path: Path):
    image = cv2.imread(str(img_path))
    if image is None:
        raise ValueError("Image could not be read")

    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    faces = RetinaFace.detect_faces(str(img_path))
    return rgb_image, faces


def process_photo(img_path: Path):
    file_hash = compute_hash(img_path)

    row = db.cursor.execute(
        "SELECT id, already_analyzed FROM photos WHERE hash = ?", (file_hash,)
    ).fetchone()
    if not row:
        return
    photo_id, already_analyzed = row
    if already_analyzed:
        return

    try:
        rgb_image, faces = analyze_image(img_path)

        if not faces:
            print(f"{img_path.name}: No faces found")
            db.cursor.execute(
                "UPDATE photos SET already_analyzed = 1 WHERE id = ?", (
                    photo_id,)
            )
            db.conn.commit()
            return

        print(f"{img_path.name}: Face found: {list(faces.keys())}")

        for key, face in faces.items():
            x1, y1, x2, y2 = face["facial_area"]
            face_img = rgb_image[y1:y2, x1:x2]
            face_coords = json.dumps([[int(x1), int(y1), int(x2), int(y2)]])
            face_encoding = compute_embedding(face_img)

            db.insert_face(photo_id, face_encoding.tobytes(),
                           face_coords, None)

        db.cursor.execute(
            "UPDATE photos SET already_analyzed = 1 WHERE id = ?", (photo_id,)
        )
        db.conn.commit()

    except Exception as e:
        print(f"Error -> Image couldn't be analyzed: {img_path.name}: {e}")


# Hash verification prevents processing the same image even if its in diff folder
def compute_hash(path: Path) -> str:

    BUF_SIZE = 65536  # 64KB
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(BUF_SIZE):
            sha256.update(chunk)
    return sha256.hexdigest()


def compute_embedding(face_img):
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
