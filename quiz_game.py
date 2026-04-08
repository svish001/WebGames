import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

QUESTIONS = [
    {"q": "What color is the sky on a clear day?", "a": "blue"},
    {"q": "How many days are in a week?", "a": "7"},
    {"q": "What is 2 + 2?", "a": "4"},
    {"q": "What do bees make?", "a": "honey"},
    {"q": "Which planet do we live on?", "a": "earth"},
    {"q": "What gas do humans breathe in to survive?", "a": "oxygen"},
    {"q": "How many months are in a year?", "a": "12"},
    {"q": "What do you call frozen water?", "a": "ice"},
    {"q": "What is the opposite of hot?", "a": "cold"},
    {"q": "What do plants need from sunlight to make food?", "a": "light"}
]


class QuizGameUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Computer Quiz Game")
        self.root.geometry("540x540")
        self.root.minsize(500, 600)

        self.photo = None
        self.current_index = 0
        self.score = 0
        self.answered = False

        self.theme = {
            "panel": "#F8F3E6",
            "title": "#193549",
            "accent": "#D94F4F",
            "text": "#1F2933",
            "button_primary": "#1C7C54",
            "button_secondary": "#276FBF",
            "button_danger": "#FCA5A5",
            "button_text": "#111827",
        }

        self.setup_start_screen()

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
            img = Image.open("wp3594884.jpg")
            img = img.resize((width, height), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(img)
            bg_label = tk.Label(self.root, image=self.photo)
            bg_label.image = self.photo
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception:
            self._draw_gradient_background(width, height)

    def _clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def setup_start_screen(self):
        self._clear_window()
        self.root.unbind("<Escape>")
        self.set_background()

        frame = tk.Frame(self.root, bg=self.theme["panel"], relief=tk.RAISED, bd=3)
        frame.pack(expand=True, padx=38, pady=38, fill=tk.BOTH)

        tk.Label(
            frame,
            text="Computer Quiz Game",
            font=("Avenir", 34, "bold"),
            bg=self.theme["panel"],
            fg=self.theme["title"],
        ).pack(pady=(28, 8))

        tk.Label(
            frame,
            text=f"Answer {len(QUESTIONS)} fun questions",
            font=("Avenir", 16),
            bg=self.theme["panel"],
            fg=self.theme["text"],
        ).pack(pady=8)

        tk.Label(
            frame,
            text="Type your answer and press Enter",
            font=("Avenir", 12, "italic"),
            bg=self.theme["panel"],
            fg=self.theme["accent"],
        ).pack(pady=(8, 20))

        tk.Button(
            frame,
            text="Start Quiz",
            command=self.start_quiz,
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

        self.root.bind("<Return>", lambda _event: self.start_quiz())

    def start_quiz(self):
        self.root.unbind("<Return>")
        self.current_index = 0
        self.score = 0
        self.setup_question_screen()

    def setup_question_screen(self):
        self._clear_window()
        self.set_background()
        self.answered = False

        frame = tk.Frame(self.root, bg=self.theme["panel"], relief=tk.RAISED, bd=3)
        frame.pack(expand=True, padx=38, pady=38, fill=tk.BOTH)

        tk.Label(
            frame,
            text=f"Question {self.current_index + 1}/{len(QUESTIONS)}",
            font=("Avenir", 30, "bold"),
            bg=self.theme["panel"],
            fg=self.theme["button_secondary"],
        ).pack(pady=(24, 8))

        tk.Label(
            frame,
            text=f"Score: {self.score}",
            font=("Avenir", 16),
            bg=self.theme["panel"],
            fg=self.theme["text"],
        ).pack(pady=4)

        self.question_label = tk.Label(
            frame,
            text=QUESTIONS[self.current_index]["q"],
            font=("Avenir", 18, "bold"),
            bg=self.theme["panel"],
            fg="#8B5E34",
            wraplength=400,
            justify="center",
        )
        self.question_label.pack(pady=(8, 16))

        self.answer_entry = tk.Entry(
            frame,
            font=("Avenir", 20),
            width=20,
            relief=tk.SUNKEN,
            bd=3,
            justify="center",
        )
        self.answer_entry.pack(pady=10)
        self.answer_entry.focus()

        self.feedback = tk.Label(
            frame,
            text="",
            font=("Avenir", 14, "bold"),
            bg=self.theme["panel"],
            fg="#1D4ED8",
            wraplength=400,
            justify="center",
        )
        self.feedback.pack(pady=10)

        self.submit_btn = tk.Button(
            frame,
            text="Submit Answer",
            command=self.submit_answer,
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
        )
        self.submit_btn.pack(pady=8)

        self.next_btn = tk.Button(
            frame,
            text="Next Question",
            command=self.next_question,
            state=tk.DISABLED,
            bg=self.theme["button_primary"],
            fg=self.theme["button_text"],
            font=("Avenir", 14, "bold"),
            padx=24,
            pady=11,
            relief=tk.RAISED,
            bd=2,
            activebackground="#166846",
            activeforeground=self.theme["button_text"],
            cursor="hand2",
        )
        self.next_btn.pack(pady=5)

        tk.Button(
            frame,
            text="Exit to Start",
            command=self.setup_start_screen,
            bg=self.theme["button_danger"],
            fg=self.theme["button_text"],
            font=("Avenir", 14, "bold"),
            padx=24,
            pady=11,
            relief=tk.RAISED,
            bd=2,
            activebackground="#F87171",
            activeforeground=self.theme["button_text"],
            cursor="hand2",
        ).pack(pady=5)

        tk.Label(
            frame,
            text="Enter = submit, Esc = exit",
            font=("Avenir", 11),
            bg=self.theme["panel"],
            fg="#4B5563",
        ).pack(pady=(8, 12))

        self.answer_entry.bind("<Return>", lambda _event: self.submit_answer())
        self.root.bind("<Escape>", lambda _event: self.setup_start_screen())

    def submit_answer(self):
        if self.answered:
            return

        user_answer = self.answer_entry.get().strip().lower()
        if not user_answer:
            messagebox.showerror("Invalid Input", "Please type an answer.")
            self.answer_entry.focus()
            return

        correct_answer = QUESTIONS[self.current_index]["a"]
        if user_answer == correct_answer:
            self.score += 1
            self.feedback.config(text="Correct! Great job.", fg="#047857")
        else:
            self.feedback.config(text=f"Incorrect. Correct answer: {correct_answer}", fg="#B91C1C")

        self.answered = True
        self.submit_btn.config(state=tk.DISABLED)
        self.next_btn.config(state=tk.NORMAL)
        self.answer_entry.config(state=tk.DISABLED)

    def next_question(self):
        self.current_index += 1
        if self.current_index >= len(QUESTIONS):
            self.show_results()
            return
        self.setup_question_screen()

    def show_results(self):
        self._clear_window()
        self.set_background()

        percent = (self.score / len(QUESTIONS)) * 100
        if self.score == len(QUESTIONS):
            performance = "Perfect score. Amazing work!"
            perf_color = "#0F766E"
        elif self.score >= 7:
            performance = "Great job! You know your stuff."
            perf_color = "#1D4ED8"
        elif self.score >= 4:
            performance = "Good effort. Keep practicing."
            perf_color = "#B45309"
        else:
            performance = "Keep going. You will improve fast."
            perf_color = "#B91C1C"

        frame = tk.Frame(self.root, bg=self.theme["panel"], relief=tk.RAISED, bd=3)
        frame.pack(expand=True, padx=38, pady=38, fill=tk.BOTH)

        tk.Label(
            frame,
            text="Quiz Complete",
            font=("Avenir", 34, "bold"),
            bg=self.theme["panel"],
            fg=self.theme["title"],
        ).pack(pady=(32, 16))

        tk.Label(
            frame,
            text=f"Your Score: {self.score}/{len(QUESTIONS)}",
            font=("Avenir", 22, "bold"),
            bg=self.theme["panel"],
            fg=self.theme["button_secondary"],
        ).pack(pady=8)

        tk.Label(
            frame,
            text=f"Accuracy: {percent:.1f}%",
            font=("Avenir", 18),
            bg=self.theme["panel"],
            fg=self.theme["text"],
        ).pack(pady=6)

        tk.Label(
            frame,
            text=performance,
            font=("Avenir", 16, "bold"),
            bg=self.theme["panel"],
            fg=perf_color,
        ).pack(pady=(10, 20))

        tk.Button(
            frame,
            text="Play Again",
            command=self.start_quiz,
            bg=self.theme["button_primary"],
            fg=self.theme["button_text"],
            font=("Avenir", 16, "bold"),
            padx=28,
            pady=12,
            relief=tk.RAISED,
            bd=2,
            activebackground="#166846",
            activeforeground=self.theme["button_text"],
            cursor="hand2",
        ).pack(pady=8)

        tk.Button(
            frame,
            text="Exit",
            command=self.root.destroy,
            bg=self.theme["button_danger"],
            fg=self.theme["button_text"],
            font=("Avenir", 16, "bold"),
            padx=28,
            pady=12,
            relief=tk.RAISED,
            bd=2,
            activebackground="#F87171",
            activeforeground=self.theme["button_text"],
            cursor="hand2",
        ).pack(pady=8)


if __name__ == "__main__":
    root = tk.Tk()
    game = QuizGameUI(root)
    root.mainloop()