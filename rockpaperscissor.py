import random
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk


class RockPaperScissorsGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Rock Paper Scissors")
        self.root.geometry("720x860")
        self.root.minsize(500, 600)

        self.photo = None
        self.options = ["rock", "paper", "scissors"]

        self.user_wins = 0
        self.computer_wins = 0
        self.draws = 0
        self.round_number = 0
        self.current_streak = 0
        self.best_streak = 0
        self.history = []

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

        self._build_ui()

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

    def _set_background(self):
        width = self.root.winfo_width() if self.root.winfo_width() > 1 else 720
        height = self.root.winfo_height() if self.root.winfo_height() > 1 else 860
        try:
            img = Image.open("wp3594884.jpg")
            img = img.resize((width, height), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(img)
            bg_label = tk.Label(self.root, image=self.photo)
            bg_label.image = self.photo
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception:
            self._draw_gradient_background(width, height)

    def _build_ui(self):
        self._set_background()

        self.frame = tk.Frame(self.root, bg=self.theme["panel"], relief=tk.RAISED, bd=3)
        self.frame.pack(expand=True, padx=38, pady=38, fill=tk.BOTH)

        tk.Label(
            self.frame,
            text="Rock Paper Scissors",
            font=("Avenir", 34, "bold"),
            bg=self.theme["panel"],
            fg=self.theme["title"],
        ).pack(pady=(24, 8))

        tk.Label(
            self.frame,
            text="Choose your move and beat the computer",
            font=("Avenir", 16),
            bg=self.theme["panel"],
            fg=self.theme["text"],
        ).pack(pady=(4, 14))

        self.round_label = tk.Label(
            self.frame,
            text="Round: 0",
            font=("Avenir", 14, "bold"),
            bg=self.theme["panel"],
            fg="#8B5E34",
        )
        self.round_label.pack(pady=(2, 6))

        self.score_label = tk.Label(
            self.frame,
            text="You: 0   Computer: 0   Draws: 0",
            font=("Avenir", 16, "bold"),
            bg=self.theme["panel"],
            fg=self.theme["button_secondary"],
        )
        self.score_label.pack(pady=6)

        self.streak_label = tk.Label(
            self.frame,
            text="Streak: 0   Best streak: 0",
            font=("Avenir", 13),
            bg=self.theme["panel"],
            fg="#374151",
        )
        self.streak_label.pack(pady=(2, 14))

        moves = tk.Frame(self.frame, bg=self.theme["panel"])
        moves.pack(pady=6)

        tk.Button(
            moves,
            text="Rock",
            command=lambda: self.play_round("rock"),
            bg=self.theme["button_secondary"],
            fg=self.theme["button_text"],
            font=("Avenir", 14, "bold"),
            padx=20,
            pady=10,
            relief=tk.RAISED,
            bd=2,
            activebackground="#1D4F91",
            activeforeground=self.theme["button_text"],
            cursor="hand2",
        ).grid(row=0, column=0, padx=8, pady=8)

        tk.Button(
            moves,
            text="Paper",
            command=lambda: self.play_round("paper"),
            bg=self.theme["button_primary"],
            fg=self.theme["button_text"],
            font=("Avenir", 14, "bold"),
            padx=20,
            pady=10,
            relief=tk.RAISED,
            bd=2,
            activebackground="#166846",
            activeforeground=self.theme["button_text"],
            cursor="hand2",
        ).grid(row=0, column=1, padx=8, pady=8)

        tk.Button(
            moves,
            text="Scissors",
            command=lambda: self.play_round("scissors"),
            bg=self.theme["button_danger"],
            fg=self.theme["button_text"],
            font=("Avenir", 14, "bold"),
            padx=20,
            pady=10,
            relief=tk.RAISED,
            bd=2,
            activebackground="#8A2241",
            activeforeground=self.theme["button_text"],
            cursor="hand2",
        ).grid(row=0, column=2, padx=8, pady=8)

        self.result_label = tk.Label(
            self.frame,
            text="Make your first move!",
            font=("Avenir", 15, "bold"),
            bg=self.theme["panel"],
            fg="#1D4ED8",
            wraplength=560,
            justify="center",
        )
        self.result_label.pack(pady=(14, 8))

        self.matchup_label = tk.Label(
            self.frame,
            text="You: -    Computer: -",
            font=("Avenir", 13),
            bg=self.theme["panel"],
            fg=self.theme["text"],
        )
        self.matchup_label.pack(pady=(0, 12))

        tk.Label(
            self.frame,
            text="Recent rounds",
            font=("Avenir", 14, "bold"),
            bg=self.theme["panel"],
            fg="#4B5563",
        ).pack(pady=(8, 4))

        self.history_box = tk.Text(
            self.frame,
            height=9,
            width=58,
            font=("Avenir", 11),
            state=tk.DISABLED,
            relief=tk.SUNKEN,
            bd=2,
            bg="#FFFDF7",
            fg="#1F2933",
        )
        self.history_box.pack(pady=(4, 12))

        actions = tk.Frame(self.frame, bg=self.theme["panel"])
        actions.pack(pady=4)

        tk.Button(
            actions,
            text="Reset Score",
            command=self.reset_score,
            bg="#D1D5DB",
            fg=self.theme["button_text"],
            font=("Avenir", 12, "bold"),
            padx=18,
            pady=10,
            relief=tk.RAISED,
            bd=2,
            activebackground="#9CA3AF",
            activeforeground=self.theme["button_text"],
            cursor="hand2",
        ).grid(row=0, column=0, padx=8)

        tk.Button(
            actions,
            text="Quit",
            command=self.confirm_quit,
            bg="#FCA5A5",
            fg=self.theme["button_text"],
            font=("Avenir", 12, "bold"),
            padx=24,
            pady=10,
            relief=tk.RAISED,
            bd=2,
            activebackground="#F87171",
            activeforeground=self.theme["button_text"],
            cursor="hand2",
        ).grid(row=0, column=1, padx=8)

        self.root.bind("<r>", lambda _event: self.play_round("rock"))
        self.root.bind("<p>", lambda _event: self.play_round("paper"))
        self.root.bind("<s>", lambda _event: self.play_round("scissors"))
        self.root.bind("<Escape>", lambda _event: self.confirm_quit())

    def _is_user_winner(self, user_pick, computer_pick):
        return (
            (user_pick == "rock" and computer_pick == "scissors")
            or (user_pick == "paper" and computer_pick == "rock")
            or (user_pick == "scissors" and computer_pick == "paper")
        )

    def _update_labels(self):
        self.round_label.config(text=f"Round: {self.round_number}")
        self.score_label.config(
            text=f"You: {self.user_wins}   Computer: {self.computer_wins}   Draws: {self.draws}"
        )
        self.streak_label.config(
            text=f"Streak: {self.current_streak}   Best streak: {self.best_streak}"
        )

    def _push_history(self, user_pick, computer_pick, outcome):
        line = f"Round {self.round_number}: You={user_pick} | Computer={computer_pick} | {outcome}\n"
        self.history.append(line)
        self.history = self.history[-10:]

        self.history_box.config(state=tk.NORMAL)
        self.history_box.delete("1.0", tk.END)
        self.history_box.insert(tk.END, "".join(self.history))
        self.history_box.config(state=tk.DISABLED)

    def play_round(self, user_pick):
        computer_pick = random.choice(self.options)
        self.round_number += 1

        if user_pick == computer_pick:
            self.draws += 1
            self.current_streak = 0
            outcome = "Draw"
            self.result_label.config(text="It is a draw. Go again!", fg="#B45309")
        elif self._is_user_winner(user_pick, computer_pick):
            self.user_wins += 1
            self.current_streak += 1
            self.best_streak = max(self.best_streak, self.current_streak)
            outcome = "You won"
            self.result_label.config(text="Nice move. You win this round!", fg="#047857")
        else:
            self.computer_wins += 1
            self.current_streak = 0
            outcome = "Computer won"
            self.result_label.config(text="Computer wins this round. Try a counter move.", fg="#B91C1C")

        self.matchup_label.config(
            text=f"You: {user_pick.title()}    Computer: {computer_pick.title()}"
        )

        self._push_history(user_pick.title(), computer_pick.title(), outcome)
        self._update_labels()

    def reset_score(self):
        self.user_wins = 0
        self.computer_wins = 0
        self.draws = 0
        self.round_number = 0
        self.current_streak = 0
        self.best_streak = 0
        self.history = []

        self.history_box.config(state=tk.NORMAL)
        self.history_box.delete("1.0", tk.END)
        self.history_box.config(state=tk.DISABLED)

        self.result_label.config(text="Score reset. Ready for a fresh match!", fg="#1D4ED8")
        self.matchup_label.config(text="You: -    Computer: -")
        self._update_labels()

    def confirm_quit(self):
        if messagebox.askyesno("Exit Game", "Do you want to quit Rock Paper Scissors?"):
            self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    game = RockPaperScissorsGame(root)
    root.mainloop()