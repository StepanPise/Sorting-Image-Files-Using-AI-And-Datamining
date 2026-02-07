from PIL import Image
import exifread
from geopy.geocoders import Nominatim
from typing import Optional, Tuple

geolocator = Nominatim(user_agent="photo_sorter")


class PhotoMetadata:

    @staticmethod
    def get_date(img_path: str) -> Optional[str]:
        with open(img_path, 'rb') as f:
            tags = exifread.process_file(
                f, stop_tag="EXIF DateTimeOriginal", details=False)
        date_tag = tags.get("EXIF DateTimeOriginal")
        return str(date_tag) if date_tag else None

    @staticmethod
    def get_location(img_path: str) -> Optional[str]:
        with open(img_path, 'rb') as f:
            tags = exifread.process_file(f, details=False)

        gps_lat = tags.get("GPS GPSLatitude")
        gps_lat_ref = tags.get("GPS GPSLatitudeRef")
        gps_lon = tags.get("GPS GPSLongitude")
        gps_lon_ref = tags.get("GPS GPSLongitudeRef")

        if not (gps_lat and gps_lat_ref and gps_lon and gps_lon_ref):
            return None, None

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

                country = location.raw["address"].get("country")

                return city, country
            return None, None
        except:
            return print("Couldnt detect location data, No Internet! (Try again when connected to Internet)")

    @staticmethod
    def get_size(img_path: str) -> Tuple[Optional[int], Optional[int]]:
        try:
            with Image.open(img_path) as img:
                return img.width, img.height
        except:
            return None, None
