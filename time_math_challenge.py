import tkinter as tk
import random
import time
from pathlib import Path

# ── Theme ─────────────────────────────────────────────────────────────────────
THEME = {
    "panel":   "#F8F3E6",
    "panel2":  "#EDE8D8",
    "title":   "#193549",
    "accent":  "#E8A838",
    "accent2": "#D4522A",
    "green":   "#27AE60",
    "red":     "#E74C3C",
    "blue":    "#2980B9",
    "text":    "#2C3E50",
    "muted":   "#7F8C8D",
    "white":   "#FFFFFF",
    "gold":    "#F1C40F",
}

DIFFICULTIES = {
    "Easy 🟢":   {"min": 2,  "max": 9,  "ops": ["+", "-"]},
    "Medium 🟡": {"min": 3,  "max": 12, "ops": ["+", "-", "*"]},
    "Hard 🔴":   {"min": 5,  "max": 20, "ops": ["+", "-", "*", "/"]},
}

BG_IMAGE = Path(__file__).parent / "wp3594884.jpg"


class MathBlitz:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("⚡ Math Blitz Challenge")
        self.root.geometry("750x620")
        self.root.resizable(False, False)

        # Persistent state
        self.difficulty   = tk.StringVar(value="Medium 🟡")
        self.num_problems = tk.IntVar(value=10)
        self.personal_best: float | None = None

        # Per-round state
        self.problems_done  = 0
        self.wrong_count    = 0
        self.streak         = 0
        self.best_streak    = 0
        self.score          = 0
        self.elapsed        = 0.0
        self.history: list  = []
        self.current_answer = 0
        self.current_expr   = ""
        self.problem_start  = 0.0
        self.timer_job      = None

        self.root.configure(bg="#0c2940")
        self._build_bg()
        self._show_setup()

    # ── Background ────────────────────────────────────────────────────────────
    def _build_bg(self):
        self.canvas = tk.Canvas(self.root, highlightthickness=0, bg="#0c2940")
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)
        try:
            from PIL import Image, ImageTk
            img = Image.open(BG_IMAGE).resize((750, 620), Image.LANCZOS)
            self._bg_photo = ImageTk.PhotoImage(img)
            self.canvas.create_image(0, 0, anchor="nw", image=self._bg_photo)
        except Exception:
            self._draw_gradient_bg()
        self.canvas.lower("all")

    def _draw_gradient_bg(self):
        w, h = 750, 620
        start_rgb = (12, 41, 64)
        end_rgb   = (90, 50, 105)
        for i in range(h):
            r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * i / h)
            g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * i / h)
            b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * i / h)
            self.canvas.create_line(0, i, w, i, fill=f"#{r:02x}{g:02x}{b:02x}")
        self.canvas.create_oval(-140, -140, 260, 260, fill="#FFB703", outline="")
        self.canvas.create_oval(520,  300,  920,  700,  fill="#8ECAE6", outline="")
        self.canvas.create_oval(160,  460,  540,  840,  fill="#FB8500", outline="")

    # ── Utility ───────────────────────────────────────────────────────────────
    def _clear(self):
        for w in self.root.winfo_children():
            if isinstance(w, tk.Frame):
                w.destroy()

    def _stop_timer(self):
        if self.timer_job:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None

    def _make_btn(self, parent, text, bg, fg, active_bg, command,
                  padx=18, pady=9, font_size=13, bold=True, side=None, pack_padx=6):
        """Frame+Label button — full area clickable, hover + press feedback, macOS safe."""
        weight = "bold" if bold else "normal"
        press_bg = active_bg  # slightly darker feel on press is handled via relief

        frame = tk.Frame(parent, bg=bg, cursor="hand2")
        lbl = tk.Label(
            frame, text=text, font=("Avenir", font_size, weight),
            bg=bg, fg=fg, cursor="hand2",
            padx=padx, pady=pady,
        )
        lbl.pack(fill="both", expand=True)

        def on_enter(e):
            frame.config(bg=active_bg)
            lbl.config(bg=active_bg)
        def on_leave(e):
            frame.config(bg=bg)
            lbl.config(bg=bg)
        def on_press(e):
            frame.config(bg=press_bg)
            lbl.config(bg=press_bg, relief="sunken")
        def on_release(e):
            frame.config(bg=active_bg)
            lbl.config(bg=active_bg, relief="flat")
            command()

        for w in (frame, lbl):
            w.bind("<Enter>",          on_enter)
            w.bind("<Leave>",          on_leave)
            w.bind("<ButtonPress-1>",  on_press)
            w.bind("<ButtonRelease-1>", on_release)

        if side:
            frame.pack(side=side, padx=pack_padx, pady=4)
        return frame

    # ── Setup Screen ──────────────────────────────────────────────────────────
    def _show_setup(self):
        self._clear()
        self._stop_timer()
        self.root.unbind("<Return>")

        panel = tk.Frame(self.root, bg=THEME["panel"],
                         highlightbackground="#D5C9B0", highlightthickness=2)
        panel.place(relx=0.5, rely=0.5, anchor="center", width=500, height=530)

        tk.Label(panel, text="⚡ Math Blitz", font=("Avenir", 36, "bold"),
                 bg=THEME["panel"], fg=THEME["title"]).pack(pady=(28, 4))
        tk.Label(panel, text="Timed arithmetic challenge 🧮",
                 font=("Avenir", 13), bg=THEME["panel"], fg=THEME["muted"]).pack()

        tk.Frame(panel, height=2, bg=THEME["accent"]).pack(fill="x", padx=40, pady=14)

        # Difficulty selector
        tk.Label(panel, text="🎯  Difficulty", font=("Avenir", 13, "bold"),
                 bg=THEME["panel"], fg=THEME["title"]).pack(anchor="w", padx=50)
        diff_row = tk.Frame(panel, bg=THEME["panel"])
        diff_row.pack(pady=7)
        colors = {"Easy 🟢": THEME["green"], "Medium 🟡": THEME["accent"], "Hard 🔴": THEME["red"]}
        for diff, col in colors.items():
            tk.Radiobutton(diff_row, text=diff, variable=self.difficulty, value=diff,
                           font=("Avenir", 12), bg=THEME["panel"], fg=col,
                           selectcolor=THEME["panel2"], activebackground=THEME["panel"],
                           cursor="hand2", indicatoron=0, width=11, relief="groove",
                           padx=6, pady=6).pack(side="left", padx=5)

        # Problem count selector
        tk.Label(panel, text="📝  Number of Problems", font=("Avenir", 13, "bold"),
                 bg=THEME["panel"], fg=THEME["title"]).pack(anchor="w", padx=50, pady=(14, 0))
        count_row = tk.Frame(panel, bg=THEME["panel"])
        count_row.pack(pady=7)
        for n in [5, 10, 15, 20]:
            tk.Radiobutton(count_row, text=str(n), variable=self.num_problems, value=n,
                           font=("Avenir", 13, "bold"), bg=THEME["panel"], fg=THEME["blue"],
                           selectcolor=THEME["panel2"], activebackground=THEME["panel"],
                           cursor="hand2", indicatoron=0, width=5, relief="groove",
                           padx=6, pady=6).pack(side="left", padx=5)

        tk.Frame(panel, height=1, bg=THEME["accent"]).pack(fill="x", padx=40, pady=(18, 10))

        # Personal best badge
        pb_txt = f"🏆 Personal Best (Medium / 10): {self.personal_best:.2f}s" \
                 if self.personal_best else "🏆 Personal Best: —"
        tk.Label(panel, text=pb_txt, font=("Avenir", 12),
                 bg=THEME["panel"], fg=THEME["gold"]).pack(pady=(0, 4))

        self._make_btn(panel, "🚀  Start Challenge!",
                      THEME["title"], THEME["white"], "#2C4F6E",
                      self._start_game, padx=28, pady=13, font_size=15
                      ).pack(pady=(16, 6))

    # ── Game Init ─────────────────────────────────────────────────────────────
    def _start_game(self):
        self.problems_done = 0
        self.wrong_count   = 0
        self.streak        = 0
        self.best_streak   = 0
        self.score         = 0
        self.elapsed       = 0.0
        self.history       = []
        self._clear()
        self._build_game_screen()
        self._next_problem()
        self._tick_timer()

    # ── Game Screen ───────────────────────────────────────────────────────────
    def _build_game_screen(self):
        # Top bar
        top = tk.Frame(self.root, bg=THEME["title"], height=54)
        top.place(x=0, y=0, width=750, height=54)

        self.timer_lbl = tk.Label(top, text="⏱  0.0s", font=("Avenir", 14, "bold"),
                                  bg=THEME["title"], fg=THEME["accent"])
        self.timer_lbl.place(x=20, y=15)

        self.streak_lbl = tk.Label(top, text="🔥 Streak: 0", font=("Avenir", 13),
                                   bg=THEME["title"], fg="#ECF0F1")
        self.streak_lbl.place(relx=0.5, rely=0.5, anchor="center")

        self.score_lbl = tk.Label(top, text="⭐ Score: 0", font=("Avenir", 14, "bold"),
                                  bg=THEME["title"], fg=THEME["gold"])
        self.score_lbl.place(x=585, y=15)

        # Main panel
        panel = tk.Frame(self.root, bg=THEME["panel"],
                         highlightbackground="#D5C9B0", highlightthickness=2)
        panel.place(relx=0.5, rely=0.5, anchor="center", width=560, height=490, y=27)
        self.game_panel = panel

        # Progress label
        self.progress_lbl = tk.Label(panel, text="Problem 1 of 10",
                                     font=("Avenir", 12), bg=THEME["panel"], fg=THEME["muted"])
        self.progress_lbl.pack(pady=(22, 4))

        # Progress bar
        self.prog_canvas = tk.Canvas(panel, width=460, height=14,
                                     bg=THEME["panel2"], highlightthickness=0, bd=0)
        self.prog_canvas.pack(pady=(0, 14))

        # Problem box
        prob_box = tk.Frame(panel, bg=THEME["panel2"],
                            highlightbackground="#CEC4A8", highlightthickness=1)
        prob_box.pack(padx=40, pady=(0, 10), fill="x")
        self.problem_lbl = tk.Label(prob_box, text="",
                                    font=("Avenir", 40, "bold"),
                                    bg=THEME["panel2"], fg=THEME["title"], pady=16)
        self.problem_lbl.pack()

        # Feedback
        self.feedback_lbl = tk.Label(panel, text="", font=("Avenir", 14, "bold"),
                                     bg=THEME["panel"], fg=THEME["green"])
        self.feedback_lbl.pack(pady=(0, 6))

        # Answer row
        entry_row = tk.Frame(panel, bg=THEME["panel"])
        entry_row.pack(pady=4)
        tk.Label(entry_row, text="Your answer:", font=("Avenir", 12),
                 bg=THEME["panel"], fg=THEME["text"]).pack(side="left", padx=(0, 10))
        self.answer_var = tk.StringVar()
        self.answer_entry = tk.Entry(entry_row, textvariable=self.answer_var,
                                     font=("Avenir", 22, "bold"), width=6,
                                     justify="center", bg=THEME["white"],
                                     fg=THEME["title"], relief="groove", bd=2)
        self.answer_entry.pack(side="left")
        self.answer_entry.focus()

        self.root.bind("<Return>", lambda e: self._submit_answer())

        # Buttons
        btn_row = tk.Frame(panel, bg=THEME["panel"])
        btn_row.pack(pady=12)
        self._make_btn(btn_row, "✓  Submit",
                       THEME["green"], THEME["white"], "#229954",
                       self._submit_answer, pady=10, side="left", pack_padx=8)
        self._make_btn(btn_row, "▷  Skip",
                       THEME["blue"], THEME["white"], "#1F6FAF",
                       self._skip_problem, pady=10, side="left", pack_padx=8)
        self._make_btn(btn_row, "✕  Quit",
                       THEME["accent2"], THEME["white"], "#C0392B",
                       self._show_setup, pady=10, side="left", pack_padx=8)

        tk.Label(panel, text="💡 Press Enter to submit quickly",
                 font=("Avenir", 10), bg=THEME["panel"], fg=THEME["muted"]).pack()

    # ── Timer ─────────────────────────────────────────────────────────────────
    def _tick_timer(self):
        self.elapsed += 0.1
        try:
            self.timer_lbl.config(text=f"⏱  {self.elapsed:.1f}s")
        except Exception:
            return
        self.timer_job = self.root.after(100, self._tick_timer)

    # ── Progress bar ──────────────────────────────────────────────────────────
    def _update_progress(self):
        total = self.num_problems.get()
        done  = self.problems_done
        self.progress_lbl.config(text=f"Problem {done + 1} of {total}")
        self.prog_canvas.delete("all")
        frac = done / total
        if frac > 0:
            self.prog_canvas.create_rectangle(0, 0, int(460 * frac), 14,
                                              fill=THEME["accent"], outline="")
        self.prog_canvas.create_text(230, 7, text=f"{done}/{total}",
                                     fill=THEME["title"], font=("Avenir", 8, "bold"))

    # ── Problem generation ────────────────────────────────────────────────────
    def _next_problem(self):
        cfg = DIFFICULTIES[self.difficulty.get()]
        mn, mx, ops = cfg["min"], cfg["max"], cfg["ops"]
        op    = random.choice(ops)
        left  = random.randint(mn, mx)
        right = random.randint(mn, mx)

        if op == "/":
            right = max(1, right)
            multiplier = random.randint(1, max(1, mx // right))
            left = right * multiplier
            answer = left // right
        else:
            answer = eval(f"{left} {op} {right}")  # nosec – no user input

        op_sym = {"*": "×", "/": "÷"}.get(op, op)
        self.current_expr   = f"{left}  {op_sym}  {right}"
        self.current_answer = int(answer)
        self.answer_var.set("")
        try:
            self.problem_lbl.config(text=f"{self.current_expr}  =  ?")
            self.feedback_lbl.config(text="")
            self._update_progress()
            self.answer_entry.focus()
        except Exception:
            pass
        self.problem_start = time.time()

    # ── Submit ────────────────────────────────────────────────────────────────
    def _submit_answer(self):
        raw = self.answer_var.get().strip()
        if not raw:
            return
        try:
            guess = int(raw)
        except ValueError:
            self.feedback_lbl.config(text="⚠️  Please enter a whole number!",
                                     fg=THEME["accent2"])
            self.answer_var.set("")
            return

        elapsed_this = time.time() - self.problem_start
        correct      = (guess == self.current_answer)
        self.history.append((self.current_expr, self.current_answer, guess, elapsed_this))

        if correct:
            self.streak     += 1
            self.best_streak = max(self.best_streak, self.streak)
            speed_bonus      = max(0, int(10 - elapsed_this))
            streak_bonus     = 5 if self.streak >= 3 else 0
            self.score      += 10 + speed_bonus + streak_bonus
            msgs = ["✅ Correct! 🎉", "✅ Nice one! 🔥", "✅ Perfect! ⭐", "✅ Brilliant! 💡"]
            msg  = random.choice(msgs)
            if self.streak >= 3:
                msg += f"  🔥 ×{self.streak} streak"
            self.feedback_lbl.config(text=msg, fg=THEME["green"])
        else:
            self.wrong_count += 1
            self.streak       = 0
            self.score        = max(0, self.score - 3)
            self.feedback_lbl.config(
                text=f"❌ Wrong!  The answer was {self.current_answer}", fg=THEME["red"])

        self.streak_lbl.config(text=f"🔥 Streak: {self.streak}")
        self.score_lbl.config(text=f"⭐ Score: {self.score}")

        self.problems_done += 1
        if self.problems_done >= self.num_problems.get():
            self.root.after(900, self._show_results)
        else:
            self.root.after(750, self._next_problem)

    # ── Skip ──────────────────────────────────────────────────────────────────
    def _skip_problem(self):
        elapsed_this = time.time() - self.problem_start
        self.wrong_count += 1
        self.streak       = 0
        self.score        = max(0, self.score - 2)
        self.history.append((self.current_expr, self.current_answer, "—skipped—", elapsed_this))
        self.feedback_lbl.config(
            text=f"⏭  Skipped  (answer: {self.current_answer})", fg=THEME["muted"])
        self.streak_lbl.config(text=f"🔥 Streak: {self.streak}")
        self.score_lbl.config(text=f"⭐ Score: {self.score}")
        self.problems_done += 1
        if self.problems_done >= self.num_problems.get():
            self.root.after(700, self._show_results)
        else:
            self.root.after(700, self._next_problem)

    # ── Results Screen ────────────────────────────────────────────────────────
    def _show_results(self):
        self._stop_timer()
        self.root.unbind("<Return>")
        total    = self.num_problems.get()
        correct  = total - self.wrong_count
        accuracy = round(correct / total * 100)
        total_t  = round(self.elapsed, 2)

        # Track personal best (Medium / 10 only)
        if self.difficulty.get() == "Medium 🟡" and total == 10:
            if self.personal_best is None or total_t < self.personal_best:
                self.personal_best = total_t

        self._clear()
        panel = tk.Frame(self.root, bg=THEME["panel"],
                         highlightbackground="#D5C9B0", highlightthickness=2)
        panel.place(relx=0.5, rely=0.5, anchor="center", width=565, height=540)

        medal = "🥇" if accuracy >= 90 else "🥈" if accuracy >= 75 else "🥉" if accuracy >= 50 else "😅"
        tk.Label(panel, text=medal, font=("Avenir", 46),
                 bg=THEME["panel"]).pack(pady=(20, 0))
        tk.Label(panel, text="Challenge Complete!", font=("Avenir", 22, "bold"),
                 bg=THEME["panel"], fg=THEME["title"]).pack(pady=(4, 2))
        tk.Label(panel, text=f"{self.difficulty.get()}  ·  {total} Problems",
                 font=("Avenir", 11), bg=THEME["panel"], fg=THEME["muted"]).pack()

        tk.Frame(panel, height=2, bg=THEME["accent"]).pack(fill="x", padx=40, pady=12)

        # Stats grid
        grid = tk.Frame(panel, bg=THEME["panel"])
        grid.pack()
        stats = [
            ("⏱  Total Time",   f"{total_t}s",        THEME["blue"]),
            ("✅  Correct",      f"{correct}/{total}",  THEME["green"]),
            ("❌  Wrong",        str(self.wrong_count), THEME["red"]),
            ("🎯  Accuracy",     f"{accuracy}%",        THEME["accent"]),
            ("⭐  Score",        str(self.score),        THEME["gold"]),
            ("🔥  Best Streak",  str(self.best_streak), THEME["accent2"]),
        ]
        for i, (lbl, val, col) in enumerate(stats):
            r, c = divmod(i, 2)
            cell = tk.Frame(grid, bg=THEME["panel2"],
                            highlightbackground="#CEC4A8", highlightthickness=1)
            cell.grid(row=r, column=c, padx=10, pady=6, ipadx=20, ipady=8, sticky="ew")
            tk.Label(cell, text=lbl, font=("Avenir", 10),
                     bg=THEME["panel2"], fg=THEME["muted"]).pack()
            tk.Label(cell, text=val, font=("Avenir", 19, "bold"),
                     bg=THEME["panel2"], fg=col).pack()

        if self.personal_best:
            tk.Label(panel, text=f"🏆 Personal Best (Medium/10): {self.personal_best:.2f}s",
                     font=("Avenir", 11), bg=THEME["panel"], fg=THEME["gold"]).pack(pady=(10, 0))

        btn_row = tk.Frame(panel, bg=THEME["panel"])
        btn_row.pack(pady=14)
        self._make_btn(btn_row, "↺  Play Again",
                       THEME["title"], THEME["white"], "#2C4F6E",
                       self._start_game, side="left", pack_padx=6)
        self._make_btn(btn_row, "◁  Menu",
                       "#5D6D7E", THEME["white"], "#4A5568",
                       self._show_setup, side="left", pack_padx=6)
        self._make_btn(btn_row, "≡  Review Answers",
                       THEME["accent2"], THEME["white"], "#C0392B",
                       self._show_review, side="left", pack_padx=6)

    # ── Review Screen ─────────────────────────────────────────────────────────
    def _show_review(self):
        self._clear()
        panel = tk.Frame(self.root, bg=THEME["panel"],
                         highlightbackground="#D5C9B0", highlightthickness=2)
        panel.place(relx=0.5, rely=0.5, anchor="center", width=590, height=530)

        tk.Label(panel, text="📋  Problem Review", font=("Avenir", 22, "bold"),
                 bg=THEME["panel"], fg=THEME["title"]).pack(pady=(20, 4))
        tk.Label(panel, text="How did you do on each question?",
                 font=("Avenir", 11), bg=THEME["panel"], fg=THEME["muted"]).pack()
        tk.Frame(panel, height=2, bg=THEME["accent"]).pack(fill="x", padx=40, pady=10)

        # Scrollable area
        container = tk.Frame(panel, bg=THEME["panel"])
        container.pack(fill="both", expand=True, padx=18, pady=(0, 6))
        sb = tk.Scrollbar(container)
        sb.pack(side="right", fill="y")
        cvs = tk.Canvas(container, bg=THEME["panel"], highlightthickness=0,
                        yscrollcommand=sb.set)
        cvs.pack(side="left", fill="both", expand=True)
        sb.config(command=cvs.yview)
        inner = tk.Frame(cvs, bg=THEME["panel"])
        cvs.create_window((0, 0), window=inner, anchor="nw")

        for i, (expr, ans, user, t) in enumerate(self.history, 1):
            skipped   = (str(user) == "—skipped—")
            is_correct = (not skipped) and (int(user) == ans)
            icon   = "✅" if is_correct else ("⏭" if skipped else "❌")
            col    = THEME["green"] if is_correct else (THEME["muted"] if skipped else THEME["red"])
            row_bg = "#EDF7EE" if is_correct else ("#F5F5F5" if skipped else "#FDECEA")

            row = tk.Frame(inner, bg=row_bg,
                           highlightbackground="#CEC4A8", highlightthickness=1)
            row.pack(fill="x", pady=3, padx=4)
            tk.Label(row, text=f"{icon}  #{i}   {expr} = {ans}",
                     font=("Avenir", 12, "bold"), bg=row_bg, fg=col, anchor="w"
                     ).pack(side="left", padx=10, pady=6)
            tk.Label(row, text=f"You: {user}   ({t:.1f}s)",
                     font=("Avenir", 11), bg=row_bg, fg=THEME["muted"], anchor="e"
                     ).pack(side="right", padx=10)

        inner.update_idletasks()
        cvs.config(scrollregion=cvs.bbox("all"))

        self._make_btn(panel, "‹  Back to Results",
                      THEME["title"], THEME["white"], "#2C4F6E",
                      self._show_results, pady=10, font_size=12
                      ).pack(pady=(0, 14))


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    MathBlitz(root)
    root.mainloop()