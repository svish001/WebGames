import datetime as dt
import math
import random
import string
import tkinter as tk
from tkinter import messagebox

try:
    import pyperclip
except ImportError:
    pyperclip = None


COLORS = {
    "bg": (15, 25, 43),
    "bg2": (44, 28, 68),
    "panel": (248, 244, 233),
    "panel2": (237, 231, 216),
    "title": (21, 50, 72),
    "text": (34, 42, 56),
    "muted": (107, 115, 128),
    "good": (32, 138, 78),
    "warn": (217, 112, 46),
    "bad": (200, 65, 65),
    "accent2": (46, 125, 191),
    "white": (255, 255, 255),
}

SPECIAL_SET = "!@#$%^&*-_=+[]{}|;:,.<>?"
SIMILAR_CHARS = set("il1Lo0O")
APP_WIDTH = 980
APP_HEIGHT = 680


def rgb_to_hex(rgb):
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"


class CustomButton(tk.Canvas):
    def __init__(self, parent, text, color, hover_color, command, width=180, height=48):
        super().__init__(parent, width=width, height=height, bg=parent["bg"], highlightthickness=0)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.command = command
        self.width_val = width
        self.height_val = height
        self.is_hovered = False

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self._draw()

    def _on_enter(self, _):
        self.is_hovered = True
        self._draw()

    def _on_leave(self, _):
        self.is_hovered = False
        self._draw()

    def _on_click(self, _):
        self.command()

    def _draw(self):
        self.delete("all")
        color = self.hover_color if self.is_hovered else self.color
        self.create_rectangle(2, 4, self.width_val, self.height_val, fill="gray20", outline="")
        self.create_rectangle(
            0,
            0,
            self.width_val - 2,
            self.height_val - 4,
            fill=rgb_to_hex(color),
            outline=rgb_to_hex((40, 44, 52)),
            width=2,
        )
        self.create_text(
            self.width_val // 2,
            (self.height_val - 4) // 2,
            text=self.text,
            fill=rgb_to_hex(COLORS["white"]),
            font=("Avenir", 11, "bold"),
        )


class PasswordGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Generator Studio")
        self.root.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.root.configure(bg=rgb_to_hex(COLORS["bg"]))

        self.length_var = tk.IntVar(value=16)
        self.upper_var = tk.BooleanVar(value=True)
        self.lower_var = tk.BooleanVar(value=True)
        self.number_var = tk.BooleanVar(value=True)
        self.special_var = tk.BooleanVar(value=True)
        self.exclude_similar_var = tk.BooleanVar(value=True)
        self.no_sequential_var = tk.BooleanVar(value=False)
        self.memorable_var = tk.BooleanVar(value=False)
        self.purpose_var = tk.StringVar(value="general")

        self.generated_password = ""
        self.hidden = False
        self.status_var = tk.StringVar(value="Ready")
        self.password_history = []

        self.show_setup_screen()

    def _clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def _paint_background(self, canvas, width=APP_WIDTH, height=APP_HEIGHT):
        for y in range(height):
            t = y / max(1, height - 1)
            r = int(COLORS["bg"][0] + (COLORS["bg2"][0] - COLORS["bg"][0]) * t)
            g = int(COLORS["bg"][1] + (COLORS["bg2"][1] - COLORS["bg"][1]) * t)
            b = int(COLORS["bg"][2] + (COLORS["bg2"][2] - COLORS["bg"][2]) * t)
            canvas.create_line(0, y, width, y, fill=rgb_to_hex((r, g, b)))
        canvas.create_oval(-120, -70, 220, 250, fill="#ffb703", outline="")
        canvas.create_oval(760, 420, 1060, 800, fill="#8ecae6", outline="")

    def _panel_shell(self, title, subtitle):
        bg = tk.Canvas(self.root, width=APP_WIDTH, height=APP_HEIGHT, highlightthickness=0)
        bg.pack(fill=tk.BOTH, expand=True)
        self._paint_background(bg)

        panel = tk.Canvas(self.root, width=870, height=540, bg=rgb_to_hex(COLORS["panel"]), highlightthickness=0)
        panel.place(x=55, y=58)
        panel.create_rectangle(0, 4, 870, 540, fill="gray20", outline="")
        panel.create_rectangle(
            0,
            0,
            868,
            536,
            fill=rgb_to_hex(COLORS["panel"]),
            outline=rgb_to_hex((205, 190, 160)),
            width=2,
        )
        panel.create_text(32, 20, text=title, anchor="nw", fill=rgb_to_hex(COLORS["title"]), font=("Avenir", 32, "bold"))
        panel.create_text(32, 64, text=subtitle, anchor="nw", fill=rgb_to_hex(COLORS["muted"]), font=("Avenir", 13))
        return panel

    def show_setup_screen(self):
        self._clear()
        panel = self._panel_shell("Password Generator Studio", "Security-first generation with guided checks")

        body = tk.Frame(self.root, bg=rgb_to_hex(COLORS["panel"]))
        body.place(x=95, y=165, width=790, height=340)
        body.grid_columnconfigure(1, weight=1)

        tk.Label(body, text="Length", bg=rgb_to_hex(COLORS["panel"]), fg=rgb_to_hex(COLORS["title"]), font=("Avenir", 13, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 10))
        tk.Scale(
            body,
            from_=8,
            to=64,
            orient=tk.HORIZONTAL,
            variable=self.length_var,
            bg=rgb_to_hex(COLORS["panel"]),
            fg=rgb_to_hex(COLORS["accent2"]),
            highlightthickness=0,
            length=420,
        ).grid(row=0, column=1, sticky="w")

        tk.Label(body, text="Character Sets", bg=rgb_to_hex(COLORS["panel"]), fg=rgb_to_hex(COLORS["title"]), font=("Avenir", 13, "bold")).grid(row=1, column=0, sticky="nw", pady=(16, 6))
        set_box = tk.Frame(body, bg=rgb_to_hex(COLORS["panel2"]))
        set_box.grid(row=1, column=1, sticky="ew", pady=(16, 6))
        self._check(set_box, "Uppercase A-Z", self.upper_var)
        self._check(set_box, "Lowercase a-z", self.lower_var)
        self._check(set_box, "Digits 0-9", self.number_var)
        self._check(set_box, "Special symbols", self.special_var)

        tk.Label(body, text="Rules", bg=rgb_to_hex(COLORS["panel"]), fg=rgb_to_hex(COLORS["title"]), font=("Avenir", 13, "bold")).grid(row=2, column=0, sticky="nw", pady=(16, 6))
        rules = tk.Frame(body, bg=rgb_to_hex(COLORS["panel2"]))
        rules.grid(row=2, column=1, sticky="ew", pady=(16, 6))
        self._check(rules, "Exclude similar chars (i l 1 o 0)", self.exclude_similar_var)
        self._check(rules, "No sequential neighbors (ab, 78)", self.no_sequential_var)
        self._check(rules, "Memorable mode (alternating letters + digits)", self.memorable_var)

        tk.Label(body, text="Purpose", bg=rgb_to_hex(COLORS["panel"]), fg=rgb_to_hex(COLORS["title"]), font=("Avenir", 13, "bold")).grid(row=3, column=0, sticky="w", pady=(16, 0))
        purpose_menu = tk.OptionMenu(body, self.purpose_var, "general", "banking", "critical", "memorable")
        purpose_menu.config(bg=rgb_to_hex(COLORS["panel2"]), fg=rgb_to_hex(COLORS["text"]), relief=tk.FLAT, highlightthickness=0)
        purpose_menu.grid(row=3, column=1, sticky="w", pady=(16, 0))

        # Pre-generate gate to make flow interactive.
        checklist = tk.Frame(body, bg=rgb_to_hex(COLORS["panel2"]))
        checklist.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(20, 0))
        tk.Label(
            checklist,
            text="Pre-check: confirm this password is for you, not shared chat, and backup recovery is set.",
            bg=rgb_to_hex(COLORS["panel2"]),
            fg=rgb_to_hex(COLORS["muted"]),
            font=("Avenir", 11),
            wraplength=730,
            justify=tk.LEFT,
        ).pack(anchor="w", padx=10, pady=8)

        action_row = tk.Frame(self.root, bg=rgb_to_hex(COLORS["bg"]))
        action_row.place(x=95, y=560, width=790, height=52)
        CustomButton(action_row, "Generate", COLORS["good"], (38, 156, 87), self.generate_password, 170, 46).pack(side=tk.LEFT, padx=6)
        CustomButton(action_row, "History", COLORS["accent2"], (35, 141, 214), self.show_history_screen, 160, 46).pack(side=tk.LEFT, padx=6)
        tk.Label(action_row, textvariable=self.status_var, bg=rgb_to_hex(COLORS["bg"]), fg=rgb_to_hex(COLORS["white"]), font=("Avenir", 11)).pack(side=tk.RIGHT, padx=10)

    def _check(self, parent, text, variable):
        tk.Checkbutton(
            parent,
            text=text,
            variable=variable,
            bg=rgb_to_hex(COLORS["panel2"]),
            fg=rgb_to_hex(COLORS["text"]),
            selectcolor=rgb_to_hex(COLORS["panel"]),
            activebackground=rgb_to_hex(COLORS["panel2"]),
            font=("Avenir", 11),
            anchor="w",
        ).pack(fill=tk.X, padx=10, pady=3)

    def _pool(self):
        groups = []
        if self.upper_var.get():
            groups.append(string.ascii_uppercase)
        if self.lower_var.get():
            groups.append(string.ascii_lowercase)
        if self.number_var.get():
            groups.append(string.digits)
        if self.special_var.get():
            groups.append(SPECIAL_SET)

        if not groups:
            return [], ""

        if self.exclude_similar_var.get():
            cleaned = []
            for group in groups:
                cleaned_group = "".join(ch for ch in group if ch not in SIMILAR_CHARS)
                if cleaned_group:
                    cleaned.append(cleaned_group)
            groups = cleaned

        return groups, "".join(groups)

    def _purpose_min_len(self):
        mapping = {"general": 12, "banking": 16, "critical": 20, "memorable": 12}
        return mapping.get(self.purpose_var.get(), 12)

    def generate_password(self):
        groups, all_chars = self._pool()
        if not groups or not all_chars:
            messagebox.showwarning("Invalid Setup", "Enable at least one usable character set.")
            return

        length = self.length_var.get()
        min_len = self._purpose_min_len()
        if length < min_len:
            self.status_var.set(f"Length raised to {min_len} for {self.purpose_var.get()} profile")
            length = min_len
            self.length_var.set(min_len)

        required = [random.choice(group) for group in groups]
        if len(required) > length:
            messagebox.showwarning("Invalid Setup", "Length is too short for selected requirements.")
            return

        password_chars = required[:]
        attempts = 0
        while len(password_chars) < length and attempts < 2000:
            attempts += 1
            if self.memorable_var.get() and len(password_chars) % 2 == 0:
                candidate_pool = string.ascii_lowercase + string.ascii_uppercase
            elif self.memorable_var.get() and len(password_chars) % 2 == 1:
                candidate_pool = string.digits
            else:
                candidate_pool = all_chars

            candidate_pool = "".join(ch for ch in candidate_pool if ch in all_chars)
            if not candidate_pool:
                candidate_pool = all_chars

            ch = random.choice(candidate_pool)
            if self.no_sequential_var.get() and password_chars:
                prev = password_chars[-1]
                if abs(ord(ch) - ord(prev)) == 1:
                    continue
            password_chars.append(ch)

        random.shuffle(password_chars)
        self.generated_password = "".join(password_chars[:length])
        score, entropy, crack = self._strength(self.generated_password, all_chars)
        self.password_history.insert(
            0,
            {
                "password": self.generated_password,
                "created": dt.datetime.now().strftime("%H:%M:%S"),
                "purpose": self.purpose_var.get(),
                "score": score,
            },
        )
        self.status_var.set(f"Generated score {score}/100 | entropy {entropy:.1f} bits | crack {crack}")
        self.hidden = False
        self.show_result_screen()

    def _strength(self, password, all_chars):
        pool_size = max(len(set(all_chars)), 1)
        entropy = len(password) * math.log2(pool_size)
        score = max(0, min(100, int((entropy / 140.0) * 100)))
        guesses = 2 ** entropy
        # rough online attack model
        seconds = guesses / 1e10
        crack = self._format_duration(seconds)
        return score, entropy, crack

    def _format_duration(self, seconds):
        if seconds < 60:
            return "under a minute"
        if seconds < 3600:
            return f"{int(seconds // 60)} minutes"
        if seconds < 86400:
            return f"{int(seconds // 3600)} hours"
        if seconds < 86400 * 365:
            return f"{int(seconds // 86400)} days"
        years = seconds / (86400 * 365)
        if years < 1000:
            return f"{int(years)} years"
        return "thousands of years"

    def show_result_screen(self):
        self._clear()
        panel = self._panel_shell("Generated Password", "Review strength, copy securely, or regenerate")

        masked = "*" * len(self.generated_password)
        display_text = masked if self.hidden else self.generated_password

        pw_card = tk.Frame(self.root, bg=rgb_to_hex(COLORS["panel2"]))
        pw_card.place(x=120, y=180, width=740, height=90)
        self.password_label = tk.Label(
            pw_card,
            text=display_text,
            bg=rgb_to_hex(COLORS["panel2"]),
            fg=rgb_to_hex(COLORS["title"]),
            font=("Menlo", 22, "bold"),
            wraplength=700,
        )
        self.password_label.pack(expand=True)

        groups, all_chars = self._pool()
        score, entropy, crack = self._strength(self.generated_password, all_chars)
        bar_bg = tk.Frame(self.root, bg=rgb_to_hex(COLORS["panel2"]))
        bar_bg.place(x=120, y=305, width=320, height=16)
        color = COLORS["bad"] if score < 35 else COLORS["warn"] if score < 70 else COLORS["good"]
        tk.Frame(self.root, bg=rgb_to_hex(color)).place(x=120, y=305, width=max(4, int(score * 3.2)), height=16)

        meta = f"Score {score}/100    Entropy {entropy:.1f} bits    Estimated crack time {crack}"
        tk.Label(self.root, text=meta, bg=rgb_to_hex(COLORS["panel"]), fg=rgb_to_hex(COLORS["text"]), font=("Avenir", 11)).place(x=120, y=332)

        row = tk.Frame(self.root, bg=rgb_to_hex(COLORS["bg"]))
        row.place(x=120, y=560, width=740, height=52)
        CustomButton(row, "Copy", COLORS["accent2"], (35, 141, 214), self.copy_password, 130, 46).pack(side=tk.LEFT, padx=6)
        CustomButton(row, "Show/Hide", COLORS["warn"], (221, 111, 55), self.toggle_reveal, 140, 46).pack(side=tk.LEFT, padx=6)
        CustomButton(row, "Generate Again", COLORS["good"], (38, 156, 87), self.show_setup_screen, 180, 46).pack(side=tk.LEFT, padx=6)
        CustomButton(row, "History", COLORS["accent2"], (35, 141, 214), self.show_history_screen, 130, 46).pack(side=tk.LEFT, padx=6)

    def copy_password(self):
        if not self.generated_password:
            return
        try:
            if pyperclip is not None:
                pyperclip.copy(self.generated_password)
            else:
                self.root.clipboard_clear()
                self.root.clipboard_append(self.generated_password)
            self.status_var.set("Password copied to clipboard")
            messagebox.showinfo("Copied", "Password copied successfully.")
        except Exception as exc:
            messagebox.showerror("Copy Failed", f"Could not copy password: {exc}")

    def toggle_reveal(self):
        self.hidden = not self.hidden
        if self.generated_password:
            self.password_label.config(text=("*" * len(self.generated_password)) if self.hidden else self.generated_password)

    def show_history_screen(self):
        self._clear()
        self._panel_shell("Password History", "Latest first. Copy only what you need.")

        host = tk.Frame(self.root, bg=rgb_to_hex(COLORS["panel"]))
        host.place(x=95, y=165, width=790, height=340)
        canvas = tk.Canvas(host, bg=rgb_to_hex(COLORS["panel"]), highlightthickness=0)
        scroll = tk.Scrollbar(host, orient=tk.VERTICAL, command=canvas.yview)
        list_frame = tk.Frame(canvas, bg=rgb_to_hex(COLORS["panel"]))
        list_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=list_frame, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)

        if not self.password_history:
            tk.Label(list_frame, text="No passwords generated yet.", bg=rgb_to_hex(COLORS["panel"]), fg=rgb_to_hex(COLORS["muted"]), font=("Avenir", 13)).pack(pady=20)
        else:
            for item in self.password_history[:50]:
                row = tk.Frame(list_frame, bg=rgb_to_hex(COLORS["panel2"]))
                row.pack(fill=tk.X, padx=8, pady=4)
                text = f"{item['created']} | {item['purpose']} | score {item['score']}/100 | {item['password']}"
                tk.Label(row, text=text, bg=rgb_to_hex(COLORS["panel2"]), fg=rgb_to_hex(COLORS["title"]), font=("Menlo", 10), anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8, pady=8)
                tk.Button(
                    row,
                    text="Copy",
                    command=lambda p=item["password"]: self._copy_specific(p),
                    bg=rgb_to_hex(COLORS["accent2"]),
                    fg=rgb_to_hex(COLORS["white"]),
                    relief=tk.FLAT,
                    padx=12,
                ).pack(side=tk.RIGHT, padx=8, pady=6)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        row = tk.Frame(self.root, bg=rgb_to_hex(COLORS["bg"]))
        row.place(x=95, y=560, width=790, height=52)
        CustomButton(row, "Back", COLORS["accent2"], (35, 141, 214), self.show_setup_screen, 130, 46).pack(side=tk.LEFT, padx=6)

    def _copy_specific(self, value):
        try:
            if pyperclip is not None:
                pyperclip.copy(value)
            else:
                self.root.clipboard_clear()
                self.root.clipboard_append(value)
            messagebox.showinfo("Copied", "Password copied successfully.")
        except Exception as exc:
            messagebox.showerror("Copy Failed", f"Could not copy password: {exc}")


def main():
    root = tk.Tk()
    app = PasswordGeneratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
