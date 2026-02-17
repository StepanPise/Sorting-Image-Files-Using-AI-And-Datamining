import customtkinter as ctk
from tkcalendar import DateEntry
from datetime import date


class TimeSidebar(ctk.CTkFrame):
    def __init__(self, master, controller, callback, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.controller = controller
        self.callback = callback

        self.scroll_frame = ctk.CTkScrollableFrame(
            self, fg_color="transparent")
        self.scroll_frame.grid(row=0, column=0, sticky="nsew")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Nastavíme váhy uvnitř scroll_frame
        self.scroll_frame.grid_columnconfigure(0, weight=1)

        self._load_ui()

    def apply_filter(self):
        d_from = self.entry_from.get()
        d_to = self.entry_to.get()

        self._check_for_diff_inputs(d_from, d_to)

        if self.callback:
            self.callback(d_from, d_to)

    def reset_filter(self):
        self.entry_from.delete(0, "end")
        self.entry_to.delete(0, "end")
        self.apply_filter()

    def _load_ui(self):
        # TITLE
        self.lbl_title = ctk.CTkLabel(
            self.scroll_frame, text="Filter by Time", font=("Arial", 14, "bold"))
        self.lbl_title.grid(row=0, column=0, padx=10,
                            pady=(10, 15), sticky="w")
        # DATE 1
        self.lbl_from = ctk.CTkLabel(
            self.scroll_frame, text="Date from:", anchor="w")
        self.lbl_from.grid(row=1, column=0, padx=10, pady=(
            5, 0), sticky="ew")

        # DATE 1 ENTRY
        self.entry_from = DateEntry(self.scroll_frame, width=12, background='darkblue',
                                    foreground='white', borderwidth=2,
                                    date_pattern='y-mm-dd')
        self.entry_from.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.entry_from.delete(0, "end")

        # DATE 2
        self.lbl_to = ctk.CTkLabel(
            self.scroll_frame, text="Date to:", anchor="w")
        self.lbl_to.grid(row=3, column=0, padx=10, pady=(15, 0), sticky="ew")

        # DATE 2 ENTRY
        self.entry_to = DateEntry(self.scroll_frame, width=12, background='darkblue',
                                  foreground='white', borderwidth=2,
                                  date_pattern='y-mm-dd')
        self.entry_to.grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.entry_to.delete(0, "end")

        # SHORTCUTS FRAME
        self.shortcuts_frame = ctk.CTkFrame(
            self.scroll_frame, fg_color="transparent")
        self.shortcuts_frame.grid(
            row=5, column=0, pady=(20, 10), padx=10, sticky="ew")

        self.shortcuts_frame.grid_columnconfigure(0, weight=1)
        self.shortcuts_frame.grid_columnconfigure(1, weight=1)

        self.btn_this_year = ctk.CTkButton(
            self.shortcuts_frame, text="This year", fg_color="gray", command=self._switch_to_this_year)
        self.btn_this_year.grid(row=0, column=0, pady=0,
                                padx=(0, 5), sticky="ew")

        self.btn_last_year = ctk.CTkButton(
            self.shortcuts_frame, text="Last year", fg_color="gray", command=self._switch_to_last_year)
        self.btn_last_year.grid(row=0, column=1, pady=0,
                                padx=(5, 0), sticky="ew")

        # BUTTONS
        self.btn_apply = ctk.CTkButton(
            self.scroll_frame, text="Apply filter", command=self.apply_filter)
        self.btn_apply.grid(row=6, column=0, pady=(
            20, 10), padx=10, sticky="ew")

        self.btn_reset = ctk.CTkButton(
            self.scroll_frame, text="Reset date", fg_color="gray", command=self.reset_filter)
        self.btn_reset.grid(row=7, column=0, pady=5, padx=10, sticky="ew")

    def _switch_to_this_year(self):
        current_year = date.today().year
        start_date = date(current_year, 1, 1)
        end_date = date(current_year, 12, 31)

        self.entry_from.set_date(start_date)
        self.entry_to.set_date(end_date)
        self.apply_filter()

    def _switch_to_last_year(self):
        current_year = date.today().year - 1
        start_date = date(current_year, 1, 1)
        end_date = date(current_year, 12, 31)

        self.entry_from.set_date(start_date)
        self.entry_to.set_date(end_date)
        self.apply_filter()

    def _check_for_diff_inputs(self, d_from, d_to):
        if len(d_from) == 4:
            d_from = f"{d_from}-01-01"
        if len(d_to) == 4:
            d_to = f"{d_to}-12-31"
        if len(d_from) == 7:
            d_from = f"{d_from}-01"
        if len(d_to) == 7:
            d_to = f"{d_to}-31"

        if d_from:
            self.entry_from.set_date(d_from)
        if d_to:
            self.entry_to.set_date(d_to)
