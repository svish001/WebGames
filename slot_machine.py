import random
import tkinter as tk
from tkinter import messagebox
from pathlib import Path

MAX_LINES = 3
MAX_BET = 100
MIN_BET = 1
ROWS = 3
COLS = 3
AUTO_SPINS = 10

SYMBOL_COUNT = {
    "A": 2,
    "B": 4,
    "C": 6,
    "D": 8,
}

SYMBOL_VALUE = {
    "A": 6,
    "B": 5,
    "C": 4,
    "D": 3,
}

SYMBOL_COLORS = {
    "A": "#F5B700",
    "B": "#EF6F6C",
    "C": "#4ECDC4",
    "D": "#5C7AEA",
}

THEME = {
    "panel": "#F8F3E6",
    "panel2": "#EDE8D8",
    "title": "#193549",
    "accent": "#E8A838",
    "good": "#1C7C54",
    "bad": "#C0392B",
    "text": "#1F2933",
    "muted": "#6B7280",
    "white": "#FFFFFF",
}

BG_IMAGE = Path(__file__).parent / "wp3594884.jpg"


def check_winnings(columns, lines, bet, values):
    winnings = 0
    winning_lines = []

    for line in range(lines):
        symbol = columns[0][line]
        for column in columns:
            if column[line] != symbol:
                break
        else:
            winnings += values[symbol] * bet
            winning_lines.append(line + 1)

    return winnings, winning_lines


def get_slot_machine_spin(rows, cols, symbols):
    all_symbols = []
    for symbol, count in symbols.items():
        all_symbols.extend([symbol] * count)

    columns = []
    for _ in range(cols):
        column = []
        current_symbols = all_symbols[:]
        for _ in range(rows):
            picked = random.choice(current_symbols)
            current_symbols.remove(picked)
            column.append(picked)
        columns.append(column)

    return columns


class SlotMachineUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Slot Machine Deluxe")
        self.root.geometry("760x620")
        self.root.resizable(False, False)

        self.photo = None
        self.balance = 0
        self.total_spins = 0
        self.total_wagered = 0
        self.total_won = 0
        self.best_win = 0
        self.jackpot_count = 0
        self.auto_left = 0
        self.auto_job = None

        self._show_start_screen()

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

        canvas.create_oval(-110, -110, 250, 250, fill="#FFB703", outline="")
        canvas.create_oval(width - 220, 90, width + 110, 420, fill="#8ECAE6", outline="")
        canvas.create_oval(120, height - 170, 460, height + 100, fill="#FB8500", outline="")

    def _set_background(self):
        width = self.root.winfo_width() if self.root.winfo_width() > 1 else 760
        height = self.root.winfo_height() if self.root.winfo_height() > 1 else 620

        try:
            from PIL import Image, ImageTk

            img = Image.open(BG_IMAGE)
            img = img.resize((width, height), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(img)
            bg = tk.Label(self.root, image=self.photo)
            bg.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception:
            self._draw_gradient_background(width, height)

    def _clear_window(self):
        if self.auto_job:
            self.root.after_cancel(self.auto_job)
            self.auto_job = None

        for widget in self.root.winfo_children():
            widget.destroy()

    def _show_start_screen(self):
        self._clear_window()
        self._set_background()
        self.root.unbind("<Return>")

        panel = tk.Frame(self.root, bg=THEME["panel"], relief=tk.RAISED, bd=3)
        panel.pack(expand=True, padx=42, pady=42, fill=tk.BOTH)

        tk.Label(
            panel,
            text="Slot Machine Deluxe",
            font=("Avenir", 34, "bold"),
            bg=THEME["panel"],
            fg=THEME["title"],
        ).pack(pady=(24, 8))

        tk.Label(
            panel,
            text=f"Bet on 1-{MAX_LINES} lines | Bet range ${MIN_BET}-${MAX_BET}",
            font=("Avenir", 14),
            bg=THEME["panel"],
            fg=THEME["text"],
        ).pack(pady=8)

        deposit_row = tk.Frame(panel, bg=THEME["panel"])
        deposit_row.pack(pady=(18, 8))
        tk.Label(
            deposit_row,
            text="Starting deposit ($):",
            font=("Avenir", 14, "bold"),
            bg=THEME["panel"],
            fg=THEME["title"],
        ).pack(side="left", padx=(0, 10))

        self.deposit_var = tk.StringVar(value="100")
        deposit_entry = tk.Entry(
            deposit_row,
            textvariable=self.deposit_var,
            width=8,
            justify="center",
            font=("Avenir", 18, "bold"),
            bd=2,
            relief=tk.SUNKEN,
        )
        deposit_entry.pack(side="left")
        deposit_entry.focus()

        self.start_feedback = tk.Label(
            panel,
            text="",
            font=("Avenir", 12, "bold"),
            bg=THEME["panel"],
            fg=THEME["bad"],
        )
        self.start_feedback.pack(pady=(10, 6))

        tk.Button(
            panel,
            text="Start Playing",
            command=self._start_game,
            bg=THEME["good"],
            fg=THEME["text"],
            activebackground="#166846",
            activeforeground=THEME["text"],
            font=("Avenir", 16, "bold"),
            padx=28,
            pady=12,
            cursor="hand2",
            relief=tk.RAISED,
            bd=2,
        ).pack(pady=12)

        tk.Label(
            panel,
            text="Press Enter to start",
            font=("Avenir", 11),
            bg=THEME["panel"],
            fg=THEME["muted"],
        ).pack(pady=(4, 0))

        self.root.bind("<Return>", lambda _event: self._start_game())

    def _start_game(self):
        text = self.deposit_var.get().strip()
        if not text.isdigit() or int(text) <= 0:
            self.start_feedback.config(text="Enter a valid positive deposit amount.")
            return

        self.balance = int(text)
        self.total_spins = 0
        self.total_wagered = 0
        self.total_won = 0
        self.best_win = 0
        self.jackpot_count = 0
        self.auto_left = 0
        self._show_game_screen()

    def _show_game_screen(self):
        self._clear_window()
        self._set_background()
        self.root.unbind("<Return>")

        panel = tk.Frame(self.root, bg=THEME["panel"], relief=tk.RAISED, bd=3)
        panel.pack(expand=True, padx=30, pady=30, fill=tk.BOTH)

        tk.Label(
            panel,
            text="Slot Machine",
            font=("Avenir", 30, "bold"),
            bg=THEME["panel"],
            fg=THEME["title"],
        ).pack(pady=(16, 6))

        self.balance_lbl = tk.Label(
            panel,
            text="",
            font=("Avenir", 16, "bold"),
            bg=THEME["panel"],
            fg=THEME["text"],
        )
        self.balance_lbl.pack()

        controls = tk.Frame(panel, bg=THEME["panel"])
        controls.pack(pady=12)

        tk.Label(controls, text="Lines:", font=("Avenir", 13, "bold"), bg=THEME["panel"], fg=THEME["text"]).grid(row=0, column=0, padx=6)
        self.lines_var = tk.IntVar(value=1)
        tk.Spinbox(
            controls,
            from_=1,
            to=MAX_LINES,
            width=4,
            textvariable=self.lines_var,
            justify="center",
            font=("Avenir", 13, "bold"),
            command=self._update_bet_preview,
        ).grid(row=0, column=1, padx=6)

        tk.Label(controls, text="Bet/line:", font=("Avenir", 13, "bold"), bg=THEME["panel"], fg=THEME["text"]).grid(row=0, column=2, padx=6)
        self.bet_var = tk.IntVar(value=5)
        tk.Spinbox(
            controls,
            from_=MIN_BET,
            to=MAX_BET,
            width=6,
            textvariable=self.bet_var,
            justify="center",
            font=("Avenir", 13, "bold"),
            command=self._update_bet_preview,
        ).grid(row=0, column=3, padx=6)

        self.total_bet_lbl = tk.Label(
            controls,
            text="",
            font=("Avenir", 12),
            bg=THEME["panel"],
            fg=THEME["muted"],
        )
        self.total_bet_lbl.grid(row=0, column=4, padx=10)

        reels = tk.Frame(panel, bg=THEME["panel2"], relief=tk.SUNKEN, bd=2)
        reels.pack(padx=32, pady=8, fill=tk.X)

        self.reel_labels = []
        for row in range(ROWS):
            row_labels = []
            for col in range(COLS):
                lbl = tk.Label(
                    reels,
                    text="-",
                    width=5,
                    height=2,
                    font=("Avenir", 26, "bold"),
                    bg=THEME["white"],
                    fg=THEME["title"],
                    relief=tk.GROOVE,
                    bd=1,
                )
                lbl.grid(row=row, column=col, padx=8, pady=8)
                row_labels.append(lbl)
            self.reel_labels.append(row_labels)

        self.feedback_lbl = tk.Label(
            panel,
            text="Choose lines and bet, then spin.",
            font=("Avenir", 13, "bold"),
            bg=THEME["panel"],
            fg=THEME["title"],
        )
        self.feedback_lbl.pack(pady=(8, 6))

        btn_row = tk.Frame(panel, bg=THEME["panel"])
        btn_row.pack(pady=6)

        tk.Button(
            btn_row,
            text="Spin",
            command=self._spin_once,
            bg="#276FBF",
            fg=THEME["text"],
            activeforeground=THEME["text"],
            font=("Avenir", 13, "bold"),
            padx=18,
            pady=10,
            cursor="hand2",
        ).grid(row=0, column=0, padx=6)

        tk.Button(
            btn_row,
            text=f"Auto x{AUTO_SPINS}",
            command=self._start_auto_spin,
            bg="#7A5195",
            fg=THEME["text"],
            activeforeground=THEME["text"],
            font=("Avenir", 13, "bold"),
            padx=18,
            pady=10,
            cursor="hand2",
        ).grid(row=0, column=1, padx=6)

        tk.Button(
            btn_row,
            text="Deposit +50",
            command=lambda: self._add_deposit(50),
            bg=THEME["good"],
            fg=THEME["text"],
            activeforeground=THEME["text"],
            font=("Avenir", 13, "bold"),
            padx=18,
            pady=10,
            cursor="hand2",
        ).grid(row=0, column=2, padx=6)

        tk.Button(
            btn_row,
            text="Cash Out",
            command=self._cash_out,
            bg="#D94F4F",
            fg=THEME["text"],
            activeforeground=THEME["text"],
            font=("Avenir", 13, "bold"),
            padx=18,
            pady=10,
            cursor="hand2",
        ).grid(row=0, column=3, padx=6)

        self.stats_lbl = tk.Label(
            panel,
            text="",
            justify="left",
            font=("Avenir", 12),
            bg=THEME["panel"],
            fg=THEME["text"],
        )
        self.stats_lbl.pack(pady=(8, 16), anchor="w", padx=34)

        self.root.bind("<Return>", lambda _event: self._spin_once())
        self._update_bet_preview()
        self._refresh_stats()

    def _read_int(self, var, default):
        try:
            return int(var.get())
        except (ValueError, tk.TclError):
            return default

    def _update_bet_preview(self):
        lines = self._read_int(self.lines_var, 1)
        bet = self._read_int(self.bet_var, MIN_BET)
        total_bet = lines * bet
        self.total_bet_lbl.config(text=f"Total bet: ${total_bet}")

    def _refresh_stats(self):
        net = self.total_won - self.total_wagered
        self.balance_lbl.config(text=f"Balance: ${self.balance}")
        self.stats_lbl.config(
            text=(
                f"Spins: {self.total_spins}    Wagered: ${self.total_wagered}    Won: ${self.total_won}\n"
                f"Net: ${net}    Best Win: ${self.best_win}    Jackpots: {self.jackpot_count}"
            )
        )

    def _validate_bet(self):
        lines = self._read_int(self.lines_var, 1)
        bet = self._read_int(self.bet_var, MIN_BET)

        if not (1 <= lines <= MAX_LINES):
            self.feedback_lbl.config(text="Lines must be between 1 and 3.", fg=THEME["bad"])
            return None
        if not (MIN_BET <= bet <= MAX_BET):
            self.feedback_lbl.config(
                text=f"Bet per line must be between ${MIN_BET} and ${MAX_BET}.",
                fg=THEME["bad"],
            )
            return None

        total_bet = lines * bet
        if total_bet > self.balance:
            self.feedback_lbl.config(text="Not enough balance for this bet.", fg=THEME["bad"])
            return None

        return lines, bet, total_bet

    def _render_slots(self, columns):
        for row in range(ROWS):
            for col in range(COLS):
                symbol = columns[col][row]
                label = self.reel_labels[row][col]
                label.config(text=symbol, fg=SYMBOL_COLORS.get(symbol, THEME["title"]))

    def _spin_once(self):
        validated = self._validate_bet()
        if not validated:
            self._stop_auto_spin()
            return

        lines, bet, total_bet = validated
        columns = get_slot_machine_spin(ROWS, COLS, SYMBOL_COUNT)
        winnings, winning_lines = check_winnings(columns, lines, bet, SYMBOL_VALUE)

        self.balance -= total_bet
        self.balance += winnings
        self.total_spins += 1
        self.total_wagered += total_bet
        self.total_won += winnings
        self.best_win = max(self.best_win, winnings)

        if winnings >= total_bet * 5 and winnings > 0:
            self.jackpot_count += 1

        self._render_slots(columns)
        if winnings > 0:
            lines_text = ", ".join(str(line) for line in winning_lines)
            self.feedback_lbl.config(
                text=f"You won ${winnings} on line(s): {lines_text}",
                fg=THEME["good"],
            )
        else:
            self.feedback_lbl.config(text=f"No win this spin. Lost ${total_bet}.", fg=THEME["bad"])

        self._update_bet_preview()
        self._refresh_stats()

        if self.balance < MIN_BET:
            self._stop_auto_spin()
            messagebox.showinfo("Balance Low", "Your balance is too low to continue. Add deposit.")

    def _run_auto_spin_step(self):
        if self.auto_left <= 0:
            self._stop_auto_spin()
            return

        self._spin_once()
        self.auto_left -= 1

        if self.auto_left > 0:
            self.auto_job = self.root.after(220, self._run_auto_spin_step)
        else:
            self._stop_auto_spin()

    def _start_auto_spin(self):
        if self.auto_job:
            return
        self.auto_left = AUTO_SPINS
        self.feedback_lbl.config(text=f"Auto spin started ({AUTO_SPINS} spins).", fg=THEME["title"])
        self._run_auto_spin_step()

    def _stop_auto_spin(self):
        self.auto_left = 0
        if self.auto_job:
            self.root.after_cancel(self.auto_job)
            self.auto_job = None

    def _add_deposit(self, amount):
        self.balance += amount
        self._refresh_stats()
        self.feedback_lbl.config(text=f"Added ${amount} to balance.", fg=THEME["good"])

    def _cash_out(self):
        self._stop_auto_spin()
        messagebox.showinfo(
            "Session Summary",
            (
                f"You cash out with ${self.balance}.\n\n"
                f"Spins: {self.total_spins}\n"
                f"Total wagered: ${self.total_wagered}\n"
                f"Total won: ${self.total_won}\n"
                f"Best win: ${self.best_win}\n"
                f"Jackpots: {self.jackpot_count}"
            ),
        )
        self._show_start_screen()


def main():
    root = tk.Tk()
    SlotMachineUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()