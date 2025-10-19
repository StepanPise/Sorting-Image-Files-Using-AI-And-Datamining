import sqlite3
from pathlib import Path
import customtkinter as ctk
from tkinter import filedialog
import exifread
from geopy.geocoders import Nominatim
from PIL import Image

from db_setup import Database

db = Database()

# geolocator
geolocator = Nominatim(user_agent="photo_sorter")

# --- Metadata functions ---


def get_photo_date(img_path):
    with open(img_path, 'rb') as f:
        tags = exifread.process_file(
            f, stop_tag="EXIF DateTimeOriginal", details=False)
    date_tag = tags.get("EXIF DateTimeOriginal")
    return str(date_tag) if date_tag else None


def get_photo_location(img_path):
    with open(img_path, 'rb') as f:
        tags = exifread.process_file(f, details=False)

    gps_lat = tags.get("GPS GPSLatitude")
    gps_lat_ref = tags.get("GPS GPSLatitudeRef")
    gps_lon = tags.get("GPS GPSLongitude")
    gps_lon_ref = tags.get("GPS GPSLongitudeRef")

    if not (gps_lat and gps_lat_ref and gps_lon and gps_lon_ref):
        return None

    def convert_to_degrees(value):
        d, m, s = [float(x.num)/float(x.den) for x in value.values]
        return d + m/60 + s/3600

    lat = convert_to_degrees(gps_lat)
    lon = convert_to_degrees(gps_lon)
    if gps_lat_ref.values[0] != 'N':
        lat = -lat
    if gps_lon_ref.values[0] != 'E':
        lon = -lon

    try:
        location = geolocator.reverse((lat, lon), language="cs")
        if location and location.raw.get("address"):
            city = location.raw["address"].get("city") or \
                location.raw["address"].get("town") or \
                location.raw["address"].get("village")
            return city
        return None
    except:
        return None


def get_photo_size(img_path):
    try:
        with Image.open(img_path) as img:
            return img.width, img.height
    except:
        return None, None


# --- GUI setup ---
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


def get_photos_metadata(input_folder):
    for path in input_folder.iterdir():
        if path.is_file() and path.suffix.lower() in [".jpg", ".jpeg", ".png"]:
            filename = path.name
            path_str = str(path)
            time_data = get_photo_date(path)
            location_data = get_photo_location(path)
            width, height = get_photo_size(path)

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

app.mainloop()

db.close()
