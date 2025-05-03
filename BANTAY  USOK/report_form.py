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
from PIL import Image, ImageTk

class BantayUsokApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("BantayHangin - Smoke Reporting System")
        self.geometry("1400x700")
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        self.resizable(True, True)
        self.photo_path = None

        tabview = ctk.CTkTabview(self)
        tabview.pack(fill="both", expand=True, padx=7, pady=10)

        # Tabs
        self.report_tab = tabview.add("Report Smoke")
        self.dashboard_tab = tabview.add("Dashboard")

        # Build tabs
        self.build_report_tab()
        self.build_dashboard_tab()

    def animate_gif(self):
        self.current_frame = (self.current_frame + 1) % len(self.gif_frames)
        self.canvas.itemconfig(self.bg_image_id, image=self.gif_frames[self.current_frame])
        self.after(50, self.animate_gif)  # Adjust timing if needed

    def build_report_tab(self):
        # 🎞️ Load animated GIF frames
        gif_path = "images/bg_report_tab.gif"
        self.gif_image = Image.open(gif_path)
        self.gif_frames = []

        try:
            while True:
                frame = self.gif_image.copy().resize((1400, 650))
                self.gif_frames.append(ImageTk.PhotoImage(frame))
                self.gif_image.seek(len(self.gif_frames))
        except EOFError:
            pass

        self.current_frame = 0

        # 🎥 Canvas for background
        self.canvas = Canvas(self.report_tab, width=1400, height=650, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.bg_image_id = self.canvas.create_image(0, 0, anchor="nw", image=self.gif_frames[0])
        self.animate_gif()

        # 🧾 Semi-transparent-style form frame (solid light color instead)
        form_frame = ctk.CTkFrame(master=self.canvas, fg_color="#a2c4c9", corner_radius=1)
        self.canvas.create_window(685, 380, window=form_frame, anchor="center")
        form_frame.grid_columnconfigure(0, weight=1)

        # Title
        ctk.CTkLabel(form_frame, text="Report Smoke", font=("Helvetica", 20, "bold"), text_color="#222").grid(
            row=0, column=0, pady=(10, 20))

        # Smoke Type
        ctk.CTkLabel(form_frame, text="Smoke Type:", text_color="#333", font=("Helvetica", 14)).grid(
            row=1, column=0, sticky="w", padx=20)

        # OptionMenu with color customization
        self.smoke_type = ctk.CTkOptionMenu(
            form_frame,
            values=["Cigarette", "Burning Trash", "Vehicle Emission"],
            button_color="#309baa",  # Change button (dropdown) background color
            fg_color="#309baa",  # Change foreground (button text) color
            text_color="black"  # Change text color inside the dropdown
        )
        self.smoke_type.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Location
        ctk.CTkLabel(form_frame, text="Location (Barangay/Street):", text_color="#333", font=("Helvetica", 14)).grid(
            row=3, column=0, sticky="w", padx=20)
        self.location_entry = ctk.CTkEntry(form_frame, placeholder_text="e.g. Barangay 5, Mabini St.",
                                           font=("Helvetica", 13))
        self.location_entry.grid(row=4, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Description
        ctk.CTkLabel(form_frame, text="Description:", text_color="#333", font=("Helvetica", 14)).grid(
            row=5, column=0, sticky="w", padx=20)
        self.description_entry = ctk.CTkTextbox(form_frame, height=100, font=("Helvetica", 13))
        self.description_entry.grid(row=6, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Upload & Submit
        ctk.CTkButton(form_frame,
                      text="Upload Photo",
                      command=self.upload_photo,
                      fg_color="#309baa"  # Set button text color
                      ).grid(row=7, column=0, padx=20, pady=(10, 5))

        # In the submit report button
        ctk.CTkButton(form_frame,
                      text="Submit Report",
                      command=self.submit_report,
                      fg_color="#309baa"  # Set button text color
                      ).grid(row=8, column=0, padx=20, pady=(5, 20))

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

        self.display_summary()

        canvas = Canvas(self.dashboard_frame, bg="white", highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)

        data_frame = ctk.CTkFrame(canvas, fg_color="white")
        canvas.create_window((0, 0), window=data_frame, anchor="nw")

        v_scrollbar = Scrollbar(self.dashboard_frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=v_scrollbar.set)
        v_scrollbar.pack(side="right", fill="y")

        headers = ["Smoke Type", "Location", "Description", "Photo", "Status", "Timestamp"]
        for col_index, header in enumerate(headers):
            label = ctk.CTkLabel(data_frame, text=header, font=("MS UI Gothic", 20, "bold"), text_color="black")
            label.grid(row=0, column=col_index, padx=65, pady=5)

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

    def display_summary(self):
        conn = sqlite3.connect("reports.db")
        cursor = conn.cursor()

        # 1. Total reports
        cursor.execute("SELECT COUNT(*) FROM reports")
        total_reports = cursor.fetchone()[0]

        # 2. Smoke type breakdown
        cursor.execute("SELECT smoke_type, COUNT(*) FROM reports GROUP BY smoke_type")
        smoke_counts = cursor.fetchall()

        # 3. Monthly trends
        cursor.execute(
            "SELECT strftime('%Y-%m', timestamp) AS month, COUNT(*) FROM reports GROUP BY month ORDER BY month")
        monthly_trends = cursor.fetchall()

        # 4. Status breakdown
        cursor.execute("SELECT status, COUNT(*) FROM reports GROUP BY status")
        status_counts = cursor.fetchall()

        conn.close()

        # Create a frame to hold summary
        summary_frame = ctk.CTkFrame(self.dashboard_frame, fg_color="#f0f0f0")
        summary_frame.pack(fill="x", padx=10, pady=10)

        # Total Reports
        ctk.CTkLabel(summary_frame, text=f"📋 Total Reports: {total_reports}", font=("Arial", 14, "bold")).pack(
            anchor="w", padx=10, pady=5)

        # Smoke Type Breakdown
        breakdown = "🔥 Smoke Types:\n"
        for smoke_type, count in smoke_counts:
            breakdown += f"• {smoke_type}: {count}\n"
        ctk.CTkLabel(summary_frame, text=breakdown.strip(), font=("Arial", 12), justify="left").pack(anchor="w",
                                                                                                     padx=10)

        # Monthly Trends
        trend_text = "📈 Monthly Trends:\n"
        for month, count in monthly_trends:
            trend_text += f"• {month}: {count} reports\n"
        ctk.CTkLabel(summary_frame, text=trend_text.strip(), font=("Arial", 12), justify="left").pack(anchor="w",
                                                                                                      padx=10, pady=5)

        # Status Breakdown
        status_text = "🟢 Case Status:\n"
        for status, count in status_counts:
            status_text += f"• {status.capitalize()}: {count}\n"
        ctk.CTkLabel(summary_frame, text=status_text.strip(), font=("Arial", 12), justify="left").pack(anchor="w",
                                                                                                       padx=10)

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
