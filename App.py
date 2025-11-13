from pathlib import Path
import customtkinter as ctk
from tkinter import filedialog

from db_setup import Database
from metadata_handle import PhotoMetadata
from PIL import Image, ImageOps, ImageDraw
import json
import time

from face_clustering import assign_person_ids
from face_detection import process_faces, compute_hash


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

db = Database()

app = ctk.CTk()
app.geometry("400x400")
app.title("Select Directory")
selected_folder = ctk.StringVar()


def choose_folder():
    folder = filedialog.askdirectory(title="Choose a folder")
    if folder:
        selected_folder.set(folder)
        analyze_selected_folder(Path(folder))


def analyze_selected_folder(input_folder):

    get_photos_metadata(input_folder)

    print("Starting TIMER...")
    start = time.perf_counter()

    process_faces(input_folder)

    assign_person_ids()

    show_detected_people()

    print_person_groups()
    finish = time.perf_counter()
    print(f"Processing completed in {finish - start:.2f} seconds.")


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


def _crop_image(img: Image.Image, person_id: int):
    coords = db.cursor.execute(
        "select face_coords from faces where person_id = ? limit 1", (person_id,)).fetchone()

    coords_str = coords[0]  # string
    # list now [[111,111,111,111]]
    coords_list = json.loads(json.loads(coords_str))

    # convert to int
    left, top, right, bottom = [int(x) for x in coords_list[0]]

    margin = 30
    top = max(0, top - margin)
    left = max(0, left - margin)
    bottom = min(img.height, bottom + margin)
    right = min(img.width, right + margin)

    cropped = img.crop((left, top, right, bottom))
    return cropped


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
            img = _crop_image(img, person_id)

            img = ImageOps.exif_transpose(img)
            img = img.resize((60, 60), Image.LANCZOS)

            # circular mask
            mask = Image.new("L", img.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0) + img.size, fill=255)
            img.putalpha(mask)

            img_ctk = ctk.CTkImage(
                light_image=img, dark_image=img, size=(60, 60))

        except Exception as e:
            print(f"Thumbnail Error: {img_path} -> {e}")
            continue

        item_frame = ctk.CTkFrame(
            scroll_frame, fg_color="#222", corner_radius=8)
        item_frame.pack(fill="x", padx=5, pady=5)

        img_label = ctk.CTkLabel(
            item_frame, image=img_ctk, text="", width=60, height=60)
        img_label.image = img_ctk
        img_label.pack(side="left", padx=5, pady=5)

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


if __name__ == "__main__":
    app.mainloop()
    db.close()
