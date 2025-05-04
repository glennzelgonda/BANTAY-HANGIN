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
from PIL import Image, ImageTk


class AdminPanel(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master=master)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.title("BantayHangin - Admin Panel")
        self.geometry("1200x700")
        self.resizable(True, True)
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Main container frame
        self.main_frame = ctk.CTkFrame(self, fg_color="white")
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        # Header section
        self.header_frame = ctk.CTkFrame(self.main_frame, fg_color="#2c3e50", height=60)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        self.header_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.header_frame,
            text="REPORTS DASHBOARD",
            font=("Arial", 18, "bold"),
            text_color="white"
        ).grid(row=0, column=0, padx=20, pady=10, sticky="w")

        # Refresh button
        refresh_btn = ctk.CTkButton(
            self.header_frame,
            text="Refresh",
            width=100,
            command=self.display_dashboard_data,
            fg_color="#3498db",
            hover_color="#2980b9"
        )
        refresh_btn.grid(row=0, column=1, padx=20, pady=10, sticky="e")

        # Data display section
        self.data_container = ctk.CTkFrame(self.main_frame, fg_color="white")
        self.data_container.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        self.data_container.grid_columnconfigure(0, weight=1)
        self.data_container.grid_rowconfigure(0, weight=1)

        # Initial data load
        self.display_dashboard_data()

    def on_close(self):
        """Clean up before closing the window"""
        # Cancel any pending after events
        if hasattr(self, '_after_ids'):
            for after_id in self._after_ids:
                self.after_cancel(after_id)
        self.destroy()

    def display_dashboard_data(self):
        # Clear existing widgets
        for widget in self.data_container.winfo_children():
            widget.destroy()

        # Connect to database
        conn = sqlite3.connect("reports.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, smoke_type, location, description, photo_path, status, timestamp FROM reports")
        records = cursor.fetchall()
        conn.close()

        # Create scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(
            self.data_container,
            fg_color="white",
            scrollbar_fg_color="#ecf0f1",
            scrollbar_button_color="#bdc3c7"
        )
        scroll_frame.grid(row=0, column=0, sticky="nsew")

        # Configure grid for data display
        for i in range(7):  # 7 columns
            scroll_frame.grid_columnconfigure(i, weight=1 if i in [1, 2] else 0)

        # Table headers
        headers = ["ID", "Smoke Type", "Location", "Description", "Photo", "Status", "Timestamp"]
        for col, header in enumerate(headers):
            header_frame = ctk.CTkFrame(scroll_frame, fg_color="#3498db", height=40)
            header_frame.grid(row=0, column=col, sticky="nsew", padx=1, pady=1)

            ctk.CTkLabel(
                header_frame,
                text=header,
                font=("Arial", 12, "bold"),
                text_color="white"
            ).pack(expand=True, fill="both", padx=5, pady=5)

        # Table rows
        for row, record in enumerate(records, start=1):
            report_id, smoke_type, location, description, photo_path, status, timestamp = record

            # Alternate row colors
            row_color = "#ffffff" if row % 2 == 0 else "#f8f9fa"

            # ID column
            id_frame = ctk.CTkFrame(scroll_frame, fg_color=row_color, height=50)
            id_frame.grid(row=row, column=0, sticky="nsew", padx=1, pady=1)
            ctk.CTkLabel(
                id_frame,
                text=str(report_id),
                font=("Arial", 11),
                text_color="#2c3e50"
            ).pack(expand=True, fill="both", padx=5, pady=5)

            # Smoke Type column
            type_frame = ctk.CTkFrame(scroll_frame, fg_color=row_color, height=50)
            type_frame.grid(row=row, column=1, sticky="nsew", padx=1, pady=1)
            ctk.CTkLabel(
                type_frame,
                text=smoke_type,
                font=("Arial", 11),
                text_color="#2c3e50",
                anchor="w"
            ).pack(expand=True, fill="both", padx=5, pady=5)

            # Location column
            loc_frame = ctk.CTkFrame(scroll_frame, fg_color=row_color, height=50)
            loc_frame.grid(row=row, column=2, sticky="nsew", padx=1, pady=1)
            ctk.CTkLabel(
                loc_frame,
                text=location,
                font=("Arial", 11),
                text_color="#2c3e50",
                anchor="w"
            ).pack(expand=True, fill="both", padx=5, pady=5)

            # Description column
            desc_frame = ctk.CTkFrame(scroll_frame, fg_color=row_color, height=50)
            desc_frame.grid(row=row, column=3, sticky="nsew", padx=1, pady=1)
            ctk.CTkLabel(
                desc_frame,
                text=description[:50] + "..." if len(description) > 50 else description,
                font=("Arial", 11),
                text_color="#2c3e50",
                anchor="w",
                wraplength=200
            ).pack(expand=True, fill="both", padx=5, pady=5)

            # Photo column
            photo_frame = ctk.CTkFrame(scroll_frame, fg_color=row_color, height=50)
            photo_frame.grid(row=row, column=4, sticky="nsew", padx=1, pady=1)
            if photo_path:
                photo_btn = ctk.CTkButton(
                    photo_frame,
                    text="View Photo",
                    width=80,
                    height=30,
                    command=partial(self.open_photo, path=photo_path),
                    fg_color="#27ae60",
                    hover_color="#219653",
                    font=("Arial", 10)
                )
                photo_btn.pack(expand=True, padx=5, pady=5)
            else:
                ctk.CTkLabel(
                    photo_frame,
                    text="No Photo",
                    font=("Arial", 11),
                    text_color="#7f8c8d"
                ).pack(expand=True, fill="both", padx=5, pady=5)

            # Status column
            status_frame = ctk.CTkFrame(scroll_frame, fg_color=row_color, height=50)
            status_frame.grid(row=row, column=5, sticky="nsew", padx=1, pady=1)

            # Color mapping for status
            status_colors = {
                "pending": "#e74c3c",
                "in progress": "#f39c12",
                "resolved": "#2ecc71"
            }

            status_menu = ctk.CTkOptionMenu(
                status_frame,
                values=["pending", "in progress", "resolved"],
                command=partial(self.change_status, report_id),
                fg_color=status_colors.get(status, "#3498db"),
                button_color=status_colors.get(status, "#2980b9"),
                button_hover_color=status_colors.get(status, "#2980b9"),
                dropdown_fg_color="#ffffff",
                dropdown_text_color="#2c3e50",
                dropdown_hover_color="#ecf0f1",
                font=("Arial", 11)
            )
            status_menu.set(status)
            status_menu.pack(expand=True, fill="both", padx=5, pady=5)

            # Timestamp column
            time_frame = ctk.CTkFrame(scroll_frame, fg_color=row_color, height=50)
            time_frame.grid(row=row, column=6, sticky="nsew", padx=1, pady=1)
            ctk.CTkLabel(
                time_frame,
                text=timestamp,
                font=("Arial", 11),
                text_color="#2c3e50"
            ).pack(expand=True, fill="both", padx=5, pady=5)

    def change_status(self, report_id, new_status):
        update_status(report_id, new_status)
        messagebox.showinfo(
            "Status Updated",
            f"Report ID {report_id} status changed to '{new_status}'",
            parent=self
        )
        self.display_dashboard_data()

    def open_photo(self, path):
        try:
            photo_window = ctk.CTkToplevel(self)
            photo_window.title("Report Photo")
            photo_window.geometry("800x600")
            photo_window.resizable(True, True)
            photo_window.protocol("WM_DELETE_WINDOW", lambda: self.close_photo_window(photo_window))

            # Make sure the photo window stays on top of the admin panel
            photo_window.transient(self)  # Set as transient window
            photo_window.grab_set()  # Grab focus
            photo_window.lift()  # Bring to top

            # Load image
            img = Image.open(path)
            img.thumbnail((750, 550))  # Resize maintaining aspect ratio

            # Create CTkImage
            ctk_image = ctk.CTkImage(
                light_image=img,
                dark_image=img,
                size=img.size
            )

            # Display image
            img_frame = ctk.CTkFrame(photo_window)
            img_frame.pack(expand=True, fill="both", padx=10, pady=10)

            img_label = ctk.CTkLabel(img_frame, text="", image=ctk_image)
            img_label.pack(expand=True)

            # Keep references
            photo_window.image_reference = ctk_image
            photo_window.img_label = img_label

            # Close button
            close_btn = ctk.CTkButton(
                photo_window,
                text="Close",
                command=lambda: self.close_photo_window(photo_window),
                fg_color="#e74c3c",
                hover_color="#c0392b"
            )
            close_btn.pack(pady=10)

        except Exception as e:
            messagebox.showerror("Error", f"Cannot open image: {e}", parent=self)

    def close_photo_window(self, window):
        """Properly clean up photo window"""
        if hasattr(window, 'image_reference'):
            del window.image_reference
        if hasattr(window, 'img_label'):
            window.img_label.destroy()
        window.destroy()
