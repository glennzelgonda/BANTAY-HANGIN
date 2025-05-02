import customtkinter as ctk
import tkinter.messagebox as messagebox
import admin_panel

VALID_USERNAME = "admin"
VALID_PASSWORD = "admin123"

class AdminLogin(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("BantayUsok - Admin Login")
        self.geometry("400x300")
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        ctk.CTkLabel(self, text="Admin Login", font=("Arial", 20, "bold")).pack(pady=20)

        self.username_entry = ctk.CTkEntry(self, placeholder_text="Username")
        self.username_entry.pack(pady=10)

        self.password_entry = ctk.CTkEntry(self, placeholder_text="Password", show="*")
        self.password_entry.pack(pady=10)

        ctk.CTkButton(self, text="Login", command=self.verify_login).pack(pady=20)

    def verify_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username == VALID_USERNAME and password == VALID_PASSWORD:
            messagebox.showinfo("Login Success", "Welcome, Admin!")
            self.withdraw()
            admin_panel.AdminPanel(master=self)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

if __name__ == "__main__":
    app = AdminLogin()
    app.mainloop()
