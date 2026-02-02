import customtkinter as ctk
from PIL import Image, ImageOps
import os


class PhotoGallery(ctk.CTkFrame):
    def __init__(self, master, controller, **kwargs):
        super().__init__(master, **kwargs)
        self.controller = controller

        self.scroll_frame_photos = ctk.CTkScrollableFrame(
            self, label_text="Photos"
        )

        self.scroll_frame_photos.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.build_photo_grid()

    # FLEXBOX ISNT VIABLE IN CTK...
    def build_photo_grid(self):
        for widget in self.scroll_frame_photos.winfo_children():
            widget.destroy()

        COLUMNS = 5
        CARD_WIDTH = 150
        CARD_HEIGHT = 150
        IMG_SIZE = 140

        photos = [{"path": "testS1/default.jpg", "id": i}
                  for i in range(20)]
        total_photos = len(photos)

        for i in range(total_photos):
            row = i // COLUMNS
            col = i % COLUMNS

            self.scroll_frame_photos.grid_columnconfigure(col, weight=1)

            # CARD
            card = ctk.CTkFrame(
                self.scroll_frame_photos,
                width=CARD_WIDTH,
                height=CARD_HEIGHT,
                fg_color=("gray85", "gray25")
            )

            card.grid(row=row, column=col, padx=10, pady=10)
            card.grid_propagate(False)  # Keep photo 150*150

            path = photos[i]["path"]

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
                    command=lambda p_id=photos[i]["id"]: print(
                        f"idd:{p_id}")
                )

            except Exception as e:
                btn = ctk.CTkButton(card, text="ERROR",
                                    width=IMG_SIZE, height=IMG_SIZE)

            btn.place(relx=0.5, rely=0.5, anchor="center")

    def update(self, photos):
        print(f"heeeeeeeeereee it issss, photos for gallery: {photos}")
