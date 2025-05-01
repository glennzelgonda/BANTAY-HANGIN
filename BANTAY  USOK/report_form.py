import customtkinter as ctk
import tkinter.filedialog as fd
import tkinter.messagebox as messagebox
import sqlite3
from tkinter import Scrollbar, Canvas
from database import init_db, insert_report
import os
import platform
import subprocess
from functools import partial

class BantayUsokApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("BantayUsok - Smoke Reporting System")
        self.geometry("900x600")
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.photo_path = None

        tabview = ctk.CTkTabview(self)
        tabview.pack(fill="both", expand=True, padx=10, pady=10)

        # Tabs
        self.report_tab = tabview.add("Report Smoke")
        self.dashboard_tab = tabview.add("Dashboard")

        # Build tabs
        self.build_report_tab()
        self.build_dashboard_tab()

    def build_report_tab(self):
        ctk.CTkLabel(self.report_tab, text="Smoke Type:").pack(pady=5)
        self.smoke_type = ctk.CTkOptionMenu(self.report_tab, values=["Cigarette", "Burning Trash", "Vehicle Emission"])
        self.smoke_type.pack()

        ctk.CTkLabel(self.report_tab, text="Location (Barangay/Street):").pack(pady=5)
        self.location_entry = ctk.CTkEntry(self.report_tab, placeholder_text="e.g. Barangay 5, Mabini St.")
        self.location_entry.pack()

        ctk.CTkLabel(self.report_tab, text="Description:").pack(pady=5)
        self.description_entry = ctk.CTkTextbox(self.report_tab, height=100)
        self.description_entry.pack()

        ctk.CTkButton(self.report_tab, text="Upload Photo", command=self.upload_photo).pack(pady=10)
        ctk.CTkButton(self.report_tab, text="Submit Report", command=self.submit_report).pack(pady=10)

    def upload_photo(self):
        file_path = fd.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if file_path:
            self.photo_path = file_path

    def submit_report(self):
        smoke_type = self.smoke_type.get()
        location = self.location_entry.get()
        description = self.description_entry.get("1.0", "end").strip()

        if not smoke_type or not location:
            messagebox.showerror("Error", "Please fill in all required fields.")
            return

        insert_report(smoke_type, location, description, self.photo_path)
        messagebox.showinfo("Success", "Report submitted successfully!")

        self.location_entry.delete(0, "end")
        self.description_entry.delete("1.0", "end")
        self.photo_path = None

        self.refresh_dashboard()

    def build_dashboard_tab(self):
        self.dashboard_frame = ctk.CTkFrame(self.dashboard_tab, fg_color="white")
        self.dashboard_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.display_dashboard_data()

    def refresh_dashboard(self):
        for widget in self.dashboard_frame.winfo_children():
            widget.destroy()
        self.display_dashboard_data()

    def display_dashboard_data(self):
        conn = sqlite3.connect("reports.db")
        cursor = conn.cursor()
        cursor.execute("SELECT smoke_type, location, description, photo_path, status, timestamp FROM reports")
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
            label.grid(row=0, column=col_index, padx=10, pady=5)

        for row_index, record in enumerate(records, start=1):
            for col_index, value in enumerate(record):
                if col_index == 3 and value:  # If it's the photo_path column and not None
                    open_photo = partial(self.open_photo, path=value)
                    view_button = ctk.CTkButton(data_frame, text="View Photo", width=100, command=open_photo)
                    view_button.grid(row=row_index, column=col_index, padx=10, pady=5)
                else:
                    label = ctk.CTkLabel(data_frame, text=str(value), font=("Arial", 12), text_color="black",
                                         anchor="w")
                    label.grid(row=row_index, column=col_index, padx=10, pady=5)

        canvas.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

    def open_photo(self, path):
        try:
            if platform.system() == "Windows":
                os.startfile(path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.call(["open", path])
            else:  # Linux
                subprocess.call(["xdg-open", path])
        except Exception as e:
            messagebox.showerror("Error", f"Cannot open image: {e}")

if __name__ == "__main__":
    init_db()
    app = BantayUsokApp()
    app.mainloop()
