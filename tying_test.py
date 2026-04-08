import random
import time
import tkinter as tk
from tkinter import messagebox

WINDOW_W = 900
WINDOW_H = 680

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

PASSAGES = {
	"Easy": [
		"Typing every day builds speed and confidence over time.",
		"Small habits repeated daily can create excellent results.",
		"Practice with focus and your fingers will learn the rhythm.",
		"Consistency matters more than short bursts of effort.",
	],
	"Medium": [
		"A calm mind and steady breathing can improve typing precision under pressure.",
		"Great typists avoid looking at the keyboard and trust muscle memory to guide them.",
		"Accuracy before speed is the rule that creates lasting typing improvement.",
		"By reviewing mistakes after each test, you can find weak patterns and fix them quickly.",
	],
	"Hard": [
		"Precision compounds: when your error rate drops, your average words per minute rises naturally and stays stable.",
		"Technical writing requires punctuation discipline, controlled pacing, and deliberate corrections during long sessions.",
		"Elite performance is built through focused repetition, objective measurement, and honest post session analysis.",
		"Advanced typists balance rhythm with adaptability, switching between narrative and command like input without hesitation.",
	],
}


class TypingMasterUI:
	def __init__(self, root):
		self.root = root
		self.root.title("Typing Master Arena")
		self.root.geometry(f"{WINDOW_W}x{WINDOW_H}")
		self.root.resizable(False, False)

		self.difficulty = tk.StringVar(value="Medium")
		self.rounds_var = tk.IntVar(value=3)

		self.custom_text = ""
		self.targets = []
		self.current_index = 0
		self.current_target = ""

		self.running = False
		self.paused = False
		self.timer_job = None
		self.start_time = 0.0
		self.pause_started = 0.0
		self.paused_total = 0.0

		self.completed_records = []

		self.tests_done = 0
		self.best_wpm = 0.0
		self.best_accuracy = 0.0
		self.total_wpm = 0.0

		self._show_setup_screen()

	def _draw_gradient_background(self):
		canvas = tk.Canvas(self.root, highlightthickness=0)
		canvas.place(x=0, y=0, relwidth=1, relheight=1)

		start_rgb = (12, 41, 64)
		end_rgb = (90, 50, 105)
		for i in range(WINDOW_H):
			r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * i / WINDOW_H)
			g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * i / WINDOW_H)
			b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * i / WINDOW_H)
			canvas.create_line(0, i, WINDOW_W, i, fill=f"#{r:02x}{g:02x}{b:02x}")

		canvas.create_oval(-120, -120, 270, 250, fill="#FFB703", outline="")
		canvas.create_oval(620, 300, 1050, 760, fill="#8ECAE6", outline="")
		canvas.create_oval(160, 520, 540, 900, fill="#FB8500", outline="")

	def _clear(self):
		self._stop_timer()
		for widget in self.root.winfo_children():
			widget.destroy()

	def _stop_timer(self):
		if self.timer_job:
			self.root.after_cancel(self.timer_job)
			self.timer_job = None

	def _make_btn(self, parent, text, bg, fg, active_bg, command, font_size=13, padx=16, pady=10):
		frame = tk.Frame(parent, bg=bg, cursor="hand2")
		lbl = tk.Label(
			frame,
			text=text,
			font=("Avenir", font_size, "bold"),
			bg=bg,
			fg=fg,
			padx=padx,
			pady=pady,
			cursor="hand2",
		)
		lbl.pack(fill="both", expand=True)

		def on_enter(_event):
			frame.config(bg=active_bg)
			lbl.config(bg=active_bg)

		def on_leave(_event):
			frame.config(bg=bg)
			lbl.config(bg=bg)

		def on_press(_event):
			lbl.config(relief="sunken")

		def on_release(_event):
			lbl.config(relief="flat")
			command()

		for w in (frame, lbl):
			w.bind("<Enter>", on_enter)
			w.bind("<Leave>", on_leave)
			w.bind("<ButtonPress-1>", on_press)
			w.bind("<ButtonRelease-1>", on_release)

		return frame

	def _show_setup_screen(self):
		self._clear()
		self._draw_gradient_background()
		self.root.unbind("<Return>")
		self.root.unbind("<Escape>")

		panel = tk.Frame(self.root, bg=THEME["panel"], highlightbackground="#D5C9B0", highlightthickness=2)
		panel.place(relx=0.5, rely=0.5, anchor="center", width=650, height=580)

		tk.Label(panel, text="Typing Master Arena", font=("Avenir", 34, "bold"), bg=THEME["panel"], fg=THEME["title"]).pack(pady=(20, 4))
		tk.Label(panel, text="Advanced speed and accuracy challenge", font=("Avenir", 13), bg=THEME["panel"], fg=THEME["muted"]).pack()

		tk.Frame(panel, height=2, bg=THEME["accent"]).pack(fill="x", padx=36, pady=12)

		config = tk.Frame(panel, bg=THEME["panel"])
		config.pack(pady=(2, 4))

		tk.Label(config, text="Difficulty", font=("Avenir", 13, "bold"), bg=THEME["panel"], fg=THEME["title"]).grid(row=0, column=0, sticky="e", padx=8, pady=6)
		diff_menu = tk.OptionMenu(config, self.difficulty, "Easy", "Medium", "Hard")
		diff_menu.config(font=("Avenir", 12), bg=THEME["panel2"], fg=THEME["text"], width=12)
		diff_menu["menu"].config(font=("Avenir", 11))
		diff_menu.grid(row=0, column=1, padx=8, pady=6)

		tk.Label(config, text="Passages", font=("Avenir", 13, "bold"), bg=THEME["panel"], fg=THEME["title"]).grid(row=1, column=0, sticky="e", padx=8, pady=6)
		tk.Spinbox(
			config,
			from_=1,
			to=10,
			textvariable=self.rounds_var,
			width=6,
			justify="center",
			font=("Avenir", 12, "bold"),
		).grid(row=1, column=1, padx=8, pady=6)

		tk.Label(panel, text="Custom Passage (optional)", font=("Avenir", 12, "bold"), bg=THEME["panel"], fg=THEME["title"]).pack(anchor="w", padx=48, pady=(10, 3))
		self.custom_input = tk.Text(panel, height=5, width=66, font=("Avenir", 11), wrap="word", bg=THEME["white"], fg=THEME["text"])
		self.custom_input.pack(padx=48)
		tk.Label(panel, text="If provided, this text will be used as the first passage.", font=("Avenir", 10), bg=THEME["panel"], fg=THEME["muted"]).pack(anchor="w", padx=48, pady=(3, 5))

		self.setup_feedback = tk.Label(panel, text="", font=("Avenir", 11, "bold"), bg=THEME["panel"], fg=THEME["bad"])
		self.setup_feedback.pack(pady=(0, 4))

		self._make_btn(panel, "Start Challenge", THEME["good"], THEME["text"], "#166846", self._start_challenge, font_size=15, padx=26, pady=12).pack(pady=8)

		avg_wpm = (self.total_wpm / self.tests_done) if self.tests_done else 0.0
		stats_text = (
			f"Tests: {self.tests_done}    Best WPM: {self.best_wpm:.1f}    "
			f"Best Accuracy: {self.best_accuracy:.1f}%    Avg WPM: {avg_wpm:.1f}"
		)
		tk.Label(panel, text=stats_text, font=("Avenir", 11), bg=THEME["panel"], fg=THEME["muted"]).pack(pady=(10, 2))
		tk.Label(panel, text="Enter = Start, Escape = Exit running test", font=("Avenir", 10), bg=THEME["panel"], fg=THEME["muted"]).pack()

		self.root.bind("<Return>", lambda _event: self._start_challenge())

	def _build_targets(self):
		try:
			rounds = int(self.rounds_var.get())
		except (ValueError, tk.TclError):
			return None, "Passages must be a number between 1 and 10."

		if not 1 <= rounds <= 10:
			return None, "Passages must be between 1 and 10."

		custom = self.custom_input.get("1.0", "end").strip()
		selected = []
		pool = PASSAGES[self.difficulty.get()][:]
		random.shuffle(pool)

		if custom:
			selected.append(custom)

		while len(selected) < rounds:
			selected.append(random.choice(pool))

		return selected, None

	def _start_challenge(self):
		targets, error = self._build_targets()
		if error:
			self.setup_feedback.config(text=error)
			return

		self.targets = targets
		self.current_index = 0
		self.current_target = self.targets[0]
		self.completed_records = []

		self.running = True
		self.paused = False
		self.start_time = time.time()
		self.paused_total = 0.0
		self.pause_started = 0.0

		self._show_test_screen()
		self._render_target()
		self._update_live_stats()
		self._tick_timer()

	def _show_test_screen(self):
		self._clear()
		self._draw_gradient_background()
		self.root.unbind("<Return>")

		panel = tk.Frame(self.root, bg=THEME["panel"], highlightbackground="#D5C9B0", highlightthickness=2)
		panel.place(relx=0.5, rely=0.5, anchor="center", width=820, height=620)

		top = tk.Frame(panel, bg=THEME["title"], height=54)
		top.pack(fill="x")

		self.time_lbl = tk.Label(top, text="Time: 0.0s", font=("Avenir", 13, "bold"), bg=THEME["title"], fg=THEME["accent"])
		self.time_lbl.place(x=14, y=15)
		self.wpm_lbl = tk.Label(top, text="WPM: 0", font=("Avenir", 13, "bold"), bg=THEME["title"], fg=THEME["white"])
		self.wpm_lbl.place(x=180, y=15)
		self.acc_lbl = tk.Label(top, text="Accuracy: 100.0%", font=("Avenir", 13, "bold"), bg=THEME["title"], fg=THEME["white"])
		self.acc_lbl.place(x=320, y=15)
		self.cpm_lbl = tk.Label(top, text="CPM: 0", font=("Avenir", 13, "bold"), bg=THEME["title"], fg=THEME["white"])
		self.cpm_lbl.place(x=520, y=15)

		self.progress_lbl = tk.Label(panel, text="Passage 1", font=("Avenir", 12, "bold"), bg=THEME["panel"], fg=THEME["muted"])
		self.progress_lbl.pack(anchor="w", padx=28, pady=(14, 4))

		self.progress_canvas = tk.Canvas(panel, width=760, height=12, bg=THEME["panel2"], highlightthickness=0)
		self.progress_canvas.pack(padx=28, pady=(0, 12))

		target_box = tk.Frame(panel, bg=THEME["panel2"], highlightbackground="#CEC4A8", highlightthickness=1)
		target_box.pack(padx=28, fill="x")

		self.target_view = tk.Text(
			target_box,
			height=7,
			wrap="word",
			font=("Avenir", 14),
			bg=THEME["panel2"],
			fg=THEME["text"],
			bd=0,
			highlightthickness=0,
		)
		self.target_view.pack(fill="x", padx=16, pady=16)
		self.target_view.config(state="disabled")

		self.target_view.tag_config("correct", foreground=THEME["good"])
		self.target_view.tag_config("wrong", foreground=THEME["bad"])
		self.target_view.tag_config("current", background="#FFE8A3", foreground=THEME["title"])
		self.target_view.tag_config("pending", foreground=THEME["text"])

		tk.Label(panel, text="Type Here", font=("Avenir", 12, "bold"), bg=THEME["panel"], fg=THEME["title"]).pack(anchor="w", padx=28, pady=(12, 4))
		self.input_var = tk.StringVar()
		self.input_entry = tk.Entry(panel, textvariable=self.input_var, font=("Avenir", 17, "bold"), bg=THEME["white"], fg=THEME["text"], relief=tk.SUNKEN, bd=2)
		self.input_entry.pack(fill="x", padx=28)
		self.input_entry.focus()
		self.input_entry.bind("<KeyRelease>", self._on_typing)

		self.feedback_lbl = tk.Label(panel, text="Type the highlighted passage exactly.", font=("Avenir", 12, "bold"), bg=THEME["panel"], fg=THEME["title"])
		self.feedback_lbl.pack(anchor="w", padx=28, pady=(8, 6))

		btn_row = tk.Frame(panel, bg=THEME["panel"])
		btn_row.pack(pady=(2, 6))
		self._make_btn(btn_row, "Pause", "#E9C46A", THEME["text"], "#DDBA56", self._toggle_pause).pack(side="left", padx=5)
		self._make_btn(btn_row, "Restart", "#2A9D8F", THEME["text"], "#1E7D71", self._restart_current).pack(side="left", padx=5)
		self._make_btn(btn_row, "Back To Setup", "#D94F4F", THEME["text"], "#C34343", self._show_setup_screen).pack(side="left", padx=5)

		self.root.bind("<Escape>", lambda _event: self._show_setup_screen())

	def _elapsed(self):
		if self.paused:
			return max(0.0, self.pause_started - self.start_time - self.paused_total)
		return max(0.0, time.time() - self.start_time - self.paused_total)

	def _tick_timer(self):
		if not self.running:
			return

		self.time_lbl.config(text=f"Time: {self._elapsed():.1f}s")
		self.timer_job = self.root.after(100, self._tick_timer)

	def _calculate_counts(self):
		typed_total = 0
		correct_total = 0

		for record in self.completed_records:
			target = record["target"]
			typed = record["typed"]
			typed_total += len(typed)
			correct_total += sum(1 for i, ch in enumerate(typed) if i < len(target) and ch == target[i])

		current_typed = self.input_var.get()
		typed_total += len(current_typed)
		correct_total += sum(1 for i, ch in enumerate(current_typed) if i < len(self.current_target) and ch == self.current_target[i])

		return typed_total, correct_total

	def _update_live_stats(self):
		typed_total, correct_total = self._calculate_counts()
		elapsed = max(self._elapsed(), 1.0)
		wpm = (correct_total / 5.0) / (elapsed / 60.0)
		cpm = correct_total / (elapsed / 60.0)
		accuracy = (correct_total / typed_total * 100.0) if typed_total else 100.0

		self.wpm_lbl.config(text=f"WPM: {wpm:.1f}")
		self.acc_lbl.config(text=f"Accuracy: {accuracy:.1f}%")
		self.cpm_lbl.config(text=f"CPM: {cpm:.0f}")

		progress = min(len(self.input_var.get()), len(self.current_target))
		ratio = (progress / len(self.current_target)) if self.current_target else 0.0
		self.progress_canvas.delete("all")
		self.progress_canvas.create_rectangle(0, 0, 760, 12, fill=THEME["panel2"], outline="")
		self.progress_canvas.create_rectangle(0, 0, int(760 * ratio), 12, fill=THEME["accent"], outline="")

		self.progress_lbl.config(text=f"Passage {self.current_index + 1} of {len(self.targets)}")

	def _render_target(self):
		typed = self.input_var.get()
		target = self.current_target

		self.target_view.config(state="normal")
		self.target_view.delete("1.0", "end")

		for idx, char in enumerate(target):
			if idx < len(typed):
				if typed[idx] == char:
					tag = "correct"
				else:
					tag = "wrong"
			elif idx == len(typed):
				tag = "current"
			else:
				tag = "pending"
			self.target_view.insert("end", char, tag)

		self.target_view.config(state="disabled")

	def _on_typing(self, _event):
		if not self.running or self.paused:
			return

		typed = self.input_var.get()
		if len(typed) > len(self.current_target):
			self.input_var.set(typed[:len(self.current_target)])
			typed = self.input_var.get()

		self._render_target()
		self._update_live_stats()

		if typed == self.current_target:
			self.completed_records.append({"target": self.current_target, "typed": typed})
			self.current_index += 1

			if self.current_index >= len(self.targets):
				self._finish_challenge()
				return

			self.current_target = self.targets[self.current_index]
			self.input_var.set("")
			self.feedback_lbl.config(text="Great! Next passage loaded.", fg=THEME["good"])
			self._render_target()
			self._update_live_stats()

	def _toggle_pause(self):
		if not self.running:
			return

		self.paused = not self.paused
		if self.paused:
			self.pause_started = time.time()
			self.input_entry.config(state="disabled")
			self.feedback_lbl.config(text="Paused. Press Pause again to resume.", fg=THEME["bad"])
		else:
			self.paused_total += time.time() - self.pause_started
			self.input_entry.config(state="normal")
			self.input_entry.focus()
			self.feedback_lbl.config(text="Resumed. Keep typing.", fg=THEME["title"])

	def _restart_current(self):
		if not self.running:
			return
		self.input_var.set("")
		self.feedback_lbl.config(text="Current passage restarted.", fg=THEME["title"])
		self._render_target()
		self._update_live_stats()

	def _finish_challenge(self):
		self.running = False
		self._stop_timer()

		typed_total, correct_total = self._calculate_counts()
		elapsed = max(self._elapsed(), 1.0)
		wpm = (correct_total / 5.0) / (elapsed / 60.0)
		accuracy = (correct_total / typed_total * 100.0) if typed_total else 100.0
		cpm = correct_total / (elapsed / 60.0)

		self.tests_done += 1
		self.best_wpm = max(self.best_wpm, wpm)
		self.best_accuracy = max(self.best_accuracy, accuracy)
		self.total_wpm += wpm

		messagebox.showinfo(
			"Challenge Complete",
			(
				f"Elapsed: {elapsed:.1f}s\n"
				f"WPM: {wpm:.1f}\n"
				f"Accuracy: {accuracy:.1f}%\n"
				f"CPM: {cpm:.0f}\n"
				f"Passages Completed: {len(self.targets)}"
			),
		)
		self._show_setup_screen()


def main():
	root = tk.Tk()
	TypingMasterUI(root)
	root.mainloop()


if __name__ == "__main__":
	main()