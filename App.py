import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageDraw
import threading

from app_logic import PhotoController

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")


class PhotoApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.controller = PhotoController()

        self.geometry("500x600")
        self.title("AI Photo Manager")

        self.selected_folder = ctk.StringVar()
        self.detect_faces_enabled = ctk.BooleanVar(value=True)

        self.create_widgets()

        # Load people on startup (if any exist in DB)
        self.refresh_people_list()

    def create_widgets(self):
        # Top frame
        top_frame = ctk.CTkFrame(self)
        top_frame.pack(pady=20, padx=20, fill="x")

        # Top frame item 1
        self.btn_select = ctk.CTkButton(
            top_frame, text="Select Folder", command=self.choose_folder)
        self.btn_select.pack(side="left", padx=10)

        # Top frame item 2
        self.switch_detect = ctk.CTkSwitch(
            top_frame, text="Detect Faces", variable=self.detect_faces_enabled)
        self.switch_detect.pack(side="left", padx=10)

        # Selected folder label
        self.lbl_folder = ctk.CTkLabel(
            self, textvariable=self.selected_folder, text_color="gray")
        self.lbl_folder.pack()

        # Middle frame
        middle_frame = ctk.CTkFrame(self)
        middle_frame.pack(pady=20, padx=20, fill="x")

        # Scrollable list of people
        self.scroll_frame = ctk.CTkScrollableFrame(
            middle_frame, label_text="Found People")
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Export button (not implemented)
        self.btn_export = ctk.CTkButton(self, text="Export Photos (TODO)")
        self.btn_export.pack(pady=10)

    def choose_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.selected_folder.set(folder)
            print("Starting analysis...")

            threading.Thread(
                target=self.controller.analyze_folder,
                args=(folder,),
                kwargs={"detect_faces": self.detect_faces_enabled.get()},
                daemon=True
            ).start()

            print("Done.")
            self.refresh_people_list()

    def refresh_people_list(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        people_data = self.controller.get_all_people()

        for row in people_data:
            self.create_person_row(row['id'], row['name'])

    def create_person_row(self, person_id, person_name):
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

        # Create row (frame) in scroll frame
        item_frame = ctk.CTkFrame(
            self.scroll_frame, fg_color=("gray85", "gray25"))
        item_frame.pack(fill="x", padx=5, pady=5)

        # Create thumbnail in item frame
        if img_ctk:
            lbl_img = ctk.CTkLabel(item_frame, image=img_ctk, text="")
            lbl_img.pack(side="left", padx=5, pady=5)

        # Create name in item frame
        entry_name = ctk.CTkEntry(item_frame, placeholder_text=person_name)
        entry_name.pack(side="left", padx=10, fill="x", expand=True)

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
        btn_save.pack(side="left", padx=5)

    def on_closing(self):
        self.controller.close()
        self.destroy()


if __name__ == "__main__":
    app = PhotoApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
