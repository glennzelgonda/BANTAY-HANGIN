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


class AnimatedGIF(ctk.CTkLabel):
    def __init__(self, master, gif_path, size=(1400, 600)):
        self.frames = []
        self.load_frames(gif_path, size)
        super().__init__(master, image=self.frames[0], text="")
        self.index = 0
        self.after(50, self.update_frame)

    def load_frames(self, gif_path, size):
        gif = Image.open(gif_path)
        try:
            while True:
                frame = gif.copy().resize(size)
                self.frames.append(ImageTk.PhotoImage(frame))
                gif.seek(len(self.frames))
        except EOFError:
            pass

    def update_frame(self):
        self.index = (self.index + 1) % len(self.frames)
        self.configure(image=self.frames[self.index])
        self.after(100, self.update_frame)

class BantayUsokApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("BantayHangin - Alisto Kontra Polusyon")
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{int(screen_width * 0.8)}x{int(screen_height * 0.8)}")
        self.minsize(int(screen_width * 0.7), int(screen_height * 0.7))

        self.photo_path = None

        main_container = ctk.CTkFrame(self)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        tabview = ctk.CTkTabview(main_container,fg_color="#a2c4c9",
            segmented_button_fg_color="#a2c4c9",
            segmented_button_selected_color="#839ea2",
            segmented_button_unselected_color="#a2c4c9",
            text_color="#545454")
        tabview.pack(fill="both", expand=True)

        self.report_tab = tabview.add("Report Smoke")
        self.dashboard_tab = tabview.add("Dashboard")

        self.build_report_tab()
        self.build_dashboard_tab()

        self.bind("<Configure>", self.on_window_resize)

        self.info_button = ctk.CTkButton(
            self,
            text="ℹ",
            command=self.show_info_module,
            width=30,
            height=30,
            fg_color="#309baa",
            corner_radius=1,
        )
        self.info_button.place(relx=0.99, rely=0.96, anchor="e")

    def show_info_module(self):
        info_window = ctk.CTkToplevel(self)
        info_window.title("Air Pollution Information")
        info_window.geometry("900x600")
        info_window.resizable(False, False)

        # Make the info window modal
        info_window.grab_set()
        info_window.focus()

        # Create and pack the styled tabview ONCE
        tabview = ctk.CTkTabview(
            info_window,
            fg_color="#8bb987",
            segmented_button_fg_color="#8bb987",
            segmented_button_selected_color="#538546",
            segmented_button_unselected_color="#8bb987",
            text_color="#545454"
        )
        tabview.pack(fill="both", expand=True, padx=10, pady=10)

        # Health Effects tab
        health_tab = tabview.add("Health Effects")
        health_tab.configure(fg_color="#8bb987")
        try:
            gif1 = AnimatedGIF(health_tab, "images/health.gif", size=(800, 500))
            gif1.pack(padx=10, pady=10)
        except Exception as e:
            ctk.CTkLabel(health_tab, text="GIF could not be loaded.", text_color="red").pack()

        # Add a description for the health tab
        ctk.CTkLabel(health_tab, text="Impact of air pollution on human health.", font=("Arial", 14),
                     text_color="white").pack(pady=10)

        # Ordinances tab
        ordinance_tab = tabview.add("Ordinances")
        ordinance_tab.configure(fg_color="#8bb987")
        try:
            gif2 = AnimatedGIF(ordinance_tab, "images/ordinance.gif", size=(600, 300))
            gif2.pack(padx=10, pady=10)
        except Exception as e:
            ctk.CTkLabel(ordinance_tab, text="GIF could not be loaded.", text_color="red").pack()

        # Add a description for the ordinances tab
        ctk.CTkLabel(ordinance_tab, text="Important ordinances addressing air pollution.", font=("Arial", 14),
                     text_color="white").pack(pady=10)

        # Clean Air Tips tab
        tips_tab = tabview.add("Clean Air Tips")
        tips_tab.configure(fg_color="#8bb987")
        try:
            gif3 = AnimatedGIF(tips_tab, "images/tips.gif", size=(800, 500))
            gif3.pack(padx=10, pady=10)
        except Exception as e:
            ctk.CTkLabel(tips_tab, text="GIF could not be loaded.", text_color="red").pack()

        # Add a description for the tips tab
        ctk.CTkLabel(tips_tab, text="Practical tips to reduce exposure to air pollution.", font=("Arial", 14),
                     text_color="white").pack(pady=10)

    def on_window_resize(self, event):
        if hasattr(self, 'canvas'):
            self.canvas.config(width=event.width, height=event.height)

    def animate_gif(self):
        self.current_frame = (self.current_frame + 1) % len(self.gif_frames)
        self.canvas.itemconfig(self.bg_image_id, image=self.gif_frames[self.current_frame])
        self.after(50, self.animate_gif)

    def build_report_tab(self):
        self.canvas = Canvas(self.report_tab, width=1400, height=650, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

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
        self.bg_image_id = self.canvas.create_image(0, 0, anchor="nw", image=self.gif_frames[0])
        self.animate_gif()

        form_frame = ctk.CTkFrame(master=self.canvas, fg_color="#a2c4c9", corner_radius=1)
        self.canvas.create_window(650, 400, window=form_frame, anchor="center")
        form_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(form_frame, text="Report", font=("Montserrat", 30, "bold"), text_color="#222").grid(row=0,
                column=0,pady=(10,20))

        # Name field - row 1
        ctk.CTkLabel(form_frame, text="Name:", text_color="#333", font=("Open Sans", 14)).grid(
            row=1, column=0, sticky="w", padx=20)
        self.name_entry = ctk.CTkEntry(form_frame, placeholder_text="Enter your name", font=("Open Sans", 13))
        self.name_entry.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Smoke Type - row 3 (changed from row 1)
        ctk.CTkLabel(form_frame, text="Smoke Type:", text_color="#333", font=("Open Sans", 14)).grid(
            row=3, column=0, sticky="w", padx=20)
        self.smoke_type = ctk.CTkOptionMenu(form_frame, values=["Cigarette", "Burning Trash", "Vehicle Emission"],
                                            button_color="#309baa", fg_color="#309baa", text_color="black")
        self.smoke_type.grid(row=4, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Location - row 5 (changed from row 3)
        ctk.CTkLabel(form_frame, text="Location (Barangay/Street):", text_color="#333", font=("Open Sans", 14)).grid(
            row=5, column=0, sticky="w", padx=20)
        self.location_entry = ctk.CTkEntry(form_frame, placeholder_text="e.g. Barangay 5, Mabini St.",
                                           font=("Open Sans", 13))
        self.location_entry.grid(row=6, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Description - row 7 (changed from row 5)
        ctk.CTkLabel(form_frame, text="Description:", text_color="#333", font=("Open Sans", 14)).grid(
            row=7, column=0, sticky="w", padx=20)
        self.description_entry = ctk.CTkTextbox(form_frame, height=100, font=("Open Sans", 13))
        self.description_entry.grid(row=8, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Buttons - row 9 and 10
        ctk.CTkButton(form_frame, text="Upload Photo", command=self.upload_photo, fg_color="#309baa").grid(
            row=9, column=0, padx=20, pady=(10, 5))
        ctk.CTkButton(form_frame, text="Submit Report", command=self.submit_report, fg_color="#309baa").grid(
            row=10, column=0, padx=20, pady=(5, 20))

    def upload_photo(self):
        file_path = fd.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if file_path:
            self.photo_path = file_path

    def submit_report(self):
        name = self.name_entry.get()
        smoke_type = self.smoke_type.get()
        location = self.location_entry.get()
        description = self.description_entry.get("1.0", "end").strip()

        if not name or not smoke_type or not location:
            messagebox.showerror("Error", "Please fill in all required fields.")
            return

        insert_report(name, smoke_type, location, description, self.photo_path)
        messagebox.showinfo("Success", "Report submitted successfully!")

        self.name_entry.delete(0, "end")
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
                if col_index == 3 and value:
                    open_photo = partial(self.open_photo, path=value)
                    view_button = ctk.CTkButton(data_frame, text="View Photo", width=100, command=open_photo)
                    view_button.grid(row=row_index, column=col_index, padx=10, pady=5)
                else:
                    label = ctk.CTkLabel(data_frame, text=str(value), font=("Arial", 12), text_color="black", anchor="w")
                    label.grid(row=row_index, column=col_index, padx=10, pady=5)

        canvas.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

    def display_summary(self):
        conn = sqlite3.connect("reports.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM reports")
        total_reports = cursor.fetchone()[0]

        cursor.execute("SELECT smoke_type, COUNT(*) FROM reports GROUP BY smoke_type")
        smoke_counts = cursor.fetchall()

        cursor.execute(
            "SELECT strftime('%Y-%m', timestamp) AS month, COUNT(*) FROM reports GROUP BY month ORDER BY month")
        monthly_trends = cursor.fetchall()

        cursor.execute("SELECT status, COUNT(*) FROM reports GROUP BY status")
        status_counts = cursor.fetchall()
        conn.close()

        # Create a frame for the summary section
        summary_frame = ctk.CTkFrame(self.dashboard_frame, fg_color="#f0f0f0", corner_radius=10)
        summary_frame.pack(fill="x", padx=10, pady=10, ipady=10)

        # Main title for summary
        ctk.CTkLabel(summary_frame,
                     text=f"📊 Dashboard Summary - Total Reports: {total_reports}",
                     font=("Arial", 16, "bold")).pack(pady=(5, 15))

        # Create columns container
        columns_frame = ctk.CTkFrame(summary_frame, fg_color="transparent")
        columns_frame.pack(fill="x", padx=10, pady=5)

        # Column 1: Smoke Types
        col1 = ctk.CTkFrame(columns_frame, fg_color="#e6f3f5", corner_radius=8)
        col1.pack(side="left", fill="both", expand=True, padx=5)

        ctk.CTkLabel(col1, text="🔥 Smoke Types",
                     font=("Arial", 14, "bold"),
                     text_color="#2c3e50").pack(pady=(10, 5))

        for smoke_type, count in smoke_counts:
            ctk.CTkLabel(col1,
                         text=f"• {smoke_type}: {count}",
                         font=("Arial", 12),
                         text_color="#34495e").pack(anchor="w", padx=20, pady=2)

        # Column 2: Monthly Trends
        col2 = ctk.CTkFrame(columns_frame, fg_color="#e6f3f5", corner_radius=8)
        col2.pack(side="left", fill="both", expand=True, padx=5)

        ctk.CTkLabel(col2, text="📅 Monthly Trends",
                     font=("Arial", 14, "bold"),
                     text_color="#2c3e50").pack(pady=(10, 5))

        for month, count in monthly_trends:
            ctk.CTkLabel(col2,
                         text=f"• {month}: {count} reports",
                         font=("Arial", 12),
                         text_color="#34495e").pack(anchor="w", padx=20, pady=2)

        # Column 3: Case Status
        col3 = ctk.CTkFrame(columns_frame, fg_color="#e6f3f5", corner_radius=8)
        col3.pack(side="left", fill="both", expand=True, padx=5)

        ctk.CTkLabel(col3, text="📌 Case Status",
                     font=("Arial", 14, "bold"),
                     text_color="#2c3e50").pack(pady=(10, 5))

        for status, count in status_counts:
            # Add color coding based on status
            color = "#27ae60" if status.lower() == "completed" else \
                "#f39c12" if status.lower() == "in progress" else \
                    "#e74c3c" if status.lower() == "pending" else "#34495e"

            ctk.CTkLabel(col3,
                         text=f"• {status.capitalize()}: {count}",
                         font=("Arial", 12),
                         text_color=color).pack(anchor="w", padx=20, pady=2)

        # Add some spacing at the bottom
        ctk.CTkLabel(summary_frame, text="").pack()

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

if __name__ == "__main__":
    init_db()
    app = BantayUsokApp()
    app.update_idletasks()

    screen_width = app.winfo_screenwidth()
    screen_height = app.winfo_screenheight()
    app.geometry(f"{screen_width}x{screen_height}+0+0")

    app.mainloop()
