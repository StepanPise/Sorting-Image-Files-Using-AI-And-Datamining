import customtkinter as ctk
from tkcalendar import DateEntry


class TimeSidebar(ctk.CTkFrame):
    def __init__(self, master, controller, callback, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.controller = controller
        self.callback = callback
        self._load_ui()

    def apply_filter(self):
        # DateEntry.get() == YYYY-MM-DD
        d_from = self.entry_from.get()
        d_to = self.entry_to.get()

        if not d_from:
            d_from = None
        if not d_to:
            d_to = None

        if self.callback:
            self.callback(d_from, d_to)

    def reset_filter(self):
        self.entry_from.delete(0, "end")
        self.entry_to.delete(0, "end")
        self.apply_filter()

    def _load_ui(self):
        # TITLE
        self.lbl_title = ctk.CTkLabel(
            self, text="Filter by Time")
        self.lbl_title.pack(pady=(10, 15), anchor="w", padx=10)

        # DATE 1
        self.lbl_from = ctk.CTkLabel(self, text="Date from:", anchor="w")
        self.lbl_from.pack(fill="x", padx=10, pady=(5, 0))
        # DATE 1 ENTRY
        self.entry_from = DateEntry(self, width=12, background='darkblue',
                                    foreground='white', borderwidth=2,
                                    date_pattern='y-mm-dd')
        self.entry_from.pack(padx=10, pady=5, anchor="w")
        self.entry_from.delete(0, "end")

        # DATE 2
        self.lbl_to = ctk.CTkLabel(self, text="Date to:", anchor="w")
        self.lbl_to.pack(fill="x", padx=10, pady=(15, 0))
        # DATE 2 ENTRY
        self.entry_to = DateEntry(self, width=12, background='darkblue',
                                  foreground='white', borderwidth=2,
                                  date_pattern='y-mm-dd')
        self.entry_to.pack(padx=10, pady=5, anchor="w")
        self.entry_to.delete(0, "end")

        # BUTTONS
        self.btn_apply = ctk.CTkButton(
            self, text="Apply filter", command=self.apply_filter)
        self.btn_apply.pack(pady=(20, 10), padx=10, fill="x")

        self.btn_reset = ctk.CTkButton(
            self, text="Reset date", fg_color="gray", command=self.reset_filter)
        self.btn_reset.pack(pady=5, padx=10, fill="x")
