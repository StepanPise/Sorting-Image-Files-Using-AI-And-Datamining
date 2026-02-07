import customtkinter as ctk
from PIL import Image, ImageDraw


class PeopleSidebar(ctk.CTkFrame):
    def __init__(self, master, controller, callback, **kwargs):
        super().__init__(master, **kwargs)
        self.controller = controller
        self.callback = callback

        self.selected_ids = set()
        self.person_rows = {}

        self.scroll_frame_people = ctk.CTkScrollableFrame(
            self, label_text="Sort by Found People"
        )
        self.scroll_frame_people.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.scroll_frame_people.grid_columnconfigure(0, weight=1)

    def refresh_people_list(self):
        for widget in self.scroll_frame_people.winfo_children():
            widget.destroy()

        people_data = self.controller.get_all_people()

        for i, row in enumerate(people_data):
            self.create_person_row(row['id'], row['name'], row_index=i)

    def create_person_row(self, person_id, person_name, row_index):
        pil_img = self.controller.get_person_thumbnail(person_id)

        if pil_img:
            pil_img = pil_img.resize((60, 60), Image.LANCZOS)
            mask = Image.new("L", pil_img.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0) + pil_img.size, fill=255)
            pil_img.putalpha(mask)

            img_ctk = ctk.CTkImage(light_image=pil_img,
                                   dark_image=pil_img, size=(60, 60))
        else:
            img_ctk = None

        if person_id in self.selected_ids:
            bg_color = ("gray75", "gray35")  # selected
        else:
            bg_color = ("gray85", "gray25")  # normal

        # Create row (frame) in scroll frame
        item_frame = ctk.CTkFrame(
            self.scroll_frame_people, fg_color=bg_color)
        item_frame.grid(row=row_index, column=0, sticky="ew", padx=5, pady=5)
        item_frame.grid_columnconfigure(
            1, weight=1)

        self.person_rows[person_id] = item_frame

        # Create thumbnail in item frame
        if img_ctk:
            lbl_img = ctk.CTkLabel(item_frame, image=img_ctk, text="")
            lbl_img.grid(row=0, column=0, padx=5, pady=5)
            lbl_img.bind(
                "<Button-1>", lambda e: self._toggle_selection(person_id))

        # Create name in item frame
        entry_name = ctk.CTkEntry(item_frame, placeholder_text=person_name)
        entry_name.grid(row=0, column=1, padx=10, sticky="ew")

        def save_action(event=None):
            new_name = entry_name.get().strip()
            if new_name:
                self.controller.update_person_name(person_id, new_name)
                print(f"Saved: {new_name}")
                self.focus()

        # Call save_action when Enter
        entry_name.bind("<Return>", save_action)

        # Create Save button in item frame
        btn_save = ctk.CTkButton(item_frame, text="💾",
                                 width=40, command=save_action)
        btn_save.grid(row=0, column=2, padx=5)

        item_frame.bind(
            "<Button-1>", lambda e: self._toggle_selection(person_id))

    def _toggle_selection(self, person_id):

        if person_id in self.selected_ids:
            self.selected_ids.remove(person_id)
            new_color = ("gray85", "gray25")
        else:
            self.selected_ids.add(person_id)
            new_color = ("gray75", "gray35")

        if person_id in self.person_rows:
            self.person_rows[person_id].configure(fg_color=new_color)

        self.callback(self.selected_ids)
        # print(f"IDS: {self.selected_ids}")
