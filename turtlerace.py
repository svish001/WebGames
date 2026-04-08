import random
import time
import tkinter as tk
from tkinter import messagebox

WINDOW_W = 940
WINDOW_H = 690
TRACK_W = 820
TRACK_H = 420

RACER_COLORS = [
	"#E63946",
	"#2A9D8F",
	"#3A86FF",
	"#F4A261",
	"#E9C46A",
	"#6A4C93",
	"#FF006E",
	"#8338EC",
	"#8D6E63",
	"#00B4D8",
]

THEME = {
	"panel": "#F8F3E6",
	"panel2": "#EDE8D8",
	"title": "#193549",
	"text": "#1F2933",
	"muted": "#6B7280",
	"good": "#1C7C54",
	"bad": "#C0392B",
	"white": "#FFFFFF",
}


class TurtleRaceUI:
	def __init__(self, root):
		self.root = root
		self.root.title("Turtle Race Championship")
		self.root.geometry(f"{WINDOW_W}x{WINDOW_H}")
		self.root.resizable(False, False)

		self.photo = None
		self.race_job = None
		self.timer_job = None
		self.running = False
		self.paused = False
		self.race_start_time = 0.0

		self.racers_count_var = tk.IntVar(value=6)
		self.speed_var = tk.StringVar(value="Normal")
		self.bet_var = tk.StringVar(value="Auto")
		self.custom_racers_var = tk.StringVar(value="")

		self.active_colors = []
		self.active_names = []
		self.racers = []
		self.finish_x = 0

		self.races_played = 0
		self.correct_bets = 0
		self.current_streak = 0
		self.best_streak = 0
		self.best_time = None

		self._show_setup_screen()

	def _draw_gradient_background(self, width, height):
		canvas = tk.Canvas(self.root, highlightthickness=0)
		canvas.place(x=0, y=0, relwidth=1, relheight=1)

		start_rgb = (12, 41, 64)
		end_rgb = (90, 50, 105)
		for i in range(max(height, 1)):
			r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * i / height)
			g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * i / height)
			b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * i / height)
			canvas.create_line(0, i, width, i, fill=f"#{r:02x}{g:02x}{b:02x}")

		canvas.create_oval(-140, -140, 260, 260, fill="#FFB703", outline="")
		canvas.create_oval(width - 320, 110, width + 140, 520, fill="#8ECAE6", outline="")
		canvas.create_oval(130, height - 190, 560, height + 140, fill="#FB8500", outline="")

	def _set_background(self):
		self._draw_gradient_background(WINDOW_W, WINDOW_H)

	def _clear_window(self):
		self._stop_race_loop()
		for widget in self.root.winfo_children():
			widget.destroy()

	def _show_setup_screen(self):
		self._clear_window()
		self._set_background()
		self.root.unbind("<space>")
		self.root.unbind("<Return>")

		panel = tk.Frame(self.root, bg=THEME["panel"], relief=tk.RAISED, bd=3)
		panel.pack(expand=True, padx=44, pady=42, fill=tk.BOTH)

		tk.Label(
			panel,
			text="Turtle Race Championship",
			font=("Avenir", 34, "bold"),
			bg=THEME["panel"],
			fg=THEME["title"],
		).pack(pady=(24, 8))

		tk.Label(
			panel,
			text="Configure your race, place a prediction, and track your season stats.",
			font=("Avenir", 14),
			bg=THEME["panel"],
			fg=THEME["text"],
		).pack(pady=6)

		config = tk.Frame(panel, bg=THEME["panel"])
		config.pack(pady=(20, 8))

		tk.Label(config, text="Racers:", font=("Avenir", 13, "bold"), bg=THEME["panel"], fg=THEME["title"]).grid(row=0, column=0, padx=7, pady=6, sticky="e")
		racers_spin = tk.Spinbox(
			config,
			from_=2,
			to=10,
			textvariable=self.racers_count_var,
			width=5,
			justify="center",
			font=("Avenir", 13, "bold"),
			command=self._refresh_bet_options,
		)
		racers_spin.grid(row=0, column=1, padx=7, pady=6)
		racers_spin.bind("<KeyRelease>", self._refresh_bet_options_event)

		tk.Label(config, text="Pace:", font=("Avenir", 13, "bold"), bg=THEME["panel"], fg=THEME["title"]).grid(row=1, column=0, padx=7, pady=6, sticky="e")
		pace_menu = tk.OptionMenu(config, self.speed_var, "Slow", "Normal", "Fast")
		pace_menu.config(font=("Avenir", 12), bg=THEME["panel2"], fg=THEME["text"], width=10)
		pace_menu["menu"].config(font=("Avenir", 11))
		pace_menu.grid(row=1, column=1, padx=7, pady=6)

		tk.Label(config, text="Predict Winner:", font=("Avenir", 13, "bold"), bg=THEME["panel"], fg=THEME["title"]).grid(row=2, column=0, padx=7, pady=6, sticky="e")
		self.bet_menu = tk.OptionMenu(config, self.bet_var, "Auto")
		self.bet_menu.config(font=("Avenir", 12), bg=THEME["panel2"], fg=THEME["text"], width=10)
		self.bet_menu["menu"].config(font=("Avenir", 11))
		self.bet_menu.grid(row=2, column=1, padx=7, pady=6)

		tk.Label(
			config,
			text="Custom Racers:",
			font=("Avenir", 13, "bold"),
			bg=THEME["panel"],
			fg=THEME["title"],
		).grid(row=3, column=0, padx=7, pady=6, sticky="e")
		custom_entry = tk.Entry(
			config,
			textvariable=self.custom_racers_var,
			font=("Avenir", 12),
			width=28,
			justify="left",
		)
		custom_entry.grid(row=3, column=1, padx=7, pady=6)
		custom_entry.bind("<KeyRelease>", self._refresh_bet_options_event)

		tk.Label(
			config,
			text="Example: Flash, Storm, Blaze",
			font=("Avenir", 10),
			bg=THEME["panel"],
			fg=THEME["muted"],
		).grid(row=4, column=1, padx=7, pady=(0, 6), sticky="w")

		self._refresh_bet_options()

		self.setup_feedback = tk.Label(
			panel,
			text="",
			font=("Avenir", 12, "bold"),
			bg=THEME["panel"],
			fg=THEME["bad"],
		)
		self.setup_feedback.pack(pady=(6, 8))

		tk.Button(
			panel,
			text="Start Race",
			command=self._start_new_race,
			bg=THEME["good"],
			fg=THEME["text"],
			activeforeground=THEME["text"],
			font=("Avenir", 16, "bold"),
			padx=28,
			pady=12,
			cursor="hand2",
		).pack(pady=10)

		stats_text = self._session_stats_text()
		tk.Label(
			panel,
			text=stats_text,
			justify="left",
			font=("Avenir", 12),
			bg=THEME["panel"],
			fg=THEME["muted"],
		).pack(pady=(12, 4), anchor="w", padx=32)

		tk.Label(
			panel,
			text="Enter = start race, Space = pause/resume during race",
			font=("Avenir", 11),
			bg=THEME["panel"],
			fg=THEME["muted"],
		).pack(pady=(2, 12))

		self.root.bind("<Return>", lambda _event: self._start_new_race())

	def _build_racer_config(self):
		raw = self.custom_racers_var.get().strip()
		if raw:
			names = [name.strip() for name in raw.split(",") if name.strip()]
			if len(names) < 2:
				return None, None, "Add at least 2 custom racers separated by commas."
			names = names[:10]
			racers = len(names)
		else:
			try:
				racers = int(self.racers_count_var.get())
			except (ValueError, tk.TclError):
				return None, None, "Racers must be a number from 2 to 10."

			if not 2 <= racers <= 10:
				return None, None, "Racers must be between 2 and 10."

			names = [f"Racer {i + 1}" for i in range(racers)]

		colors = RACER_COLORS[:len(names)]
		return names, colors, None

	def _refresh_bet_options_event(self, _event):
		self._refresh_bet_options()

	def _refresh_bet_options(self):
		names, colors, _error = self._build_racer_config()
		if not names:
			return

		self.active_names = names
		self.active_colors = colors

		menu = self.bet_menu["menu"]
		menu.delete(0, "end")
		menu.add_command(label="Auto", command=tk._setit(self.bet_var, "Auto"))
		for name in self.active_names:
			menu.add_command(label=name, command=tk._setit(self.bet_var, name))

		if self.bet_var.get() not in ["Auto"] + self.active_names:
			self.bet_var.set("Auto")

	def _set_feedback(self, text, is_error=False):
		color = THEME["bad"] if is_error else THEME["title"]
		if hasattr(self, "setup_feedback") and self.setup_feedback.winfo_exists():
			self.setup_feedback.config(text=text, fg=color)
			return
		if hasattr(self, "feedback_lbl") and self.feedback_lbl.winfo_exists():
			self.feedback_lbl.config(text=text, fg=color)
			return
		if text:
			messagebox.showerror("Race Setup", text) if is_error else messagebox.showinfo("Race", text)

	def _start_new_race(self):
		names, colors, error = self._build_racer_config()
		if error:
			self._set_feedback(error, is_error=True)
			return

		pairs = list(zip(names, colors))
		random.shuffle(pairs)
		self.active_names = [name for name, _ in pairs]
		self.active_colors = [color for _, color in pairs]
		self._set_feedback("")
		self._show_race_screen()
		self._init_race_objects()
		self._run_race_loop()

	def _show_race_screen(self):
		self._clear_window()
		self._set_background()
		self.root.unbind("<Return>")

		panel = tk.Frame(self.root, bg=THEME["panel"], relief=tk.RAISED, bd=3)
		panel.pack(expand=True, padx=22, pady=20, fill=tk.BOTH)

		header = tk.Frame(panel, bg=THEME["panel"])
		header.pack(fill="x", padx=16, pady=(14, 6))

		tk.Label(
			header,
			text="Live Race",
			font=("Avenir", 28, "bold"),
			bg=THEME["panel"],
			fg=THEME["title"],
		).pack(side="left")

		self.time_lbl = tk.Label(
			header,
			text="Time: 0.00s",
			font=("Avenir", 14, "bold"),
			bg=THEME["panel"],
			fg=THEME["text"],
		)
		self.time_lbl.pack(side="right")

		self.track = tk.Canvas(panel, width=TRACK_W, height=TRACK_H, bg="#F7F7F2", highlightthickness=1, highlightbackground="#D2C9B3")
		self.track.pack(padx=14, pady=8)

		footer = tk.Frame(panel, bg=THEME["panel"])
		footer.pack(fill="x", padx=16, pady=(8, 12))

		left = tk.Frame(footer, bg=THEME["panel"])
		left.pack(side="left", fill="both", expand=True)

		self.feedback_lbl = tk.Label(
			left,
			text="Race in progress...",
			font=("Avenir", 13, "bold"),
			bg=THEME["panel"],
			fg=THEME["title"],
		)
		self.feedback_lbl.pack(anchor="w", pady=(0, 4))

		self.leaderboard_lbl = tk.Label(
			left,
			text="",
			justify="left",
			font=("Avenir", 12),
			bg=THEME["panel"],
			fg=THEME["text"],
		)
		self.leaderboard_lbl.pack(anchor="w")

		right = tk.Frame(footer, bg=THEME["panel"])
		right.pack(side="right")

		self.pause_btn = tk.Button(
			right,
			text="Pause",
			command=self._toggle_pause,
			bg="#E9C46A",
			fg=THEME["text"],
			activeforeground=THEME["text"],
			font=("Avenir", 13, "bold"),
			padx=16,
			pady=10,
			cursor="hand2",
		)
		self.pause_btn.grid(row=0, column=0, padx=6)

		tk.Button(
			right,
			text="Race Again",
			command=self._start_new_race,
			bg="#2A9D8F",
			fg=THEME["text"],
			activeforeground=THEME["text"],
			font=("Avenir", 13, "bold"),
			padx=16,
			pady=10,
			cursor="hand2",
		).grid(row=0, column=1, padx=6)

		tk.Button(
			right,
			text="Back To Setup",
			command=self._show_setup_screen,
			bg="#D94F4F",
			fg=THEME["text"],
			activeforeground=THEME["text"],
			font=("Avenir", 13, "bold"),
			padx=16,
			pady=10,
			cursor="hand2",
		).grid(row=0, column=2, padx=6)

		self.root.bind("<space>", lambda _event: self._toggle_pause())

	def _init_race_objects(self):
		self.racers = []
		self.running = True
		self.paused = False
		self.pause_btn.config(text="Pause")

		self.track.delete("all")
		lane_count = len(self.active_colors)
		lane_h = TRACK_H / lane_count
		self.finish_x = TRACK_W - 78
		start_x = 56

		self.track.create_rectangle(0, 0, TRACK_W, TRACK_H, fill="#FBFAF5", outline="")

		for i in range(lane_count):
			y0 = i * lane_h
			y1 = (i + 1) * lane_h
			lane_fill = "#F6EFE1" if i % 2 == 0 else "#EFE7D7"
			self.track.create_rectangle(0, y0, TRACK_W, y1, fill=lane_fill, outline="")
			self.track.create_line(0, y1, TRACK_W, y1, fill="#D5CDBB")

		self.track.create_line(self.finish_x, 0, self.finish_x, TRACK_H, width=4, fill="#1F2933")
		self.track.create_text(self.finish_x + 26, 18, text="FINISH", angle=90, fill="#1F2933", font=("Avenir", 10, "bold"))

		for index, (name, color) in enumerate(zip(self.active_names, self.active_colors)):
			center_y = index * lane_h + lane_h / 2
			lane_top = center_y - 15
			lane_bottom = center_y + 15

			shell = self.track.create_oval(start_x - 16, lane_top, start_x + 16, lane_bottom, fill=color, outline="#1F2933", width=1)
			head = self.track.create_oval(start_x + 13, center_y - 7, start_x + 27, center_y + 7, fill="#3A3A3A", outline="")
			tag = self.track.create_text(20, center_y, text=str(index + 1), fill="#1F2933", font=("Avenir", 11, "bold"))

			self.racers.append(
				{
					"name": name,
					"color": color,
					"x": start_x,
					"speed": random.uniform(1.8, 3.4),
					"shell": shell,
					"head": head,
					"tag": tag,
					"finished": False,
				}
			)

		self.race_start_time = time.time()
		self._update_timer()
		self._update_leaderboard()

	def _speed_factor(self):
		pace = self.speed_var.get()
		if pace == "Slow":
			return 0.75
		if pace == "Fast":
			return 1.35
		return 1.0

	def _run_race_loop(self):
		if not self.running:
			return

		if self.paused:
			self.race_job = self.root.after(30, self._run_race_loop)
			return

		factor = self._speed_factor()
		winner = None

		for racer in self.racers:
			if racer["finished"]:
				continue

			drift = random.uniform(-0.35, 0.95)
			surge = 1.0
			if random.random() < 0.03:
				surge = random.uniform(1.35, 1.8)

			racer["speed"] = max(1.2, min(7.0, racer["speed"] + drift))
			step = racer["speed"] * surge * factor
			racer["x"] += step

			if racer["x"] >= self.finish_x - 10:
				racer["x"] = self.finish_x - 10
				racer["finished"] = True
				winner = racer

			self._move_racer(racer)

		self._update_leaderboard()

		if winner:
			self._complete_race(winner)
			return

		self.race_job = self.root.after(35, self._run_race_loop)

	def _move_racer(self, racer):
		x = racer["x"]
		shell_box = self.track.bbox(racer["shell"])
		head_box = self.track.bbox(racer["head"])
		if not shell_box or not head_box:
			return

		shell_center_x = (shell_box[0] + shell_box[2]) / 2
		dx_shell = x - shell_center_x
		self.track.move(racer["shell"], dx_shell, 0)

		head_center_x = (head_box[0] + head_box[2]) / 2
		dx_head = x + 15 - head_center_x
		self.track.move(racer["head"], dx_head, 0)

	def _update_leaderboard(self):
		sorted_racers = sorted(self.racers, key=lambda r: r["x"], reverse=True)
		lines = []
		for i, racer in enumerate(sorted_racers[:5], start=1):
			pct = max(0.0, min(100.0, ((racer["x"] - 56) / (self.finish_x - 66)) * 100.0))
			lines.append(f"{i}. {racer['name']}  {pct:5.1f}%")
		self.leaderboard_lbl.config(text="\n".join(lines))

	def _update_timer(self):
		if not self.running:
			return

		if not self.paused:
			elapsed = time.time() - self.race_start_time
			self.time_lbl.config(text=f"Time: {elapsed:.2f}s")

		self.timer_job = self.root.after(80, self._update_timer)

	def _toggle_pause(self):
		if not self.running:
			return
		self.paused = not self.paused
		if self.paused:
			self.pause_btn.config(text="Resume")
			self.feedback_lbl.config(text="Race paused.", fg=THEME["bad"])
		else:
			self.pause_btn.config(text="Pause")
			self.feedback_lbl.config(text="Race resumed.", fg=THEME["title"])

	def _complete_race(self, winner):
		self.running = False
		elapsed = time.time() - self.race_start_time

		self.races_played += 1
		picked = self.bet_var.get()

		if picked == "Auto":
			picked = random.choice(self.active_names)

		bet_correct = picked == winner["name"]
		if bet_correct:
			self.correct_bets += 1
			self.current_streak += 1
			self.best_streak = max(self.best_streak, self.current_streak)
		else:
			self.current_streak = 0

		if self.best_time is None or elapsed < self.best_time:
			self.best_time = elapsed

		msg_color = THEME["good"] if bet_correct else THEME["bad"]
		status = "Prediction correct" if bet_correct else "Prediction missed"
		self.feedback_lbl.config(
			text=f"Winner: {winner['name']} | {status} | Time: {elapsed:.2f}s",
			fg=msg_color,
		)

		self._stop_race_loop()

		messagebox.showinfo(
			"Race Finished",
			(
				f"Winner: {winner['name']}\n"
				f"Winner color: {winner['color']}\n"
				f"Your pick: {picked}\n"
				f"{status}\n\n"
				f"Race time: {elapsed:.2f}s\n"
				f"Season stats:\n{self._session_stats_text()}"
			),
		)

	def _stop_race_loop(self):
		self.running = False
		if self.race_job:
			self.root.after_cancel(self.race_job)
			self.race_job = None
		if self.timer_job:
			self.root.after_cancel(self.timer_job)
			self.timer_job = None

	def _session_stats_text(self):
		acc = (self.correct_bets / self.races_played * 100.0) if self.races_played else 0.0
		best_time_text = f"{self.best_time:.2f}s" if self.best_time is not None else "-"
		return (
			f"Races played: {self.races_played}\n"
			f"Correct predictions: {self.correct_bets} ({acc:.1f}%)\n"
			f"Current streak: {self.current_streak} | Best streak: {self.best_streak}\n"
			f"Best race time: {best_time_text}"
		)


def main():
	root = tk.Tk()
	TurtleRaceUI(root)
	root.mainloop()


if __name__ == "__main__":
	main()