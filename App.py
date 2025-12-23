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


ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

db = Database()

app = ctk.CTk()
app.geometry("400x400")
app.title("Select Directory")
selected_folder = ctk.StringVar()

detect_faces_enabled = True


def choose_folder():
    folder = filedialog.askdirectory(title="Choose a folder")
    if folder:
        selected_folder.set(folder)
        analyze_selected_folder(Path(folder))


def analyze_selected_folder(input_folder):

    get_photos_metadata(input_folder)

    print("Starting TIMER...")
    start = time.perf_counter()

    if detect_faces_enabled:
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

            db.cursor.execute(
                "SELECT id FROM photos WHERE hash = %s", (hash,)
            )
            exists = db.cursor.fetchone()
            if exists is not None:
                db.update_photo(
                    photo_id=exists["id"],
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

    db.cursor.execute("SELECT id, photo_id, person_id FROM faces")
    rows = db.cursor.fetchall()

    from collections import defaultdict
    groups = defaultdict(list)

    for row in rows:
        face_id = row["id"]
        photo_id = row["photo_id"]
        person_id = row["person_id"]
        groups[person_id].append(photo_id)

    for person_id, photos in groups.items():
        unique_photos = list(set(photos))
        print(f"Person {person_id} appears in photos: {unique_photos}")


def _crop_image(person_id: int) -> Image.Image:

    db.cursor.execute(
        """
        SELECT f.face_coords, p.path
        FROM faces f
        JOIN photos p ON p.id = f.photo_id
        WHERE f.person_id = %s
        """,
        (person_id,)
    )

    rows = db.cursor.fetchall()

    if not rows:
        return None

    biggest_area = -1
    biggest_face = None
    biggest_photo_path = None

    for row in rows:
        try:
            coords = json.loads(json.loads(row["face_coords"]))
        except Exception:
            continue

        if not coords:
            continue

        left, top, right, bottom = coords[0]
        area = (right - left) * (bottom - top)

        if area > biggest_area:
            biggest_area = area
            biggest_face = (left, top, right, bottom)
            biggest_photo_path = row["path"]

    if biggest_face is None or biggest_photo_path is None:
        return None

    try:
        image = Image.open(biggest_photo_path)
    except Exception:
        return None

    left, top, right, bottom = biggest_face
    MARGIN = 30
    top = max(0, top - MARGIN)
    left = max(0, left - MARGIN)
    bottom = min(image.height, bottom + MARGIN)
    right = min(image.width, right + MARGIN)

    return image.crop((left, top, right, bottom))


def show_detected_people():
    # clear scroll frame
    for widget in scroll_frame.winfo_children():
        widget.destroy()

    # load people ids
    db.cursor.execute("""
        SELECT p.id, p.name
        FROM people p
        JOIN faces f ON f.person_id = p.id
        JOIN photos ph ON ph.id = f.photo_id
        GROUP BY p.id, p.name
        ORDER BY p.name;
    """)
    sc_items = db.cursor.fetchall()

    for row in sc_items:
        person_id = row['id']
        person_name = row['name']

        img = None
        try:
            img = _crop_image(person_id)
            if img is None:
                continue

            img = ImageOps.exif_transpose(img)
            img = img.resize((60, 60), Image.LANCZOS)

            # circular mask
            mask = Image.new("L", img.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0) + img.size, fill=255)
            img.putalpha(mask)

            img_ctk = ctk.CTkImage(
                light_image=img, dark_image=img, size=(60, 60)
            )

        except Exception as e:
            print(f"Thumbnail Error for person {person_id}: {e}")
            continue

        # UI
        # item in scrollframe
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
                    "UPDATE people SET name = %s WHERE id = %s", (
                        new_name, pid)
                )
                db.conn.commit()

        name_entry.bind("<Return>", save_name)

        save_btn = ctk.CTkButton(
            item_frame, text="💾", width=40,
            command=lambda pid=person_id, entry=name_entry: save_name(
                pid=pid, entry=entry)
        )
        save_btn.pack(side="left", padx=5)


def on_switch_toggle():
    global detect_faces_enabled
    detect_faces_enabled = bool(show_switch.get())


top_row = ctk.CTkFrame(app)
top_row.pack(pady=20)

select_btn = ctk.CTkButton(
    top_row, text="Select folder", command=choose_folder)
select_btn.pack(side="left", padx=10)

show_switch = ctk.CTkSwitch(
    top_row,
    text="Detect faces",
    command=on_switch_toggle
)
show_switch.pack(side="left", padx=10)

ctk.CTkLabel(app, textvariable=selected_folder, text_color="lightblue").pack()


scroll_frame = ctk.CTkScrollableFrame(
    app, label_text="Detected people")
scroll_frame.pack(fill="both", expand=False, padx=10, pady=10)

process_btn = ctk.CTkButton(app, text="Export photos")
process_btn.pack(pady=10)

show_detected_people()


if __name__ == "__main__":
    app.mainloop()
    db.close()
