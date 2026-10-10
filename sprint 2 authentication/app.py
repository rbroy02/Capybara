import tkinter as tk
from tkinter import messagebox

from auth import create_user_table, authenticate_user


# Make sure the database/table exists
create_user_table()

# --------------------------------------------------
# Login function
# --------------------------------------------------

def login():
    username = username_entry.get().strip()
    password = password_entry.get()

    # Required field check
    if not username or not password:
        messagebox.showerror(
            "Login Failed",
            "Username and password are required."
        )
        return

    # Check credentials
    if authenticate_user(username, password):
        messagebox.showinfo(
            "Login Successful",
            "Authentication successful."
        )

        login_frame.pack_forget()
        application_frame.pack(pady=40)

    else:
        messagebox.showerror(
            "Login Failed",
            "Invalid username or password."
        )

        password_entry.delete(0, tk.END)


# --------------------------------------------------
# Logout function
# --------------------------------------------------

def logout():
    application_frame.pack_forget()

    username_entry.delete(0, tk.END)
    password_entry.delete(0, tk.END)

    login_frame.pack(pady=40)


# --------------------------------------------------
# Window
# --------------------------------------------------

root = tk.Tk()

root.title("SPN pH Correction Skid Design Tool")
root.geometry("500x400")
root.resizable(False, False)


# --------------------------------------------------
# Login screen
# --------------------------------------------------

login_frame = tk.Frame(root)

title_label = tk.Label(
    login_frame,
    text="SPN Design Tool",
    font=("Arial", 22, "bold")
)
title_label.pack(pady=20)

subtitle_label = tk.Label(
    login_frame,
    text="User Login",
    font=("Arial", 14)
)
subtitle_label.pack(pady=10)


username_label = tk.Label(
    login_frame,
    text="Username"
)
username_label.pack()

username_entry = tk.Entry(
    login_frame,
    width=30
)
username_entry.pack(pady=5)


password_label = tk.Label(
    login_frame,
    text="Password"
)
password_label.pack()

password_entry = tk.Entry(
    login_frame,
    width=30,
    show="*"
)
password_entry.pack(pady=5)


login_button = tk.Button(
    login_frame,
    text="Login",
    width=15,
    command=login
)
login_button.pack(pady=20)

login_frame.pack(pady=40)


# --------------------------------------------------
# Protected application screen
# --------------------------------------------------

application_frame = tk.Frame(root)

welcome_label = tk.Label(
    application_frame,
    text="Login Successful",
    font=("Arial", 20, "bold")
)
welcome_label.pack(pady=15)

access_label = tk.Label(
    application_frame,
    text="Access granted to the SPN Design Tool."
)
access_label.pack(pady=10)

placeholder_label = tk.Label(
    application_frame,
    text="Main application will be integrated here."
)
placeholder_label.pack(pady=10)

logout_button = tk.Button(
    application_frame,
    text="Logout",
    width=15,
    command=logout
)
logout_button.pack(pady=20)


# Start application
root.mainloop()