import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageDraw
import threading

from app_logic import PhotoController
from repositories.sys_prefs_repo import SystemPrefsRepository

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")


class PhotoApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.controller = PhotoController()
        self.sys_prefs_repo = SystemPrefsRepository(self.controller.db)

        self.window_width = 500
        self.window_height = 600

        self.load_user_preferences()

        self.geometry(f"{self.window_width}x{self.window_height}")
        self.title("AI Photo Manager")

        self.selected_folder = ctk.StringVar()
        self.detect_faces_enabled = ctk.BooleanVar(value=True)

        self.create_widgets()
        # Load people on startup (if any exist in DB)
        self.refresh_people_list()

    def create_widgets(self):

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # top_frame
        self.grid_rowconfigure(1, weight=0)  # lbl_folder
        self.grid_rowconfigure(2, weight=0)  # status_frame
        self.grid_rowconfigure(3, weight=1)  # scroll_frame
        self.grid_rowconfigure(4, weight=0)  # btn_export

        # Top frame
        top_frame = ctk.CTkFrame(self)
        top_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        top_frame.grid_columnconfigure(2, weight=1)

        # Top frame item 1 = Select folder button
        self.btn_select_folder = ctk.CTkButton(
            top_frame, text="Select Folder", command=self.choose_folder)
        self.btn_select_folder.grid(row=0, column=0, padx=10, sticky="w")

        # Top frame item 2 = Detect faces switch
        self.switch_detect = ctk.CTkSwitch(
            top_frame, text="Detect Faces", variable=self.detect_faces_enabled)
        self.switch_detect.grid(row=0, column=1, padx=10, sticky="w")

        # Selected folder string
        self.lbl_folder = ctk.CTkLabel(
            self, textvariable=self.selected_folder, text_color="gray"
        )
        self.lbl_folder.grid(row=1, column=0, padx=20, sticky="w")

        # Status frame for progress bar and status label
        self.status_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.status_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=5)
        self.status_frame.grid_columnconfigure(0, weight=1)

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self.status_frame)
        self.progress_bar.grid(row=0, column=0, sticky="ew", pady=(10, 5))
        self.progress_bar.set(0)

        # Progress bar status label
        self.lbl_status = ctk.CTkLabel(self.status_frame, text="")
        self.lbl_status.grid(row=1, column=0, pady=(0, 10))

        self.status_frame.grid_remove()

        # Scrollable list of people
        self.scroll_frame = ctk.CTkScrollableFrame(
            self, label_text="Found People"
        )
        self.scroll_frame.grid(
            row=3, column=0, padx=10, pady=10, sticky="nsew"
        )
        self.scroll_frame.grid_columnconfigure(0, weight=1)

        # Export button (not implemented)
        self.btn_export = ctk.CTkButton(self, text="Export Photos (TODO)")
        self.btn_export.grid(row=4, column=0, pady=10)

    def choose_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.selected_folder.set(folder)
            print("Starting analysis...")

            # progress bar

            self.status_frame.grid()

            self.update_progress_bar(0, "Starting...")

            self.btn_select_folder.configure(state="disabled")
            self.switch_detect.configure(state="disabled")

            threading.Thread(
                target=self.run_folder_analysis_with_seperate_thread,
                args=(folder,),
                daemon=True
            ).start()

    def run_folder_analysis_with_seperate_thread(self, folder):

        self.controller.analyze_folder(
            folder,
            detect_faces=self.detect_faces_enabled.get(),
            callback=self.update_progress_bar
        )

        self.after(0, lambda: self.on_analysis_complete())

    def on_analysis_complete(self):
        print("Done.")
        self.refresh_people_list()
        self.btn_select_folder.configure(state="enabled")
        self.switch_detect.configure(state="enabled")
        # self.status_frame.pack_forget()

    def refresh_people_list(self):
        for widget in self.scroll_frame.winfo_children():
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

        # Create row (frame) in scroll frame
        item_frame = ctk.CTkFrame(
            self.scroll_frame, fg_color=("gray85", "gray25"))
        item_frame.grid(row=row_index, column=0, sticky="ew", padx=5, pady=5)
        item_frame.grid_columnconfigure(
            1, weight=1)

        # Create thumbnail in item frame
        if img_ctk:
            lbl_img = ctk.CTkLabel(item_frame, image=img_ctk, text="")
            lbl_img.grid(row=0, column=0, padx=5, pady=5)

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

    def on_closing(self):
        self.controller.close()
        self.destroy()

    def update_progress_bar(self, percent, message=""):
        # THREAD SAFE - another thread cannot update GUI directly
        self.after(0, lambda: self.progress_bar.set(percent))

        if message:
            if isinstance(message, (int, float)):
                text = f"{message*100:.0f}%"
            else:
                text = str(message)

            self.after(0, lambda: self.lbl_status.configure(text=text))

    def load_user_preferences(self):
        width = self.sys_prefs_repo.load_pref("window_width")
        if (width != None and width > 0):
            self.window_width = width

        height = self.sys_prefs_repo.load_pref("window_height")
        if (height != None and height > 0):
            self.window_height = height


if __name__ == "__main__":
    app = PhotoApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
