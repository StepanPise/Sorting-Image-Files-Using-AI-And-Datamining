import customtkinter as ctk


class LocationSidebar(ctk.CTkFrame):

    def __init__(self, master, controller, callback, **kwargs):
        super().__init__(master, **kwargs)
        self.controller = controller
        self.callback = callback

        self.locations_data = {}
        # dicts for checkboxes
        self.country_checkboxes = {}
        self.city_checkboxes = {}

        self.grid_columnconfigure(0, weight=1)

        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(4, weight=1)

        self.lbl_title = ctk.CTkLabel(
            self, text="Filter by Location")
        self.lbl_title.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

        self.lbl_country = ctk.CTkLabel(
            self, text="Countries:")
        self.lbl_country.grid(row=1, column=0, padx=10,
                              pady=(5, 0), sticky="w")

        self.scroll_countries = ctk.CTkScrollableFrame(
            self, height=150, label_text="Country list")
        self.scroll_countries.grid(
            row=2, column=0, padx=5, pady=5, sticky="ew")

        self.scroll_countries.grid_columnconfigure(0, weight=1)

        self.lbl_city = ctk.CTkLabel(
            self, text="Cities:")
        self.lbl_city.grid(row=3, column=0, padx=10, pady=(15, 0), sticky="w")

        self.scroll_cities = ctk.CTkScrollableFrame(
            self, label_text="City list")
        self.scroll_cities.grid(row=4, column=0, padx=5,
                                pady=5, sticky="nsew")

        self.scroll_cities.grid_columnconfigure(0, weight=1)

        self.lbl_info = ctk.CTkLabel(
            self.scroll_cities, text="Select a country first", text_color="gray")
        self.lbl_info.grid(row=0, column=0, pady=20)

        self.prepare_locations()

    # load_location_tree() return example: { "Česko": ["Praha", "Brno"], "Německo": ["Berlín"] }

    def prepare_locations(self):
        '''RUN ONCE on init = loads data and prepares country checkboxes'''
        self.locations_data = self.controller.load_location_tree()
        sorted_countries = sorted(list(self.locations_data.keys()))

        for widget in self.scroll_countries.winfo_children():
            widget.destroy()
        self.country_checkboxes.clear()

        if not sorted_countries:
            label = ctk.CTkLabel(self.scroll_countries, text="No data")
            label.grid(row=0, column=0, sticky="ew")
            return

        for i, country in enumerate(sorted_countries):
            check = ctk.CTkCheckBox(
                self.scroll_countries,
                text=country,
                command=self.on_country_change
            )
            check.grid(row=i, column=0, sticky="w", pady=2, padx=5)

            self.country_checkboxes[country] = check

    def on_country_change(self):
        # load checkboxes
        previously_selected = set()
        for city_name, check in self.city_checkboxes.items():
            if check.get() == 1:
                previously_selected.add(city_name)
        active_countries = []
        for country_name, check in self.country_checkboxes.items():
            if check.get() == 1:
                active_countries.append(country_name)

        # cleanup
        for widget in self.scroll_cities.winfo_children():
            widget.destroy()
        self.city_checkboxes.clear()
        if not active_countries:
            label = ctk.CTkLabel(
                self.scroll_cities, text="Select a country first", text_color="gray")
            label.grid(row=0, column=0, pady=20)
            self.trigger_filter()
            return

        new_cities = []
        for country in active_countries:
            cities = self.locations_data.get(country, [])
            new_cities.extend(cities)

        new_cities = sorted(list(set(new_cities)))

        if not new_cities:
            label = ctk.CTkLabel(self.scroll_cities, text="No cities found")
            label.grid(row=0, column=0, pady=10)

        for i, city_name in enumerate(new_cities):
            check = ctk.CTkCheckBox(
                self.scroll_cities,
                text=city_name,
                command=self.trigger_filter
            )
            check.grid(row=i, column=0, sticky="w", pady=2, padx=5)

            if city_name in previously_selected:
                check.select()

            self.city_checkboxes[city_name] = check
        self.trigger_filter()

    def trigger_filter(self):
        selected_countries = []
        for name, check in self.country_checkboxes.items():
            if check.get() == 1:
                selected_countries.append(name)

        selected_cities = []
        for name, check in self.city_checkboxes.items():
            if check.get() == 1:
                selected_cities.append(name)

        self.callback(selected_countries, selected_cities)

    def reset_filter(self):
        for check in self.country_checkboxes.values():
            check.deselect()
        for check in self.city_checkboxes.values():
            check.deselect()
        self.trigger_filter()
