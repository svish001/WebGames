import random
import math
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk


class NumberGuessingGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Number Guessing Game")
        self.root.geometry("540x540")
        self.root.minsize(480, 620)
        self.guesses = 0
        self.random_number = None
        self.top_of_range = None
        self.photo = None
        self.best_score = None
        self.recent_guesses = []
        self.target_attempts = 0
        self.background_image_path = Path(__file__).with_name("wp3594884.jpg")

        self.theme = {
            "panel": "#F8F3E6",
            "title": "#193549",
            "accent": "#D94F4F",
            "text": "#1F2933",
            "button_primary": "#1C7C54",
            "button_secondary": "#276FBF",
            "button_danger": "#B83B5E",
            "button_text": "#111827",
        }

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure(
            "Score.Horizontal.TProgressbar",
            troughcolor="#E5E7EB",
            background="#F59E0B",
            bordercolor="#D1D5DB",
            lightcolor="#F59E0B",
            darkcolor="#D97706",
        )
        
        self.setup_initial_screen()

    def _draw_gradient_background(self, width, height):
        canvas = tk.Canvas(self.root, highlightthickness=0)
        canvas.place(x=0, y=0, relwidth=1, relheight=1)

        start_rgb = (14, 36, 58)
        end_rgb = (81, 45, 92)
        steps = max(height, 1)
        for i in range(steps):
            r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * i / steps)
            g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * i / steps)
            b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * i / steps)
            color = f"#{r:02x}{g:02x}{b:02x}"
            canvas.create_line(0, i, width, i, fill=color)

        # Decorative circles make the background feel less flat.
        canvas.create_oval(-120, -120, 260, 260, fill="#FFB703", outline="")
        canvas.create_oval(width - 230, 80, width + 120, 420, fill="#8ECAE6", outline="")
        canvas.create_oval(80, height - 180, 420, height + 120, fill="#FB8500", outline="")

    def set_background(self):
        width = self.root.winfo_width() if self.root.winfo_width() > 1 else 540
        height = self.root.winfo_height() if self.root.winfo_height() > 1 else 540

        # Try to load a background image, or draw a gradient fallback.
        try:
            bg_label = tk.Label(self.root, image=self.photo)
            bg_label.image = self.photo
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception:
            self._draw_gradient_background(width, height)

    def setup_initial_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.set_background()

        frame = tk.Frame(self.root, bg=self.theme["panel"], relief=tk.RAISED, bd=3)
        frame.pack(expand=True, padx=38, pady=38, fill=tk.BOTH)

        tk.Label(
            frame,
            text="Number Guessing Game",
            font=("Avenir", 34, "bold"),
            bg=self.theme["panel"],
            fg=self.theme["title"],
        ).pack(pady=(28, 8))

        tk.Label(
            frame,
            text="Pick the maximum number for this round",
            font=("Avenir", 16),
            bg=self.theme["panel"],
            fg=self.theme["text"],
        ).pack(pady=8)

        self.entry = tk.Entry(
            frame,
            font=("Avenir", 20),
            width=18,
            relief=tk.SUNKEN,
            bd=3,
            justify="center",
        )
        self.entry.pack(pady=10)
        self.entry.focus()

        tk.Label(
            frame,
            text="Tip: try 100 for a balanced challenge",
            font=("Avenir", 12, "italic"),
            bg=self.theme["panel"],
            fg=self.theme["accent"],
        ).pack(pady=(8, 20))

        tk.Button(
            frame,
            text="Start Game",
            command=self.start_game,
            bg=self.theme["button_primary"],
            fg=self.theme["button_text"],
            font=("Avenir", 16, "bold"),
            padx=28,
            pady=14,
            relief=tk.RAISED,
            bd=2,
            activebackground="#166846",
            activeforeground=self.theme["button_text"],
            cursor="hand2",
        ).pack(pady=12)

        tk.Label(
            frame,
            text="Press Enter to start quickly",
            font=("Avenir", 11),
            bg=self.theme["panel"],
            fg="#4B5563",
        ).pack(pady=(6, 20))

        self.entry.bind("<Return>", lambda _event: self.start_game())
    
    def start_game(self):
        try:
            self.top_of_range = int(self.entry.get())
            if self.top_of_range < 2:
                messagebox.showerror("Invalid Input", "Please enter a number larger than 1")
                return

            self.random_number = random.randint(1, self.top_of_range)
            self.guesses = 0
            self.recent_guesses = []
            self.target_attempts = max(1, math.ceil(math.log2(self.top_of_range)))
            self.setup_game_screen()
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number")

    def _start_new_round_same_range(self):
        self.random_number = random.randint(1, self.top_of_range)
        self.guesses = 0
        self.recent_guesses = []
        self.feedback.config(text="New round started. Good luck!", fg="#0F766E")
        self.guess_count.config(text="Guesses: 0")
        self.recent_label.config(text="Recent guesses: -")
        self.score_meter["value"] = 0
        self.guess_entry.delete(0, tk.END)
        self.guess_entry.focus()

    def _update_recent_guesses(self, guess):
        self.recent_guesses.append(guess)
        self.recent_guesses = self.recent_guesses[-6:]
        history = ", ".join(str(value) for value in self.recent_guesses)
        self.recent_label.config(text=f"Recent guesses: {history}")

    def setup_game_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.set_background()

        frame = tk.Frame(self.root, bg=self.theme["panel"], relief=tk.RAISED, bd=3)
        frame.pack(expand=True, padx=38, pady=38, fill=tk.BOTH)

        tk.Label(
            frame,
            text="Make Your Guess",
            font=("Avenir", 30, "bold"),
            bg=self.theme["panel"],
            fg=self.theme["button_secondary"],
        ).pack(pady=(24, 8))

        tk.Label(
            frame,
            text=f"Range: 1 to {self.top_of_range}",
            font=("Avenir", 16),
            bg=self.theme["panel"],
            fg=self.theme["text"],
        ).pack(pady=4)

        tk.Label(
            frame,
            text=f"Smart target: {self.target_attempts} guesses or less",
            font=("Avenir", 12, "italic"),
            bg=self.theme["panel"],
            fg="#8B5E34",
        ).pack(pady=(0, 12))

        self.guess_entry = tk.Entry(
            frame,
            font=("Avenir", 20),
            width=18,
            relief=tk.SUNKEN,
            bd=3,
            justify="center",
        )
        self.guess_entry.pack(pady=10)
        self.guess_entry.focus()

        self.feedback = tk.Label(
            frame,
            text="",
            font=("Avenir", 14, "bold"),
            fg="#1D4ED8",
            bg=self.theme["panel"],
            wraplength=520,
            justify="center",
        )
        self.feedback.pack(pady=10)

        self.guess_count = tk.Label(
            frame,
            text="Guesses: 0",
            font=("Avenir", 14, "bold"),
            bg=self.theme["panel"],
            fg="#B45309",
        )
        self.guess_count.pack(pady=5)

        self.score_meter = ttk.Progressbar(
            frame,
            style="Score.Horizontal.TProgressbar",
            mode="determinate",
            maximum=max(10, self.target_attempts * 2),
            length=420,
        )
        self.score_meter.pack(pady=10)

        self.recent_label = tk.Label(
            frame,
            text="Recent guesses: -",
            font=("Avenir", 12),
            bg=self.theme["panel"],
            fg="#374151",
        )
        self.recent_label.pack(pady=(4, 14))

        tk.Button(
            frame,
            text="Submit Guess",
            command=self.check_guess,
            bg=self.theme["button_secondary"],
            fg=self.theme["button_text"],
            font=("Avenir", 14, "bold"),
            padx=24,
            pady=11,
            relief=tk.RAISED,
            bd=2,
            activebackground="#1D4F91",
            activeforeground=self.theme["button_text"],
            cursor="hand2",
        ).pack(pady=8)

        tk.Button(
            frame,
            text="New Game",
            command=self.reset,
            bg=self.theme["button_danger"],
            fg=self.theme["button_text"],
            font=("Avenir", 14, "bold"),
            padx=24,
            pady=11,
            relief=tk.RAISED,
            bd=2,
            activebackground="#8A2241",
            activeforeground=self.theme["button_text"],
            cursor="hand2",
        ).pack(pady=5)

        tk.Label(
            frame,
            text="Enter = submit, Esc = restart",
            font=("Avenir", 11),
            bg=self.theme["panel"],
            fg="#4B5563",
        ).pack(pady=(8, 12))

        self.guess_entry.bind("<Return>", lambda _event: self.check_guess())
        self.root.bind("<Escape>", lambda _event: self.reset())
    
    def check_guess(self):
        try:
            user_guess = int(self.guess_entry.get())

            if user_guess < 1 or user_guess > self.top_of_range:
                messagebox.showerror("Out of Range", f"Guess a number between 1 and {self.top_of_range}")
                self.guess_entry.delete(0, tk.END)
                self.guess_entry.focus()
                return

            self.guesses += 1
            self.guess_count.config(text=f"Guesses: {self.guesses}")
            self.score_meter["value"] = min(self.guesses, self.score_meter["maximum"])
            self._update_recent_guesses(user_guess)

            if user_guess == self.random_number:
                if self.best_score is None or self.guesses < self.best_score:
                    self.best_score = self.guesses

                best = f"Best score: {self.best_score}"
                messagebox.showinfo("Success", f"Great job! You got it in {self.guesses} guesses.\n{best}")

                same_range = messagebox.askyesno(
                    "Play Again",
                    "Play another round with the same range?",
                )
                if same_range:
                    self._start_new_round_same_range()
                else:
                    self.reset()
            elif user_guess > self.random_number:
                diff = user_guess - self.random_number
                self.feedback.config(text=f"Too high by {diff}. Try a smaller number.", fg="#B91C1C")
            else:
                diff = self.random_number - user_guess
                self.feedback.config(text=f"Too low by {diff}. Try a bigger number.", fg="#047857")

            self.guess_entry.delete(0, tk.END)
            self.guess_entry.focus()
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number")
            self.guess_entry.delete(0, tk.END)
            self.guess_entry.focus()
    
    def reset(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.unbind("<Escape>")
        self.setup_initial_screen()

if __name__ == "__main__":
    root = tk.Tk()
    game = NumberGuessingGame(root)
    root.mainloop()
