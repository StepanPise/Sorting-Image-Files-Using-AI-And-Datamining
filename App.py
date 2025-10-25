from pathlib import Path
import customtkinter as ctk
from tkinter import filedialog

from db_setup import Database
from metadata_handle import PhotoMetadata
import face_recognition

db = Database()

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("400x200")
app.title("Select Directory")

selected_folder = ctk.StringVar()


def choose_folder():
    folder = filedialog.askdirectory(title="Choose a folder")
    if folder:
        selected_folder.set(folder)
        input_folder = Path(folder)
        get_photos_metadata(input_folder)

        # presunout do vlastni classy/metody
        for img_path in input_folder.iterdir():
            if img_path.is_file() and img_path.suffix.lower() in [".jpg", ".jpeg", ".png"]:
                try:
                    image = face_recognition.load_image_file(img_path)
                    locations = face_recognition.face_locations(  # proved detekci obliceju na fotce
                        image, model="hog")
                    print(f"{img_path.name}: Face found:", locations)

                    if locations:
                        row = db.cursor.execute("SELECT id FROM photos WHERE filename = ?", (
                            img_path.name,)).fetchone()  # Beru si id fotky z db
                        if row:
                            photo_id = row[0]
                            # pro kazdy oblicej vytvor embedding
                            face_encodings = face_recognition.face_encodings(
                                image, locations)
                            # vloz do db v bitstream formatu
                            for encoding in face_encodings:
                                db.insert_face(
                                    photo_id, encoding.tobytes(), None)
                except Exception as e:
                    print(
                        f"Error -> Image couldnt be analyzed: {img_path.name}: {e}")


def get_photos_metadata(input_folder: Path):
    for path in input_folder.iterdir():
        if path.is_file() and path.suffix.lower() in [".jpg", ".jpeg", ".png"]:
            filename = path.name
            path_str = str(path)

            time_data = PhotoMetadata.get_date(path)
            location_data = PhotoMetadata.get_location(path)
            width, height = PhotoMetadata.get_size(path)

            db.insert_photo(
                path=path_str,
                filename=filename,
                location_data=location_data,
                time_data=time_data,
                width=width,
                height=height
            )


ctk.CTkButton(app, text="Select folder", command=choose_folder).pack(pady=40)
ctk.CTkLabel(app, textvariable=selected_folder, text_color="lightblue").pack()

if __name__ == "__main__":
    app.mainloop()
    db.close()
