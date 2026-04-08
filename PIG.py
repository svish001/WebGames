import random
import tkinter as tk
from tkinter import messagebox


class PigGameUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Pig Dice Arena 🎲")
        self.root.geometry("760x620")
        self.root.minsize(680, 560)

        self.theme = {
            "panel": "#F8F3E6",
            "title": "#193549",
            "accent": "#D94F4F",
            "text": "#1F2933",
            "button_primary": "#1C7C54",
            "button_secondary": "#276FBF",
            "button_warning": "#F59E0B",
            "button_danger": "#EF4444",
            "button_text": "#111827",
            "muted": "#8B5E34",
        }

        self.dice_faces = {1: "⚀", 2: "⚁", 3: "⚂", 4: "⚃", 5: "⚄", 6: "⚅"}

        self.target_score = 50
        self.players = []
        self.current_player_idx = 0
        self.turn_score = 0
        self.round_count = 1
        self.last_roll = None
        self.shield_active = False
        self.bot_turn_pending = False

        self.setup_screen = None
        self.game_frame = None
        self.scoreboard_labels = []

        self._draw_gradient_background()
        self._build_setup_screen()

    def _draw_gradient_background(self):
        self.bg_canvas = tk.Canvas(self.root, highlightthickness=0)
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)

        width = 1000
        height = 700
        start_rgb = (12, 41, 64)
        end_rgb = (90, 50, 105)
        for i in range(height):
            r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * i / height)
            g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * i / height)
            b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * i / height)
            self.bg_canvas.create_line(0, i, width, i, fill=f"#{r:02x}{g:02x}{b:02x}")

        self.bg_canvas.create_oval(-140, -140, 260, 260, fill="#FFB703", outline="")
        self.bg_canvas.create_oval(620, 60, 1020, 460, fill="#8ECAE6", outline="")
        self.bg_canvas.create_oval(180, 500, 560, 900, fill="#FB8500", outline="")

    def _build_setup_screen(self):
        self.setup_screen = tk.Frame(self.root, bg=self.theme["panel"], relief=tk.RAISED, bd=3)
        self.setup_screen.pack(expand=True, fill=tk.BOTH, padx=40, pady=40)

        tk.Label(
            self.setup_screen,
            text="Pig Dice Arena 🎲",
            font=("Avenir", 36, "bold"),
            bg=self.theme["panel"],
            fg=self.theme["title"],
        ).pack(pady=(24, 6))

        tk.Label(
            self.setup_screen,
            text="Advanced mode with bots, shields, streak bonuses, and live battle log ✨",
            font=("Avenir", 12),
            bg=self.theme["panel"],
            fg=self.theme["muted"],
        ).pack(pady=(0, 22))

        controls = tk.Frame(self.setup_screen, bg=self.theme["panel"])
        controls.pack(pady=8)

        tk.Label(
            controls,
            text="Players (2-6) 👥",
            font=("Avenir", 12, "bold"),
            bg=self.theme["panel"],
            fg=self.theme["text"],
        ).grid(row=0, column=0, sticky="w", padx=(0, 10), pady=8)

        self.players_var = tk.IntVar(value=2)
        players_ctrl = tk.Frame(controls, bg=self.theme["panel"])
        players_ctrl.grid(row=0, column=1, sticky="w", pady=8)

        tk.Button(
            players_ctrl,
            text="-",
            command=lambda: self.adjust_players(-1),
            bg=self.theme["button_secondary"],
            fg=self.theme["button_text"],
            font=("Avenir", 11, "bold"),
            width=3,
            cursor="hand2",
        ).pack(side=tk.LEFT)

        self.players_value_label = tk.Label(
            players_ctrl,
            textvariable=self.players_var,
            width=4,
            anchor="center",
            font=("Avenir", 12, "bold"),
            bg="#FFFDF7",
            fg=self.theme["text"],
            relief=tk.SUNKEN,
            bd=1,
        )
        self.players_value_label.pack(side=tk.LEFT, padx=6)

        tk.Button(
            players_ctrl,
            text="+",
            command=lambda: self.adjust_players(1),
            bg=self.theme["button_primary"],
            fg=self.theme["button_text"],
            font=("Avenir", 11, "bold"),
            width=3,
            cursor="hand2",
        ).pack(side=tk.LEFT)

        tk.Label(
            controls,
            text="Target Score 🎯",
            font=("Avenir", 12, "bold"),
            bg=self.theme["panel"],
            fg=self.theme["text"],
        ).grid(row=1, column=0, sticky="w", padx=(0, 10), pady=8)

        self.target_var = tk.IntVar(value=50)
        target_ctrl = tk.Frame(controls, bg=self.theme["panel"])
        target_ctrl.grid(row=1, column=1, sticky="w", pady=8)

        tk.Button(
            target_ctrl,
            text="-",
            command=lambda: self.adjust_target(-5),
            bg=self.theme["button_secondary"],
            fg=self.theme["button_text"],
            font=("Avenir", 11, "bold"),
            width=3,
            cursor="hand2",
        ).pack(side=tk.LEFT)

        self.target_value_label = tk.Label(
            target_ctrl,
            textvariable=self.target_var,
            width=5,
            anchor="center",
            font=("Avenir", 12, "bold"),
            bg="#FFFDF7",
            fg=self.theme["text"],
            relief=tk.SUNKEN,
            bd=1,
        )
        self.target_value_label.pack(side=tk.LEFT, padx=6)

        tk.Button(
            target_ctrl,
            text="+",
            command=lambda: self.adjust_target(5),
            bg=self.theme["button_primary"],
            fg=self.theme["button_text"],
            font=("Avenir", 11, "bold"),
            width=3,
            cursor="hand2",
        ).pack(side=tk.LEFT)

        self.bots_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            controls,
            text="Enable smart bots for players 2+ 🤖",
            variable=self.bots_var,
            bg=self.theme["panel"],
            fg=self.theme["text"],
            font=("Avenir", 11),
            selectcolor=self.theme["panel"],
            activebackground=self.theme["panel"],
            activeforeground=self.theme["text"],
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=10)

        tk.Button(
            self.setup_screen,
            text="Start Epic Match 🚀",
            command=self.start_game,
            bg=self.theme["button_primary"],
            fg=self.theme["button_text"],
            font=("Avenir", 14, "bold"),
            padx=28,
            pady=12,
            relief=tk.RAISED,
            bd=2,
            activebackground="#166846",
            activeforeground=self.theme["button_text"],
            cursor="hand2",
        ).pack(pady=(12, 14))

    def adjust_players(self, delta):
        new_value = max(2, min(6, self.players_var.get() + delta))
        self.players_var.set(new_value)

    def adjust_target(self, delta):
        new_value = max(25, min(150, self.target_var.get() + delta))
        # Keep target score on multiples of 5 for cleaner gameplay pacing.
        rounded = int(round(new_value / 5) * 5)
        rounded = max(25, min(150, rounded))
        self.target_var.set(rounded)

    def start_game(self):
        try:
            players_count = int(self.players_var.get())
            target_score = int(self.target_var.get())
        except ValueError:
            messagebox.showerror("Invalid Setup", "Players and target score must be numbers.")
            return

        if not 2 <= players_count <= 6:
            messagebox.showerror("Invalid Players", "Players must be between 2 and 6.")
            return

        if not 25 <= target_score <= 150:
            messagebox.showerror("Invalid Target", "Target score must be between 25 and 150.")
            return

        self.target_score = target_score
        self.players = []
        bots_enabled = self.bots_var.get()

        for i in range(players_count):
            is_bot = bots_enabled and i > 0
            self.players.append(
                {
                    "name": f"Bot {i + 1} 🤖" if is_bot else "You 🧑",
                    "score": 0,
                    "is_bot": is_bot,
                    "shield_available": True,
                }
            )

        self.current_player_idx = 0
        self.turn_score = 0
        self.round_count = 1
        self.last_roll = None
        self.shield_active = False
        self.bot_turn_pending = False

        self.setup_screen.destroy()
        self._build_game_screen()
        self._refresh_ui()
        self._log("Game started! Reach the target score to win. 🎯")

        if self.current_player()["is_bot"]:
            self.root.after(700, self._run_bot_turn)

    def _build_game_screen(self):
        self.game_frame = tk.Frame(self.root, bg=self.theme["panel"], relief=tk.RAISED, bd=3)
        self.game_frame.pack(expand=True, fill=tk.BOTH, padx=28, pady=28)

        tk.Label(
            self.game_frame,
            text="Pig Dice Arena 🎲",
            font=("Avenir", 30, "bold"),
            bg=self.theme["panel"],
            fg=self.theme["title"],
        ).pack(pady=(14, 4))

        self.status_label = tk.Label(
            self.game_frame,
            text="",
            font=("Avenir", 12),
            bg=self.theme["panel"],
            fg=self.theme["muted"],
        )
        self.status_label.pack(pady=(0, 8))

        self.dice_label = tk.Label(
            self.game_frame,
            text="🎲",
            font=("Avenir", 54),
            bg=self.theme["panel"],
            fg=self.theme["accent"],
        )
        self.dice_label.pack(pady=(0, 6))

        self.turn_label = tk.Label(
            self.game_frame,
            text="",
            font=("Avenir", 13, "bold"),
            bg=self.theme["panel"],
            fg=self.theme["text"],
        )
        self.turn_label.pack(pady=(0, 8))

        self.scoreboard_frame = tk.Frame(self.game_frame, bg="#FFFDF7", relief=tk.SUNKEN, bd=2)
        self.scoreboard_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.scoreboard_labels = []
        for idx, _player in enumerate(self.players):
            lbl = tk.Label(
                self.scoreboard_frame,
                text="",
                font=("Avenir", 11, "bold"),
                anchor="w",
                bg="#FFFDF7",
                fg=self.theme["text"],
            )
            lbl.grid(row=idx, column=0, sticky="ew", padx=8, pady=3)
            self.scoreboard_labels.append(lbl)
        self.scoreboard_frame.columnconfigure(0, weight=1)

        btn_row = tk.Frame(self.game_frame, bg=self.theme["panel"])
        btn_row.pack(fill=tk.X, padx=10, pady=(0, 8))

        self.roll_btn = tk.Button(
            btn_row,
            text="Roll 🎲",
            command=self.roll_action,
            bg=self.theme["button_secondary"],
            fg=self.theme["button_text"],
            font=("Avenir", 12, "bold"),
            padx=16,
            pady=10,
            relief=tk.RAISED,
            bd=2,
            activebackground="#1D4F91",
            activeforeground=self.theme["button_text"],
            cursor="hand2",
        )
        self.roll_btn.pack(side=tk.LEFT)

        self.hold_btn = tk.Button(
            btn_row,
            text="Hold ✋",
            command=self.hold_action,
            bg=self.theme["button_primary"],
            fg=self.theme["button_text"],
            font=("Avenir", 12, "bold"),
            padx=16,
            pady=10,
            relief=tk.RAISED,
            bd=2,
            activebackground="#166846",
            activeforeground=self.theme["button_text"],
            cursor="hand2",
        )
        self.hold_btn.pack(side=tk.LEFT, padx=(8, 0))

        self.shield_btn = tk.Button(
            btn_row,
            text="Use Shield 🛡️",
            command=self.use_shield,
            bg=self.theme["button_warning"],
            fg=self.theme["button_text"],
            font=("Avenir", 12, "bold"),
            padx=16,
            pady=10,
            relief=tk.RAISED,
            bd=2,
            activebackground="#D97706",
            activeforeground=self.theme["button_text"],
            cursor="hand2",
        )
        self.shield_btn.pack(side=tk.LEFT, padx=(8, 0))

        self.end_btn = tk.Button(
            btn_row,
            text="End Turn ⏭️",
            command=self.end_turn,
            bg="#EAB308",
            fg=self.theme["button_text"],
            font=("Avenir", 12, "bold"),
            padx=16,
            pady=10,
            relief=tk.RAISED,
            bd=2,
            activebackground="#CA8A04",
            activeforeground=self.theme["button_text"],
            cursor="hand2",
        )
        self.end_btn.pack(side=tk.LEFT, padx=(8, 0))

        footer_row = tk.Frame(self.game_frame, bg=self.theme["panel"])
        footer_row.pack(fill=tk.X, padx=10, pady=(0, 8))

        tk.Button(
            footer_row,
            text="New Match 🔁",
            command=self.restart_to_setup,
            bg=self.theme["button_danger"],
            fg=self.theme["button_text"],
            font=("Avenir", 11, "bold"),
            padx=14,
            pady=8,
            relief=tk.RAISED,
            bd=2,
            activebackground="#DC2626",
            activeforeground=self.theme["button_text"],
            cursor="hand2",
        ).pack(side=tk.LEFT)

        self.log_box = tk.Text(
            self.game_frame,
            height=11,
            font=("Avenir", 10),
            bg="#FFFDF7",
            fg="#1F2933",
            relief=tk.SUNKEN,
            bd=2,
            wrap=tk.WORD,
            state=tk.DISABLED,
        )
        self.log_box.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 12))

        self.root.bind("<r>", lambda _event: self.roll_action())
        self.root.bind("<h>", lambda _event: self.hold_action())

    def current_player(self):
        return self.players[self.current_player_idx]

    def _refresh_ui(self):
        player = self.current_player()
        self.status_label.config(
            text=f"Round {self.round_count} | Target: {self.target_score} | Active: {player['name']}"
        )
        self.turn_label.config(
            text=(
                f"Turn Score: {self.turn_score} | "
                f"Shield: {'READY ✅' if player['shield_available'] else 'USED ❌'} | "
                f"Active Shield: {'ON 🛡️' if self.shield_active else 'OFF'}"
            )
        )

        for idx, p in enumerate(self.players):
            marker = "👉 " if idx == self.current_player_idx else "   "
            role = "(BOT)" if p["is_bot"] else "(YOU)"
            self.scoreboard_labels[idx].config(
                text=f"{marker}{p['name']} {role} - {p['score']} pts"
            )

        is_human = not player["is_bot"]
        normal_state = tk.NORMAL if is_human and not self.bot_turn_pending else tk.DISABLED
        self.roll_btn.config(state=normal_state)
        self.hold_btn.config(state=normal_state)
        self.end_btn.config(state=normal_state)

        if is_human and player["shield_available"] and not self.shield_active and not self.bot_turn_pending:
            self.shield_btn.config(state=tk.NORMAL)
        else:
            self.shield_btn.config(state=tk.DISABLED)

    def _log(self, msg):
        self.log_box.config(state=tk.NORMAL)
        self.log_box.insert(tk.END, f"{msg}\n")
        self.log_box.see(tk.END)
        self.log_box.config(state=tk.DISABLED)

    def use_shield(self):
        player = self.current_player()
        if not player["shield_available"]:
            return
        self.shield_active = True
        player["shield_available"] = False
        self._log(f"{player['name']} activated shield for this turn 🛡️")
        self._refresh_ui()

    def roll_action(self):
        if self.bot_turn_pending:
            return

        player = self.current_player()
        value = random.randint(1, 6)
        self.dice_label.config(text=self.dice_faces[value])

        if value == 1:
            if self.shield_active:
                # Shield converts bust into a safe mini gain once per activation.
                shield_gain = 2
                self.turn_score += shield_gain
                self.shield_active = False
                self.last_roll = value
                self._log(
                    f"{player['name']} rolled 1 but shield saved the turn! +{shield_gain} bonus 🛡️"
                )
                self._refresh_ui()
                return

            self._log(f"{player['name']} rolled 1 and busted! 💥 Turn lost.")
            self.turn_score = 0
            self.shield_active = False
            self.last_roll = value
            self.end_turn()
            return

        bonus = 0
        if value == 6 and self.last_roll == 6:
            bonus = 4
            self._log(f"Back-to-back sixes! {player['name']} gets +4 streak bonus 🔥")

        self.turn_score += value + bonus
        self.last_roll = value
        self._log(f"{player['name']} rolled {value} {self.dice_faces[value]} | Turn total: {self.turn_score}")
        self._refresh_ui()

    def hold_action(self):
        player = self.current_player()
        gained = self.turn_score

        if gained >= 20:
            gained += 5
            self._log(f"Big hold bonus! {player['name']} earned +5 for a 20+ turn 🌟")

        player["score"] += gained
        self._log(f"{player['name']} holds and banks {gained} points 🏦")

        if player["score"] >= self.target_score:
            self._refresh_ui()
            self._announce_winner(player)
            return

        self.end_turn(next_round_increment=True)

    def end_turn(self, next_round_increment=False):
        self.turn_score = 0
        self.shield_active = False
        self.last_roll = None

        self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
        if self.current_player_idx == 0 and next_round_increment:
            self.round_count += 1

        self._refresh_ui()

        if self.current_player()["is_bot"]:
            self.bot_turn_pending = True
            self.root.after(700, self._run_bot_turn)

    def _run_bot_turn(self):
        if not self.current_player()["is_bot"]:
            self.bot_turn_pending = False
            self._refresh_ui()
            return

        bot = self.current_player()

        if bot["shield_available"] and not self.shield_active and self.turn_score >= 8:
            self.use_shield()

        hold_threshold = random.randint(12, 20)
        projected = bot["score"] + self.turn_score

        if projected >= self.target_score or self.turn_score >= hold_threshold:
            self.bot_turn_pending = False
            self.hold_action()
            return

        self.roll_action()

        if self.current_player()["is_bot"]:
            self.root.after(700, self._run_bot_turn)
        else:
            self.bot_turn_pending = False
            self._refresh_ui()

    def _announce_winner(self, player):
        self._log(f"{player['name']} wins with {player['score']} points! 🏆")
        self.roll_btn.config(state=tk.DISABLED)
        self.hold_btn.config(state=tk.DISABLED)
        self.shield_btn.config(state=tk.DISABLED)
        self.end_btn.config(state=tk.DISABLED)

        messagebox.showinfo(
            "Winner!",
            f"{player['name']} is the champion!\n\n"
            f"Final Score: {player['score']}\n"
            f"Target: {self.target_score}\n"
            f"Rounds Played: {self.round_count}\n\n"
            "Start a new match to play again. 🎉",
        )

    def restart_to_setup(self):
        if messagebox.askyesno("New Match", "Return to setup and start a new match?"):
            if self.game_frame is not None:
                self.game_frame.destroy()
            self._build_setup_screen()


if __name__ == "__main__":
    root = tk.Tk()
    app = PigGameUI(root)
    root.mainloop()
