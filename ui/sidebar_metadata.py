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
