import customtkinter as ctk


class PhotoGallery(ctk.CTkFrame):
    def __init__(self, master, controller, **kwargs):
        super().__init__(master, **kwargs)
        self.controller = controller

        self.scroll_frame_photos = ctk.CTkScrollableFrame(
            self, label_text="Photos"
        )

        # nastaveni gridu pro scrollable frame
        self.scroll_frame_photos.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def build_photo_grid(self):
        pass
