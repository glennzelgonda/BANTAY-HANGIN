import customtkinter as ctk
import tkinter.messagebox as messagebox
from tkinter import Scrollbar, Canvas
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

        canvas = Canvas(self.dashboard_frame, bg="white", highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)

        data_frame = ctk.CTkFrame(canvas, fg_color="white")
        canvas.create_window((0, 0), window=data_frame, anchor="nw")

        v_scrollbar = Scrollbar(self.dashboard_frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=v_scrollbar.set)
        v_scrollbar.pack(side="right", fill="y")

        headers = ["Smoke Type", "Location", "Description", "Photo", "Status", "Timestamp"]
        for col_index, header in enumerate(headers):
            label = ctk.CTkLabel(data_frame, text=header, font=("Arial", 12, "bold"), text_color="black")
            label.grid(row=0, column=col_index, padx=37, pady=5)

        for row_index, record in enumerate(records, start=1):
            report_id, smoke_type, location, description, photo_path, status, timestamp = record
            values = [smoke_type, location, description, photo_path, status, timestamp]

            for col_index, value in enumerate(values):
                if col_index == 3 and value:
                    open_photo = partial(self.open_photo, path=value)
                    view_button = ctk.CTkButton(data_frame, text="View Photo", width=100, command=open_photo)
                    view_button.grid(row=row_index, column=col_index, padx=10, pady=5)
                elif col_index == 4:
                    status_menu = ctk.CTkOptionMenu(
                        data_frame,
                        values=["pending", "in progress", "resolved"],
                        command=partial(self.change_status, report_id)
                    )
                    status_menu.set(value)
                    status_menu.grid(row=row_index, column=col_index, padx=10, pady=5)
                else:
                    label = ctk.CTkLabel(data_frame, text=str(value), font=("Arial", 12), text_color="black", anchor="w")
                    label.grid(row=row_index, column=col_index, padx=10, pady=5)

        canvas.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

    def change_status(self, report_id, new_status):
        update_status(report_id, new_status)
        messagebox.showinfo("Status Updated", f"Report ID {report_id} status changed to '{new_status}'")
        self.display_dashboard_data()

    def open_photo(self, path):
        try:
            if platform.system() == "Windows":
                os.startfile(path)
            elif platform.system() == "Darwin":
                subprocess.call(["open", path])
            else:
                subprocess.call(["xdg-open", path])
        except Exception as e:
            messagebox.showerror("Error", f"Cannot open image: {e}")
