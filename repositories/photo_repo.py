from .base_repo import BaseRepository
from structures import FilterCriteria


class PhotoRepository(BaseRepository):

    def get_all(self):
        self.cursor.execute("SELECT * FROM photos")
        return self.cursor.fetchall()

    def get_by_hash(self, hash_val):
        self.cursor.execute(
            "SELECT * FROM photos WHERE hash = %s", (hash_val,))
        return self.cursor.fetchone()

    def insert_photo(self, **kwargs):
        self.cursor.execute(
            """
            INSERT INTO photos (path, filename, hash, location_data_city, time_data, width, height, location_data_country)
            VALUES (%s, %s, %s, %s, %s, %s, %s,%s)
            """,
            (kwargs["path"], kwargs["filename"], kwargs["hash"], kwargs["location_data_city"],
             kwargs["time_data"], kwargs["width"], kwargs["height"], kwargs["location_data_country"])
        )
        self.conn.commit()

    def update_photo(self, photo_id, **kwargs):

        location_data_city = kwargs.get("location_data_city")

        if (location_data_city != None):
            self.cursor.execute(
                "UPDATE photos SET path=%s, filename=%s, location_data_city=%s,location_data_country=%s  WHERE id=%s",
                (kwargs["path"], kwargs["filename"],
                 kwargs["location_data_city"], kwargs["location_data_country"], photo_id)
            )
        else:
            self.cursor.execute(
                "UPDATE photos SET path=%s, filename=%s WHERE id=%s",
                (kwargs["path"], kwargs["filename"], photo_id)
            )

        self.conn.commit()

    def mark_analyzed(self, photo_id):
        self.cursor.execute(
            "UPDATE photos SET already_analyzed = 1 WHERE id = %s",
            (photo_id,)
        )
        self.conn.commit()

    def get_photos(self, criteria: FilterCriteria):

        query = "SELECT DISTINCT p.* FROM photos p"
        params = []
        joins = []
        conditions = []

        if criteria.person_ids:
            joins.append("JOIN faces f ON p.id = f.photo_id")
            placeholders = ",".join(["%s"] * len(criteria.person_ids))
            conditions.append(f"f.person_id IN ({placeholders})")
            params.extend(criteria.person_ids)

        if criteria.country:
            placeholders = ",".join(["%s"] * len(criteria.country))
            conditions.append(f"p.location_data_country IN ({placeholders})")
            params.extend(criteria.country)

        if criteria.city:
            placeholders = ",".join(["%s"] * len(criteria.city))
            conditions.append(f"p.location_data_city IN ({placeholders})")
            params.extend(criteria.city)

        if criteria.date_from:
            conditions.append("p.time_data >= %s")
            params.append(criteria.date_from)

        if criteria.date_to:
            conditions.append("p.time_data <= %s")
            params.append(criteria.date_to)

        if joins:
            query += " " + " ".join(joins)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY p.time_data DESC"

        self.cursor.execute(query, params)

        return self.cursor.fetchall()

    def get_unique_locations(self):
        """
        RETURN example: { "Česko": ["Praha", "Brno"], "Německo": ["Berlín"] }
        """

        self.cursor.execute("""
                SELECT DISTINCT location_data_country, location_data_city 
                FROM photos 
                WHERE (location_data_country IS NOT NULL)
                ORDER BY location_data_country ASC, location_data_city ASC
            """)

        rows = self.cursor.fetchall()

        tree = {}

        for row in rows:

            country = row['location_data_country']
            city = row['location_data_city']

            # If country is not in the tree, add it with an empty list
            if country not in tree:
                tree[country] = []

            # If city is not already in the list for this country, add it
            if city and city not in tree[country]:
                tree[country].append(city)

        return tree
