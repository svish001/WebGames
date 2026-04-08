import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import string
import secrets
import subprocess
from cryptography.fernet import Fernet, InvalidToken
from PIL import Image, ImageTk


class PasswordManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Manager 🔐")
        self.root.geometry("540x540")
        self.root.minsize(500, 650)
        self.photo = None

        self.base_dir = Path(__file__).resolve().parent
        self.key_path = self.base_dir / "key.key"
        self.background_image_path = self.base_dir / "wp3594884.jpg"
        lower_passwords = self.base_dir / "passwords.txt"
        upper_passwords = self.base_dir / "passwords.TXT"
        self.passwords_path = upper_passwords if upper_passwords.exists() else lower_passwords

        self.theme = {
            "panel": "#F8F3E6",
            "title": "#193549",
            "text": "#1F2933",
            "button_primary": "#1C7C54",
            "button_secondary": "#276FBF",
            "button_text": "#111827",
        }

        self.fer = Fernet(self.load_or_create_key())
        self.ensure_passwords_file()
        self.setup_ui()
        self.refresh_passwords(show_decrypted=False)

    def load_or_create_key(self):
        if not self.key_path.exists():
            key = Fernet.generate_key()
            self.key_path.write_bytes(key)
            return key
        return self.key_path.read_bytes()

    def ensure_passwords_file(self):
        if not self.passwords_path.exists():
            self.passwords_path.touch()

    def _draw_gradient_background(self, width, height):
        canvas = tk.Canvas(self.root, highlightthickness=0)
        canvas.place(x=0, y=0, relwidth=1, relheight=1)

        start_rgb = (14, 36, 58)
        end_rgb = (81, 45, 92)
        for i in range(max(height, 1)):
            r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * i / height)
            g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * i / height)
            b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * i / height)
            canvas.create_line(0, i, width, i, fill=f"#{r:02x}{g:02x}{b:02x}")

        canvas.create_oval(-120, -120, 260, 260, fill="#FFB703", outline="")
        canvas.create_oval(width - 230, 80, width + 120, 420, fill="#8ECAE6", outline="")
        canvas.create_oval(80, height - 180, 420, height + 120, fill="#FB8500", outline="")

    def set_background(self):
        width = self.root.winfo_width() if self.root.winfo_width() > 1 else 540
        height = self.root.winfo_height() if self.root.winfo_height() > 1 else 540

        try:
            img = Image.open(self.background_image_path)
            img = img.resize((width, height), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(img)
            bg_label = tk.Label(self.root, image=self.photo)
            bg_label.image = self.photo
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception:
            self._draw_gradient_background(width, height)

    def setup_ui(self):
        self.set_background()

        self.main_frame = tk.Frame(self.root, bg=self.theme["panel"], relief=tk.RAISED, bd=3)
        self.main_frame.pack(expand=True, padx=28, pady=28, fill=tk.BOTH)

        self.title_label = tk.Label(
            self.main_frame,
            text="Password Vault 🔐",
            font=("Avenir", 30, "bold"),
            bg=self.theme["panel"],
            fg=self.theme["title"],
        )
        self.title_label.pack(pady=(18, 8))

        self.status_label = tk.Label(
            self.main_frame,
            text=f"File: {self.passwords_path.name} 📁 | Display: Hidden 🔒",
            font=("Avenir", 11),
            bg=self.theme["panel"],
            fg="#8B5E34",
        )
        self.status_label.pack(pady=(0, 10))

        form_frame = tk.Frame(self.main_frame, bg=self.theme["panel"])
        form_frame.pack(fill=tk.X, padx=8, pady=(0, 10))

        tk.Label(
            form_frame,
            text="Account 🧾",
            font=("Avenir", 11, "bold"),
            bg=self.theme["panel"],
            fg=self.theme["text"],
        ).grid(row=0, column=0, sticky="w", pady=4)

        self.account_entry = tk.Entry(form_frame, font=("Avenir", 11), width=28)
        self.account_entry.grid(row=0, column=1, sticky="ew", pady=4, padx=(8, 0))

        tk.Label(
            form_frame,
            text="Username 👤",
            font=("Avenir", 11, "bold"),
            bg=self.theme["panel"],
            fg=self.theme["text"],
        ).grid(row=1, column=0, sticky="w", pady=4)

        self.username_entry = tk.Entry(form_frame, font=("Avenir", 11), width=28)
        self.username_entry.grid(row=1, column=1, sticky="ew", pady=4, padx=(8, 0))

        tk.Label(
            form_frame,
            text="Password 🔑",
            font=("Avenir", 11, "bold"),
            bg=self.theme["panel"],
            fg=self.theme["text"],
        ).grid(row=2, column=0, sticky="w", pady=4)

        self.password_entry = tk.Entry(form_frame, font=("Avenir", 11), width=28, show="*")
        self.password_entry.grid(row=2, column=1, sticky="ew", pady=4, padx=(8, 0))

        form_frame.columnconfigure(1, weight=1)

        actions = tk.Frame(self.main_frame, bg=self.theme["panel"])
        actions.pack(fill=tk.X, padx=8, pady=(0, 10))

        self.add_button = tk.Button(
            actions,
            text="Add Password ➕",
            command=self.add_password,
            bg=self.theme["button_primary"],
            fg=self.theme["button_text"],
            font=("Avenir", 11, "bold"),
            padx=14,
            pady=8,
            relief=tk.RAISED,
            bd=2,
            activebackground="#166846",
            activeforeground=self.theme["button_text"],
            cursor="hand2",
        )
        self.add_button.pack(side=tk.LEFT, padx=(0, 8))

        self.show_button = tk.Button(
            actions,
            text="Show Passwords 👀",
            command=self.show_decrypted_passwords,
            bg=self.theme["button_secondary"],
            fg=self.theme["button_text"],
            font=("Avenir", 11, "bold"),
            padx=14,
            pady=8,
            relief=tk.RAISED,
            bd=2,
            activebackground="#1D4F91",
            activeforeground=self.theme["button_text"],
            cursor="hand2",
        )
        self.show_button.pack(side=tk.LEFT)

        self.open_file_button = tk.Button(
            actions,
            text="Open TXT File 📂",
            command=self.open_passwords_file,
            bg="#F59E0B",
            fg=self.theme["button_text"],
            font=("Avenir", 11, "bold"),
            padx=14,
            pady=8,
            relief=tk.RAISED,
            bd=2,
            activebackground="#D97706",
            activeforeground=self.theme["button_text"],
            cursor="hand2",
        )
        self.open_file_button.pack(side=tk.LEFT, padx=(8, 0))

        self.generate_button = tk.Button(
            actions,
            text="Generate Password 🎲",
            command=self.generate_password,
            bg="#8B5CF6",
            fg=self.theme["button_text"],
            font=("Avenir", 11, "bold"),
            padx=14,
            pady=8,
            relief=tk.RAISED,
            bd=2,
            activebackground="#7C3AED",
            activeforeground=self.theme["button_text"],
            cursor="hand2",
        )
        self.generate_button.pack(side=tk.LEFT, padx=(8, 0))

        self.text_area = tk.Text(
            self.main_frame,
            height=13,
            font=("Avenir", 11),
            bg="#FFFDF7",
            fg="#1F2933",
            relief=tk.SUNKEN,
            bd=2,
            wrap=tk.WORD,
            state=tk.DISABLED,
        )
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 10))

        bottom_actions = tk.Frame(self.main_frame, bg=self.theme["panel"])
        bottom_actions.pack(fill=tk.X, padx=8, pady=(0, 6))

        self.hide_button = tk.Button(
            bottom_actions,
            text="Hide Passwords 🙈",
            command=self.hide_passwords,
            bg="#EF4444",
            fg=self.theme["button_text"],
            font=("Avenir", 11, "bold"),
            padx=14,
            pady=8,
            relief=tk.RAISED,
            bd=2,
            activebackground="#DC2626",
            activeforeground=self.theme["button_text"],
            cursor="hand2",
        )
        self.hide_button.pack(side=tk.RIGHT)

        self.root.bind("<Return>", lambda _event: self.add_password())

    def show_decrypted_passwords(self):
        self.refresh_passwords(show_decrypted=True)
        self.status_label.config(
            text=f"File: {self.passwords_path.name} 📁 | Display: Decrypted 👀"
        )

    def hide_passwords(self):
        self.refresh_passwords(show_decrypted=False)
        self.status_label.config(
            text=f"File: {self.passwords_path.name} 📁 | Display: Hidden 🔒"
        )

    def open_passwords_file(self):
        try:
            # macOS command to open the file in the default app.
            subprocess.run(["open", str(self.passwords_path)], check=False)
            self.status_label.config(
                text=f"Opened: {self.passwords_path.name} 📂 | Display: Hidden 🔒"
            )
        except Exception as exc:
            messagebox.showerror("Open Failed", f"Could not open file:\n{exc}")

    def generate_password(self):
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*()_-+="
        generated = "".join(secrets.choice(alphabet) for _ in range(14))
        self.password_entry.delete(0, tk.END)
        self.password_entry.insert(0, generated)
        self.status_label.config(
            text=f"Generated secure password 🎲 | File: {self.passwords_path.name} 📁 | Display: Hidden 🔒"
        )

    def add_password(self):
        account = self.account_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not account or not username or not password:
            messagebox.showerror("Missing Data", "Please enter account, username, and password.")
            return

        encrypted = self.fer.encrypt(password.encode("utf-8")).decode("utf-8")
        with self.passwords_path.open("a", encoding="utf-8") as f:
            f.write(f"{account}|{username}|{encrypted}\n")

        self.account_entry.delete(0, tk.END)
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.account_entry.focus()
        self.refresh_passwords(show_decrypted=False)
        self.status_label.config(
            text=f"File: {self.passwords_path.name} 📁 | Display: Hidden 🔒"
        )
        messagebox.showinfo("Saved ✅", "Password added successfully.")

    def refresh_passwords(self, show_decrypted=False):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete("1.0", tk.END)
        if show_decrypted:
            self.text_area.insert(tk.END, "Decrypted credentials shown below:\n\n")
        else:
            self.text_area.insert(tk.END, "Encrypted credentials shown below (password hidden):\n\n")

        lines = self.passwords_path.read_text(encoding="utf-8").splitlines()
        if not lines:
            self.text_area.insert(tk.END, "No saved passwords yet. Add one above. ✨")
            self.text_area.config(state=tk.DISABLED)
            return

        for index, line in enumerate(lines, start=1):
            parts = line.split("|")
            if len(parts) not in (2, 3):
                self.text_area.insert(tk.END, f"{index}. Skipped invalid line\n")
                continue

            if len(parts) == 3:
                account, username, encrypted = parts
            else:
                # Backward compatibility for old format: account|encrypted_password
                account, encrypted = parts
                username = "-"

            if show_decrypted:
                try:
                    decrypted = self.fer.decrypt(encrypted.encode("utf-8")).decode("utf-8")
                except (InvalidToken, ValueError):
                    decrypted = "<unable to decrypt>"

                self.text_area.insert(
                    tk.END,
                    f"{index}. Account: {account} | Username: {username} | Password: {decrypted}\n",
                )
            else:
                self.text_area.insert(
                    tk.END,
                    f"{index}. Account: {account} | Username: {username} | Password: ******** | Encrypted: {encrypted}\n",
                )

        self.text_area.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordManagerApp(root)
    root.mainloop()