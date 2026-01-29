import customtkinter as ctk
from tkinter import filedialog
import threading

from app_logic import PhotoController
from repositories.sys_prefs_repo import SystemPrefsRepository

from structures import FilterCriteria
from ui.gallery import PhotoGallery
from ui.sidebar import PeopleSidebar

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")


class PhotoApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.controller = PhotoController()
        self.sys_prefs_repo = SystemPrefsRepository(self.controller.db)
        self.sidebar = None
        self.gallery = None

        self.window_width = 500
        self.window_height = 600
        self.detect_faces_enabled = ctk.BooleanVar(value=True)
        self.load_user_preferences()

        self.geometry(f"{self.window_width}x{self.window_height}")
        self.title("AI Photo Manager")

        self.selected_folder = ctk.StringVar()

        self.create_widgets()
        self.sidebar.refresh_people_list()

    def create_widgets(self):

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # top_frame
        self.grid_rowconfigure(1, weight=0)  # lbl_folder
        self.grid_rowconfigure(2, weight=0)  # status_frame
        self.grid_rowconfigure(3, weight=1)  # scroll_frame_people_people
        self.grid_rowconfigure(4, weight=1)  # scroll_frame_photos
        self.grid_rowconfigure(5, weight=0)  # btn_export

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

        # Scrollable list of people NEW
        self.sidebar = PeopleSidebar(
            self, self.controller
        )
        self.sidebar.grid(
            row=3, column=0, padx=10, pady=10, sticky="nsew"
        )
        self.sidebar.grid_columnconfigure(0, weight=1)

        # Photo gallery
        self.gallery = PhotoGallery(
            self,
            controller=self.controller,
        )
        self.gallery.grid(
            row=4, column=0, padx=10, pady=10, sticky="nsew"
        )
        self.gallery.grid_columnconfigure(0, weight=1)

        # Export button (not implemented)
        self.btn_export = ctk.CTkButton(self, text="Export Photos (TODO)")
        self.btn_export.grid(row=5, column=0, pady=10)

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
        self.sidebar.refresh_people_list()
        self.btn_select_folder.configure(state="enabled")
        self.switch_detect.configure(state="enabled")
        # self.status_frame.pack_forget()

    def on_closing(self):

        # SAVE WINDOW H AND W STATE
        scaling = self._get_window_scaling()
        width = int(self.winfo_width() / scaling)
        height = int(self.winfo_height() / scaling)
        self.sys_prefs_repo.save_pref("window_width", width)
        self.sys_prefs_repo.save_pref("window_height", height)

        # # SAVE FULLSCREEN STATE
        # self.sys_prefs_repo.save_pref(
        #     "fullscreen_enabled", self.attributes("-fullscreen"))

        # SAVE face_detect_button STATE
        self.sys_prefs_repo.save_pref(
            "face_detection_enabled", self.detect_faces_enabled.get())

        # CLOSE DB
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

        detection_button_state = self.sys_prefs_repo.load_pref(
            "face_detection_enabled")
        if (detection_button_state != None):
            self.detect_faces_enabled.set(detection_button_state)


if __name__ == "__main__":
    app = PhotoApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
