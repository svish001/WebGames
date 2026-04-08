import random
import re
import tkinter as tk
from pathlib import Path
from tkinter import messagebox


class MadLibsStudio:
    def __init__(self, root):
        self.root = root
        self.root.title("Mad Libs Studio ✍️")
        self.root.geometry("820x640")
        self.root.minsize(740, 580)

        self.theme = {
            "panel": "#F8F3E6",
            "title": "#193549",
            "text": "#1F2933",
            "muted": "#8B5E34",
            "primary": "#1C7C54",
            "secondary": "#276FBF",
            "warning": "#F59E0B",
            "danger": "#EF4444",
            "button_text": "#111827",
        }

        self.templates = self._load_templates()
        self.current_template_name = ""
        self.current_template = ""
        self.placeholders = []
        self.entries = {}
        self.history = []

        self._draw_gradient_background()
        self._build_ui()
        self._set_initial_template()

    def _draw_gradient_background(self):
        self.bg_canvas = tk.Canvas(self.root, highlightthickness=0)
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)

        width = 1200
        height = 900
        start_rgb = (14, 36, 58)
        end_rgb = (81, 45, 92)
        for i in range(height):
            r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * i / height)
            g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * i / height)
            b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * i / height)
            self.bg_canvas.create_line(0, i, width, i, fill=f"#{r:02x}{g:02x}{b:02x}")

        self.bg_canvas.create_oval(-120, -120, 280, 260, fill="#FFB703", outline="")
        self.bg_canvas.create_oval(700, 40, 1120, 430, fill="#8ECAE6", outline="")
        self.bg_canvas.create_oval(180, 560, 590, 930, fill="#FB8500", outline="")

    def _load_templates(self):
        templates = {
            "Space Mission 🚀": (
                "Captain <name> launched the ship from <place>. "
                "With a <adjective> crew and a box of <plural_noun>, they "
                "faced a <adjective2> alien named <funny_name>. "
                "To survive, they had to <verb> while shouting '<exclamation>!'"
            ),
            "Haunted Mansion 👻": (
                "At midnight, <name> entered the <adjective> mansion carrying a <noun>. "
                "The hall smelled like <food>, and the walls started to <verb>. "
                "A ghost yelled '<exclamation>!' and chased them toward the <place>."
            ),
            "Jungle Quest 🐍": (
                "Explorer <name> crossed the <adjective> jungle with <number> "
                "maps and a <noun>. Suddenly, a giant <animal> appeared and started "
                "to <verb>. The team escaped by jumping into a <vehicle>."
            ),
        }

        custom_story = Path(__file__).with_name("story.txt")
        if custom_story.exists():
            content = custom_story.read_text(encoding="utf-8").strip()
            if content:
                templates["Custom Story 📘"] = content

        return templates

    def _build_ui(self):
        self.main = tk.Frame(self.root, bg=self.theme["panel"], relief=tk.RAISED, bd=3)
        self.main.pack(expand=True, fill=tk.BOTH, padx=26, pady=26)

        tk.Label(
            self.main,
            text="Mad Libs Studio ✍️",
            font=("Avenir", 34, "bold"),
            bg=self.theme["panel"],
            fg=self.theme["title"],
        ).pack(pady=(14, 4))

        self.status = tk.Label(
            self.main,
            text="Build your story by filling every word slot. 🎯",
            font=("Avenir", 11),
            bg=self.theme["panel"],
            fg=self.theme["muted"],
        )
        self.status.pack(pady=(0, 8))

        top = tk.Frame(self.main, bg=self.theme["panel"])
        top.pack(fill=tk.X, padx=10, pady=(0, 8))

        tk.Label(
            top,
            text="Template",
            font=("Avenir", 11, "bold"),
            bg=self.theme["panel"],
            fg=self.theme["text"],
        ).pack(side=tk.LEFT)

        self.template_var = tk.StringVar()
        self.template_menu = tk.OptionMenu(top, self.template_var, *self.templates.keys())
        self.template_menu.config(font=("Avenir", 11), bg="#FFFDF7")
        self.template_menu.pack(side=tk.LEFT, padx=(8, 10))

        tk.Button(
            top,
            text="Load Template 📄",
            command=self.load_template,
            bg=self.theme["secondary"],
            fg=self.theme["button_text"],
            font=("Avenir", 10, "bold"),
            padx=10,
            pady=6,
            relief=tk.RAISED,
            bd=2,
            cursor="hand2",
        ).pack(side=tk.LEFT)

        tk.Button(
            top,
            text="Random Fill 🎲",
            command=self.random_fill,
            bg=self.theme["warning"],
            fg=self.theme["button_text"],
            font=("Avenir", 10, "bold"),
            padx=10,
            pady=6,
            relief=tk.RAISED,
            bd=2,
            cursor="hand2",
        ).pack(side=tk.LEFT, padx=(8, 0))

        tk.Button(
            top,
            text="Clear 🧹",
            command=self.clear_fields,
            bg=self.theme["danger"],
            fg=self.theme["button_text"],
            font=("Avenir", 10, "bold"),
            padx=10,
            pady=6,
            relief=tk.RAISED,
            bd=2,
            cursor="hand2",
        ).pack(side=tk.LEFT, padx=(8, 0))

        body = tk.Frame(self.main, bg=self.theme["panel"])
        body.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 8))

        left = tk.Frame(body, bg="#FFFDF7", relief=tk.SUNKEN, bd=2)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))

        tk.Label(
            left,
            text="Word Inputs",
            font=("Avenir", 12, "bold"),
            bg="#FFFDF7",
            fg=self.theme["title"],
        ).pack(pady=(8, 6))

        self.fields_container = tk.Frame(left, bg="#FFFDF7")
        self.fields_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        right = tk.Frame(body, bg="#FFFDF7", relief=tk.SUNKEN, bd=2)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(6, 0))

        tk.Label(
            right,
            text="Generated Story",
            font=("Avenir", 12, "bold"),
            bg="#FFFDF7",
            fg=self.theme["title"],
        ).pack(pady=(8, 6))

        self.story_output = tk.Text(
            right,
            height=14,
            font=("Avenir", 11),
            bg="#FFFDF7",
            fg=self.theme["text"],
            relief=tk.FLAT,
            wrap=tk.WORD,
            state=tk.DISABLED,
        )
        self.story_output.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        bottom = tk.Frame(self.main, bg=self.theme["panel"])
        bottom.pack(fill=tk.X, padx=10, pady=(0, 8))

        tk.Button(
            bottom,
            text="Create Story ✨",
            command=self.create_story,
            bg=self.theme["primary"],
            fg=self.theme["button_text"],
            font=("Avenir", 12, "bold"),
            padx=16,
            pady=9,
            relief=tk.RAISED,
            bd=2,
            cursor="hand2",
        ).pack(side=tk.LEFT)

        tk.Button(
            bottom,
            text="Show Last Story 🕘",
            command=self.show_last_story,
            bg=self.theme["secondary"],
            fg=self.theme["button_text"],
            font=("Avenir", 12, "bold"),
            padx=16,
            pady=9,
            relief=tk.RAISED,
            bd=2,
            cursor="hand2",
        ).pack(side=tk.LEFT, padx=(8, 0))

        self.score_label = tk.Label(
            bottom,
            text="Creativity Score: 0",
            font=("Avenir", 11, "bold"),
            bg=self.theme["panel"],
            fg=self.theme["muted"],
        )
        self.score_label.pack(side=tk.RIGHT)

    def _set_initial_template(self):
        first_name = next(iter(self.templates.keys()))
        self.template_var.set(first_name)
        self.load_template()

    def _extract_placeholders(self, text):
        return list(dict.fromkeys(re.findall(r"<([^<>]+)>", text)))

    def load_template(self):
        template_name = self.template_var.get()
        if template_name not in self.templates:
            return

        self.current_template_name = template_name
        self.current_template = self.templates[template_name]
        self.placeholders = self._extract_placeholders(self.current_template)

        for widget in self.fields_container.winfo_children():
            widget.destroy()
        self.entries = {}

        if not self.placeholders:
            tk.Label(
                self.fields_container,
                text="No placeholders found in this template.",
                font=("Avenir", 11),
                bg="#FFFDF7",
                fg=self.theme["muted"],
            ).pack(anchor="w", pady=4)
        else:
            for idx, key in enumerate(self.placeholders, start=1):
                row = tk.Frame(self.fields_container, bg="#FFFDF7")
                row.pack(fill=tk.X, pady=3)

                tk.Label(
                    row,
                    text=f"{idx}. {key}",
                    width=16,
                    anchor="w",
                    font=("Avenir", 10, "bold"),
                    bg="#FFFDF7",
                    fg=self.theme["text"],
                ).pack(side=tk.LEFT)

                entry = tk.Entry(row, font=("Avenir", 10), width=24)
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
                self.entries[key] = entry

        self.status.config(text=f"Loaded template: {self.current_template_name} ✅")
        self._set_output("Template loaded. Fill words and click Create Story ✨")
        if self.placeholders:
            first_entry = self.entries[self.placeholders[0]]
            first_entry.focus_set()

    def random_fill(self):
        word_bank = {
            "name": ["Alex", "Mira", "Ravi", "Nora", "Zane"],
            "place": ["Mars", "the attic", "the desert", "Neon City", "the moon base"],
            "adjective": ["weird", "sparkly", "brave", "tiny", "furious"],
            "adjective2": ["glowing", "mysterious", "chaotic", "silent", "gigantic"],
            "verb": ["dance", "sprint", "whisper", "juggle", "teleport"],
            "noun": ["toaster", "helmet", "guitar", "banana", "compass"],
            "plural_noun": ["dragons", "socks", "robots", "cookies", "comets"],
            "funny_name": ["Captain Noodle", "Sir Quack", "Zorp", "Bean Master", "Dr. Wiggles"],
            "food": ["pizza", "chocolate", "pickles", "nachos", "soup"],
            "exclamation": ["Boom", "Yikes", "Hooray", "No way", "Zap"],
            "number": ["3", "7", "12", "21", "42"],
            "animal": ["tiger", "parrot", "python", "llama", "penguin"],
            "vehicle": ["submarine", "hovercraft", "jeep", "balloon", "rocket"],
        }

        for key, entry in self.entries.items():
            options = word_bank.get(key, ["mystery", "epic", "turbo", "cosmic"])
            entry.delete(0, tk.END)
            entry.insert(0, random.choice(options))

        self.status.config(text="Random words filled. Ready to generate! 🎲")

    def clear_fields(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.status.config(text="Inputs cleared. Add new words. 🧹")
        self._set_output("")
        if self.placeholders:
            self.entries[self.placeholders[0]].focus_set()

    def _compute_score(self, values):
        unique_words = len(set(v.lower() for v in values if v.strip()))
        long_words = sum(1 for v in values if len(v.strip()) >= 7)
        return unique_words * 4 + long_words * 3

    def create_story(self):
        if not self.current_template:
            messagebox.showerror("No Template", "Please load a template first.")
            return

        filled = {}
        for key, entry in self.entries.items():
            value = entry.get().strip()
            if not value:
                messagebox.showerror("Missing Input", f"Please fill: {key}")
                entry.focus_set()
                return
            filled[key] = value

        story = self.current_template
        for key, value in filled.items():
            story = story.replace(f"<{key}>", value)

        score = self._compute_score(list(filled.values()))
        self.score_label.config(text=f"Creativity Score: {score}")
        self.history.append(story)
        self._set_output(story)
        self.status.config(text=f"Story created from {self.current_template_name} ✨")

    def show_last_story(self):
        if not self.history:
            messagebox.showinfo("No History", "No stories generated yet.")
            return
        self._set_output(self.history[-1])
        self.status.config(text="Showing last generated story. 🕘")

    def _set_output(self, text):
        self.story_output.config(state=tk.NORMAL)
        self.story_output.delete("1.0", tk.END)
        self.story_output.insert(tk.END, text)
        self.story_output.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    app = MadLibsStudio(root)
    root.mainloop()