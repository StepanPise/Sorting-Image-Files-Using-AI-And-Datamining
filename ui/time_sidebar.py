import customtkinter as ctk
from tkcalendar import Calendar


class TimeSidebar(ctk.CTkFrame):

    def __init__(self, master, controller, callback, **kwargs):
        super().__init__(master, **kwargs)
        self.controller = controller
        self.callback = callback
