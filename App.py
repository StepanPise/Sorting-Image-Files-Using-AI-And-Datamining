from pathlib import Path
import customtkinter as ctk
from tkinter import filedialog

from db_setup import Database
from metadata_handle import PhotoMetadata
import face_recognition

import numpy as np
from sklearn.cluster import DBSCAN
import cv2

import hashlib


db = Database()

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("400x400")
app.title("Select Directory")

selected_folder = ctk.StringVar()


def choose_folder():
    folder = filedialog.askdirectory(title="Choose a folder")
    if folder:
        selected_folder.set(folder)
        input_folder = Path(folder)

        get_photos_metadata(input_folder)

        process_faces(input_folder)
        assign_person_ids()

        print_person_groups()


def get_photos_metadata(input_folder: Path):
    for path in input_folder.iterdir():
        if path.is_file() and path.suffix.lower() in [".jpg", ".jpeg", ".png"]:

            filename = path.name
            path_str = str(path)
            hash = compute_hash(path)
            time_data = PhotoMetadata.get_date(path)
            location_data = PhotoMetadata.get_location(path)
            width, height = PhotoMetadata.get_size(path)

            exists = db.cursor.execute(
                "SELECT id FROM photos WHERE hash = ?", (hash,)
            ).fetchone()

            if exists:
                db.update_photo(
                    photo_id=exists[0],
                    path=path_str,
                    filename=filename,
                )
                continue

            db.insert_photo(
                path=path_str,
                filename=filename,
                hash=hash,
                location_data=location_data,
                time_data=time_data,
                width=width,
                height=height
            )


def process_faces(input_folder: Path):
    for img_path in input_folder.iterdir():
        if img_path.is_file() and img_path.suffix.lower() in [".jpg", ".jpeg", ".png"]:

            file_hash = compute_hash(img_path)

            row = db.cursor.execute(
                "SELECT id, already_analyzed FROM photos WHERE hash = ?", (
                    file_hash,)
            ).fetchone()
            if not row:
                continue

            photo_id, already_analyzed = row

            if already_analyzed:
                continue

            try:
                image = face_recognition.load_image_file(img_path)

                scale = 0.25
                small_img = cv2.resize(image, (0, 0), fx=scale, fy=scale)

                face_locations = face_recognition.face_locations(
                    small_img, model="hog")

                # Scale back up face locations
                face_locations = [
                    [int(top / scale), int(right / scale),
                     int(bottom / scale), int(left / scale)]
                    for top, right, bottom, left in face_locations
                ]

                print(f"{img_path.name}: Face found:", face_locations)

                if face_locations:
                    face_encodings = face_recognition.face_encodings(
                        image, face_locations)
                    for encoding in face_encodings:
                        db.insert_face(photo_id, encoding.tobytes(), None)

                db.cursor.execute(
                    "UPDATE photos SET already_analyzed = 1 WHERE id = ?", (
                        photo_id,)
                )
                db.conn.commit()

            except Exception as e:
                print(
                    f"Error -> Image couldnt be analyzed: {img_path.name}: {e}")


def assign_person_ids():
    rows = db.cursor.execute("SELECT id, embedding FROM faces").fetchall()
    if not rows:
        print("No faces in database.")
        return

    face_ids = []
    embeddings = []

    for row in rows:
        face_id = row[0]
        embedding_bytes = row[1]
        embedding = np.frombuffer(embedding_bytes, dtype=np.float64)
        face_ids.append(face_id)
        embeddings.append(embedding)

    embeddings_array = np.array(embeddings)  # make matrix
    clustering = DBSCAN(metric='euclidean', eps=0.5,
                        min_samples=1).fit(embeddings_array)
    labels = clustering.labels_
    unique_labels = np.unique(clustering.labels_)

    # load existing people avg embeddings
    people_rows = db.get_people()
    people_avg_embeddings = {}
    for person_id, name, avg_bytes in people_rows:
        if avg_bytes:
            people_avg_embeddings[person_id] = np.frombuffer(
                avg_bytes, dtype=np.float64)
        else:
            people_avg_embeddings[person_id] = None

    label_to_person_id = {}
    next_person_index = len(people_rows)
    for label in unique_labels:
        cluster_indices = [i for i, l in enumerate(labels) if l == label]
        cluster_embeddings = embeddings_array[cluster_indices]
        cluster_avg = np.mean(cluster_embeddings, axis=0)

        # match existing people
        matched_person_id = None
        for person_id, avg_emb in people_avg_embeddings.items():
            if avg_emb is not None:
                dist = np.linalg.norm(cluster_avg - avg_emb)
                if dist < 0.5:
                    matched_person_id = person_id
                    break

        if matched_person_id is not None:
            person_id = matched_person_id
            all_embeddings = np.vstack(
                [cluster_embeddings, people_avg_embeddings[person_id].reshape(1, -1)])
            new_avg = np.mean(all_embeddings, axis=0)
            db.cursor.execute(
                "UPDATE people SET avg_embedding = ? WHERE id = ?",
                (new_avg.tobytes(), person_id)
            )
            people_avg_embeddings[person_id] = new_avg
        else:
            person_name = f"Person{next_person_index}"
            avg_bytes = cluster_avg.tobytes() if cluster_avg is not None else None
            db.insert_person(name=person_name, avg_embedding=avg_bytes)
            person_id = db.cursor.lastrowid
            people_avg_embeddings[person_id] = cluster_avg
            next_person_index += 1

        label_to_person_id[label] = person_id

    # update face records with person_ids
    for face_id, label in zip(face_ids, labels):
        person_id = label_to_person_id[label]
        db.cursor.execute(
            "UPDATE faces SET person_id = ? WHERE id = ?", (person_id, face_id)
        )

    db.conn.commit()
    print(
        f"Assigned person_id to {len(face_ids)} faces and created {len(unique_labels)} people.")


def print_person_groups():  # for debugging purposes

    rows = db.cursor.execute(
        "SELECT id, photo_id, person_id FROM faces").fetchall()

    from collections import defaultdict
    groups = defaultdict(list)

    for face_id, photo_id, person_id in rows:
        groups[person_id].append(photo_id)

    for person_id, photos in groups.items():
        unique_photos = list(set(photos))
        print(f"Person {person_id} appears in photos: {unique_photos}")


ctk.CTkButton(app, text="Select folder", command=choose_folder).pack(pady=40)
ctk.CTkLabel(app, textvariable=selected_folder, text_color="lightblue").pack()

scroll_frame = ctk.CTkScrollableFrame(app, label_text="Detected people")
scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)


# Hash verification prevents processing the same image even if its in diff folder
def compute_hash(path: Path) -> str:
    BUF_SIZE = 65536  # 64KB
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(BUF_SIZE):
            sha256.update(chunk)
    return sha256.hexdigest()


if __name__ == "__main__":
    app.mainloop()
    db.close()
