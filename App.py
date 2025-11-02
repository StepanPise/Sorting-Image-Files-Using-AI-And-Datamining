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
from face_clustering import assign_person_ids

from PIL import Image, ImageTk, ImageOps
import tkinter as tk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("400x400")
app.title("Select Directory")

selected_folder = ctk.StringVar()

db = Database()


def choose_folder():
    folder = filedialog.askdirectory(title="Choose a folder")
    if folder:
        selected_folder.set(folder)
        input_folder = Path(folder)

        get_photos_metadata(input_folder)

        process_faces(input_folder)

        assign_person_ids()

        show_detected_people()

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


def show_detected_people():
    for widget in scroll_frame.winfo_children():
        widget.destroy()

    sc_items = db.cursor.execute("""
        SELECT p.id, ph.path, p.name
        FROM people p
        JOIN faces f ON f.person_id = p.id
        JOIN photos ph ON ph.id = f.photo_id
        GROUP BY p.id, p.name
        ORDER BY p.name
    """).fetchall()

    for person_id, img_path, person_name in sc_items:
        try:
            img = Image.open(img_path)
            img = ImageOps.exif_transpose(img)
            img = img.resize((100, 100), Image.LANCZOS)
            img_ctk = ctk.CTkImage(
                light_image=img, dark_image=img, size=(80, 80))
        except Exception as e:
            print(f"Thumbnail Error: {img_path}")
            continue

        item_frame = ctk.CTkFrame(
            scroll_frame, fg_color="#222", corner_radius=8)
        item_frame.pack(fill="x", padx=5, pady=5)

        img_label = ctk.CTkLabel(item_frame, image=img_ctk, text="")
        img_label.image = img_ctk
        img_label.pack(side="left", padx=5)

        name_entry = ctk.CTkEntry(
            item_frame, width=100, placeholder_text=person_name)
        name_entry.pack(side="left", padx=10, fill="x", expand=True)

        def save_name(event=None, pid=person_id, entry=name_entry):
            new_name = entry.get().strip()
            if new_name:
                db.cursor.execute(
                    "UPDATE people SET name = ? WHERE id = ?", (new_name, pid))
                db.conn.commit()

        name_entry.bind("<Return>", save_name)

        save_btn = ctk.CTkButton(
            item_frame, text="💾", width=40,
            command=lambda pid=person_id, entry=name_entry: save_name(
                pid=pid, entry=entry)
        )
        save_btn.pack(side="left", padx=5)


ctk.CTkButton(app, text="Select folder", command=choose_folder).pack(pady=40)
ctk.CTkLabel(app, textvariable=selected_folder, text_color="lightblue").pack()

scroll_frame = ctk.CTkScrollableFrame(app, label_text="Detected people")
scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

show_detected_people()


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
