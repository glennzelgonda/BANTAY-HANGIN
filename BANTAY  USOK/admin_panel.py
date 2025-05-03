import customtkinter as ctk
import tkinter as tk
tk.Tk().withdraw()
import tkinter.messagebox as messagebox
import sqlite3
import os
import platform
import subprocess
from functools import partial
from database import update_status

class AdminPanel(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master=master)
        self.title("BantayHangin - Admin Panel")
        self.geometry("900x600")
        self.resizable(False, False)
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.dashboard_frame = ctk.CTkFrame(self, fg_color="white")
        self.dashboard_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.display_dashboard_data()

    def display_dashboard_data(self):
        for widget in self.dashboard_frame.winfo_children():
            widget.destroy()

        conn = sqlite3.connect("reports.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, smoke_type, location, description, photo_path, status, timestamp FROM reports")
        records = cursor.fetchall()
        conn.close()

        canvas = ctk.CTkCanvas(self.dashboard_frame, bg="white", highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)

        data_frame = ctk.CTkFrame(canvas, fg_color="white")
        canvas.create_window((0, 0), window=data_frame, anchor="nw")

        v_scrollbar = ctk.CTkScrollbar(self.dashboard_frame, orientation="vertical", command=canvas.yview)
        v_scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=v_scrollbar.set)

        headers = ["Smoke Type", "Location", "Description", "Photo", "Status", "Timestamp"]
        for col, header in enumerate(headers):
            ctk.CTkLabel(data_frame, text=header, font=("Arial", 12, "bold"), text_color="black")\
                .grid(row=0, column=col, padx=37, pady=5)

        for row, record in enumerate(records, start=1):
            report_id, smoke_type, location, description, photo_path, status, timestamp = record
            cells = [smoke_type, location, description, photo_path, status, timestamp]

            for col, cell in enumerate(cells):
                if col == 3 and cell:
                    ctk.CTkButton(
                        data_frame,
                        text="View Photo",
                        width=100,
                        command=partial(self.open_photo, path=cell)
                    ).grid(row=row, column=col, padx=10, pady=5)
                elif col == 4:
                    status_menu = ctk.CTkOptionMenu(
                        data_frame,
                        values=["pending", "in progress", "resolved"],
                        command=partial(self.change_status, report_id)
                    )
                    status_menu.set(cell)
                    status_menu.grid(row=row, column=col, padx=10, pady=5)
                else:
                    ctk.CTkLabel(
                        data_frame,
                        text=str(cell),
                        font=("Arial", 12),
                        text_color="black",
                        anchor="w"
                    ).grid(row=row, column=col, padx=10, pady=5)

        canvas.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

    def change_status(self, report_id, new_status):
        update_status(report_id, new_status)
        messagebox.showinfo("Status Updated", f"Report ID {report_id} status changed to '{new_status}'")
        self.display_dashboard_data()

    def open_photo(self, path):
        try:
            system = platform.system()
            if system == "Windows":
                os.startfile(path)
            elif system == "Darwin":
                subprocess.call(["open", path])
            else:
                subprocess.call(["xdg-open", path])
        except Exception as e:
            messagebox.showerror("Error", f"Cannot open image: {e}")
