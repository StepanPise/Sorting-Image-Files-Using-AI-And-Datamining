import customtkinter as ctk
from PIL import Image, ImageOps
import os

# ADD REFRESH GALLERY FUNCTION!!!


class PhotoGallery(ctk.CTkFrame):
    def __init__(self, master, controller, **kwargs):
        super().__init__(master, **kwargs)
        self.controller = controller

        self.num_of_photos_per_batch = 20
        self.batches = []  # [[id,path,...], [id,path,...], ...]
        self.current_batch_index = 0

        self.grid_rowconfigure(0, weight=1)  # photos
        self.grid_rowconfigure(1, weight=0)  # navigation
        self.grid_columnconfigure(0, weight=1)

        # 1. SCROLL FRAME 5
        self.scroll_frame_photos = ctk.CTkScrollableFrame(
            self, label_text="Photos"
        )
        self.scroll_frame_photos.grid(
            row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.scroll_frame_photos.grid_columnconfigure(0, weight=1)

        # 2. NAVIGATION BUTTONS
        self.bottom_bar = ctk.CTkFrame(self, height=40, fg_color="transparent")
        self.bottom_bar.grid(row=1, column=0, sticky="ew", padx=10, pady=5)

        self.btn_prev = ctk.CTkButton(self.bottom_bar, text="< Previous", width=100,
                                      command=lambda: self.change_batch(-1))
        self.btn_prev.pack(side="left", padx=10)

        self.lbl_page = ctk.CTkLabel(self.bottom_bar, text="0 / 0")
        self.lbl_page.pack(side="left", expand=True)

        self.btn_next = ctk.CTkButton(self.bottom_bar, text="Next >", width=100,
                                      command=lambda: self.change_batch(1))
        self.btn_next.pack(side="right", padx=10)

    def update(self, photos):
        self.batches = []
        temp_list = []

        for photo in photos:

            temp_list.append(photo)

            if len(temp_list) == self.num_of_photos_per_batch:
                self.batches.append(temp_list)
                temp_list = []

        # last incomplete batch
        if temp_list:
            self.batches.append(temp_list)

        self.current_batch_index = 0
        self.build_photo_grid()

    def change_batch(self, direction):
        new_index = self.current_batch_index + direction

        if 0 <= new_index < len(self.batches):
            self.current_batch_index = new_index
            self.build_photo_grid()

    def build_photo_grid(self):
        for widget in self.scroll_frame_photos.winfo_children():
            widget.destroy()

        if not self.batches:
            self.lbl_page.configure(text="0 / 0")
            self.btn_prev.configure(state="disabled")
            self.btn_next.configure(state="disabled")
            return

        current_photos = self.batches[self.current_batch_index]

        self.lbl_page.configure(
            text=f"Page {self.current_batch_index + 1} / {len(self.batches)}")

        self.btn_prev.configure(
            state="normal" if self.current_batch_index > 0 else "disabled")
        self.btn_next.configure(state="normal" if self.current_batch_index < len(
            self.batches) - 1 else "disabled")

        COLUMNS = 5
        CARD_WIDTH = 150
        CARD_HEIGHT = 150
        IMG_SIZE = 140

        for i, photo_data in enumerate(current_photos):
            row = i // COLUMNS
            col = i % COLUMNS
            self.scroll_frame_photos.grid_columnconfigure(col, weight=1)

            card = ctk.CTkFrame(
                self.scroll_frame_photos,
                width=CARD_WIDTH,
                height=CARD_HEIGHT,
                fg_color=("gray85", "gray25")
            )
            card.grid(row=row, column=col, padx=10, pady=10)
            card.grid_propagate(False)

            path = photo_data.get('path')
            p_id = photo_data.get('id')

            try:
                pil_img = Image.open(path)
                pil_img = ImageOps.exif_transpose(pil_img)
                pil_img.thumbnail((IMG_SIZE, IMG_SIZE))

                my_image = ctk.CTkImage(
                    light_image=pil_img,
                    dark_image=pil_img,
                    size=(IMG_SIZE, IMG_SIZE)
                )

                btn = ctk.CTkButton(
                    card,
                    text="",
                    image=my_image,
                    fg_color="transparent",
                    hover_color="gray40",
                    width=IMG_SIZE,
                    height=IMG_SIZE,
                    command=lambda x=p_id: print(f"id:{x}")
                )
            except Exception as e:
                btn = ctk.CTkButton(card, text="ERROR",
                                    width=IMG_SIZE, height=IMG_SIZE)

            btn.place(relx=0.5, rely=0.5, anchor="center")
