import customtkinter as ctk
from tkcalendar import Calendar


class MetadataSidebar(ctk.CTkFrame):
    def __init__(self, master, controller, **kwargs):
        super().__init__(master, **kwargs)
        self.controller = controller

        self.scroll_frame_metadata = ctk.CTkScrollableFrame(
            self, label_text="Sort by Metadata"
        )

        self.scroll_frame_metadata.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.scroll_frame_metadata.grid_columnconfigure(0, weight=1)

        self.combo_countries = ctk.CTkComboBox(
            self.scroll_frame_metadata, command=self.country_changed)

        self.combo_countries.grid(
            row=0, column=0, padx=10, pady=10, sticky="ew")

        self.combo_cities = ctk.CTkComboBox(
            self.scroll_frame_metadata)
        self.combo_cities.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.prepare_locations()

    # load_location_tree() return example: { "Česko": ["Praha", "Brno"], "Německo": ["Berlín"] }

    def prepare_locations(self):
        """
        call with init only
        """
        self.locations_data = self.controller.load_location_tree()

        countries = list(self.locations_data.keys())
        self.combo_countries.configure(values=countries)

        if countries:
            first_country = countries[0]
            self.combo_countries.set(first_country)
            self.country_changed(first_country)
        else:
            self.combo_countries.set("No data")
            self.combo_cities.configure(values=[])

    def country_changed(self, selected_country):
        cities = self.locations_data.get(selected_country, [])

        self.combo_cities.configure(values=cities)

        if cities:
            self.combo_cities.set(cities[0])
        else:
            self.combo_cities.set("-")
