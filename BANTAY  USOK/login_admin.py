import customtkinter as ctk
import admin_panel

VALID_USERNAME = "admin"
VALID_PASSWORD = "admin123"

class AdminLogin(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("BantayHangin - Admin Login")
        self.geometry("400x300")
        self.resizable(False, False)
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.show_password = False

        login_frame = ctk.CTkFrame(self, corner_radius=10)
        login_frame.pack(pady=20, padx=20, fill="both", expand=True)

        ctk.CTkLabel(login_frame, text="🔒 Admin Login", font=("Arial", 20, "bold")).pack(pady=(15, 10))

        self.username_entry = ctk.CTkEntry(login_frame, placeholder_text="Username", width=240)
        self.username_entry.pack(pady=(5, 10))

        password_frame = ctk.CTkFrame(login_frame, fg_color="transparent")
        password_frame.pack(pady=(0, 10))

        self.password_entry = ctk.CTkEntry(password_frame, placeholder_text="Password", show="*", width=190)
        self.password_entry.pack(side="left", padx=(0, 5))

        self.eye_button = ctk.CTkButton(password_frame, text="👁️", width=30, command=self.toggle_password)
        self.eye_button.pack(side="left")

        ctk.CTkButton(login_frame, text="Login", command=self.login, width=240).pack(pady=(0, 10))

        self.status_label = ctk.CTkLabel(login_frame, text="", text_color="red")
        self.status_label.pack()

    def toggle_password(self):
        self.show_password = not self.show_password
        self.password_entry.configure(show="" if self.show_password else "*")
        self.eye_button.configure(text="🙈" if self.show_password else "👁️")

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if username == VALID_USERNAME and password == VALID_PASSWORD:
            self.status_label.configure(text="Login successful!", text_color="green")
            self.after(100, self.open_admin_panel)
        else:
            self.status_label.configure(text="Invalid credentials", text_color="red")

    def open_admin_panel(self):
        self.destroy()
        admin_panel.AdminPanel().mainloop()

if __name__ == "__main__":
    AdminLogin().mainloop()
