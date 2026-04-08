import tkinter as tk
from tkinter import messagebox
from pathlib import Path


class AdventureGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Interactive Adventure 🗺️")
        self.root.geometry("540x540")
        self.root.minsize(480, 480)

        self.photo = None
        self.player_name = ""
        self.current_scene = "start"
        self.choices_made = []
        self.score = 0
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

        # Story data structure - EXPANDED ADVENTURE
        self.story = {
            "start": {
                "text": "You are standing at the start of your adventure.",
                "options": [
                    {"text": "Enter your name", "action": "get_name"}
                ]
            },
            "road": {
                "text": "You wake up in a mysterious forest. The air is foggy and sounds of wildlife echo around you.\nYou find three paths ahead.",
                "options": [
                    {"text": "Take the LEFT path (darker, mysterious)", "next": "dark_forest", "score": 0},
                    {"text": "Take the CENTER path (well-trodden)", "next": "village", "score": 5},
                    {"text": "Take the RIGHT path (narrow, overgrown)", "next": "cliff", "score": 0}
                ]
            },
            "dark_forest": {
                "text": "You venture into a dark forest. Suddenly, you encounter a wise old wizard!\nHe offers you a choice.",
                "options": [
                    {"text": "Ask for his magic amulet", "next": "wizard_fight", "score": -15},
                    {"text": "Ask for directions to treasure", "next": "wizard_map", "score": 20},
                    {"text": "Ignore him and move on", "next": "forest_lost", "score": -5}
                ]
            },
            "wizard_fight": {
                "text": "The wizard becomes angry and attacks you with dark magic!\nYou are overwhelmed and fall to the ground.\nGame Over - You were no match for his power.",
                "options": [
                    {"text": "Play Again", "action": "restart"}
                ]
            },
            "wizard_map": {
                "text": "The wizard smiles and gives you an ancient treasure map!\nHe points to the north. You feel lucky.",
                "options": [
                    {"text": "Follow the map north", "next": "mountain", "score": 10},
                    {"text": "Show the map to others first", "next": "village", "score": 5}
                ]
            },
            "forest_lost": {
                "text": "You wander deeper into the forest and become hopelessly lost.\nAfter days of wandering, you collapse from exhaustion.\nGame Over - Lost in the wilderness.",
                "options": [
                    {"text": "Play Again", "action": "restart"}
                ]
            },
            "village": {
                "text": "You reach a peaceful village! The locals welcome you warmly.\nAn innkeeper offers you three options.",
                "options": [
                    {"text": "Rest and gather information", "next": "tavern", "score": 5},
                    {"text": "Challenge the local champion to a duel", "next": "duel", "score": 10},
                    {"text": "Steal from the village treasury", "next": "caught", "score": -20}
                ]
            },
            "tavern": {
                "text": "At the tavern, an old merchant tells you about a legendary castle in the mountains.\nHe gives you supplies for the journey.",
                "options": [
                    {"text": "Head to the mountain castle", "next": "mountain", "score": 10},
                    {"text": "Ask about secret shortcuts", "next": "secret_cave", "score": 15},
                    {"text": "Stay and enjoy the drinks", "next": "drunk_game", "score": 0}
                ]
            },
            "duel": {
                "text": "You face the champion in combat. Your skills are impressive!",
                "options": [
                    {"text": "Fight honorably", "next": "duel_win", "score": 25},
                    {"text": "Use dirty tricks", "next": "duel_cheat", "score": -10},
                    {"text": "Back down and apologize", "next": "tavern", "score": 0}
                ]
            },
            "duel_win": {
                "text": "You defeat the champion honorably! The crowd cheers!\nThe champion gifts you his family's gold ring.",
                "options": [
                    {"text": "Go to the mountain castle", "next": "castle_rich", "score": 15},
                    {"text": "Explore the secret cave", "next": "secret_cave", "score": 10}
                ]
            },
            "duel_cheat": {
                "text": "You use dirty tricks but the crowd sees you!\nThe village turns hostile against you.\nGame Over - You are banished from the village.",
                "options": [
                    {"text": "Play Again", "action": "restart"}
                ]
            },
            "caught": {
                "text": "Guards catch you stealing! You are thrown in jail.\nGame Over - Imprisoned for theft.",
                "options": [
                    {"text": "Play Again", "action": "restart"}
                ]
            },
            "secret_cave": {
                "text": "You find a hidden cave filled with glowing crystals!\nInside, you discover ancient technology and riches.",
                "options": [
                    {"text": "Collect the crystals and treasures", "next": "crystal_ending", "score": 30},
                    {"text": "Study the ancient technology", "next": "tech_master", "score": 25},
                    {"text": "Leave it untouched and respect the ancients", "next": "wisdom_ending", "score": 20}
                ]
            },
            "drunk_game": {
                "text": "You get drunk with the locals and play cards.\nYou win big! The next morning you wake with a headache.",
                "options": [
                    {"text": "Take your winnings and leave", "next": "quick_escape", "score": 10},
                    {"text": "Spend the winnings on more revelry", "next": "broke_morning", "score": -5}
                ]
            },
            "quick_escape": {
                "text": "You escape the village with your newfound wealth.\nYou decide to build a new life elsewhere. Ending - Wealthy Wanderer.",
                "options": [
                    {"text": "Play Again", "action": "restart"}
                ]
            },
            "broke_morning": {
                "text": "You spent all the money! Now broke again.\nYou must continue your quest penniless.\nGame Over - Broke and defeated.",
                "options": [
                    {"text": "Play Again", "action": "restart"}
                ]
            },
            "cliff": {
                "text": "You climb a narrow cliff path. The wind is strong.\nAt the top, you see an ancient temple!",
                "options": [
                    {"text": "Enter the temple carefully", "next": "temple", "score": 10},
                    {"text": "Search the cliff for hidden treasures", "next": "cliff_treasure", "score": 15},
                    {"text": "Turn back, it looks too dangerous", "next": "coward_end", "score": -10}
                ]
            },
            "temple": {
                "text": "Inside the ancient temple, you find religious artifacts and scrolls.\nA guardian statue comes to life!",
                "options": [
                    {"text": "Fight the guardian bravely", "next": "temple_fight", "score": -15},
                    {"text": "Solve the temple puzzles", "next": "temple_puzzle", "score": 20},
                    {"text": "Flee from the temple", "next": "temple_escape", "score": 5}
                ]
            },
            "temple_fight": {
                "text": "The stone guardian is too powerful!\nYou are crushed under its weight.\nGame Over - Defeated by the guardian.",
                "options": [
                    {"text": "Play Again", "action": "restart"}
                ]
            },
            "temple_puzzle": {
                "text": "Your intellect solves the ancient puzzles!\nThe temple glows, revealing a secret chamber with unlimited treasure.",
                "options": [
                    {"text": "Claim the treasure - VICTORY!", "next": "ultimate_victory", "score": 40}
                ]
            },
            "temple_escape": {
                "text": "You escape the temple with some artifacts.\nThey are quite valuable. Ending - Lucky Escape.",
                "options": [
                    {"text": "Play Again", "action": "restart"}
                ]
            },
            "cliff_treasure": {
                "text": "You search and find ancient coins and jewels hidden in crevices!\nYou become rich from this treasure.",
                "options": [
                    {"text": "Return to village as a rich adventurer", "next": "hero_return", "score": 20},
                    {"text": "Continue exploring for more", "next": "cliff_greedy", "score": 5}
                ]
            },
            "hero_return": {
                "text": "You return to the village a wealthy hero!\nThe villagers celebrate your success. Ending - Legendary Hero.",
                "options": [
                    {"text": "Play Again", "action": "restart"}
                ]
            },
            "cliff_greedy": {
                "text": "You get greedy and search too much.\nThe cliff crumbles beneath you!\nGame Over - Buried by greed.",
                "options": [
                    {"text": "Play Again", "action": "restart"}
                ]
            },
            "coward_end": {
                "text": "You turn back and descend the cliff.\nYou return to an ordinary life.\nGame Over - Ended your adventure early.",
                "options": [
                    {"text": "Play Again", "action": "restart"}
                ]
            },
            "mountain": {
                "text": "You climb the mountain. At the peak stands a magnificent castle!\nGuards stand at the entrance.",
                "options": [
                    {"text": "Approach the guards with confidence", "next": "castle_talk", "score": 10},
                    {"text": "Sneak around the guards", "next": "castle_sneak", "score": 5},
                    {"text": "Challenge the guards to combat", "next": "castle_fight", "score": -10}
                ]
            },
            "castle_rich": {
                "text": "You arrive at the castle as a known hero!\nThe guards welcome you with honor.\nYou negotiate for the castle's treasures.",
                "options": [
                    {"text": "Accept their offer - VICTORY!", "next": "ultimate_victory", "score": 35}
                ]
            },
            "castle_talk": {
                "text": "The guards respect your approach.\nThey allow you to enter and meet the castle lord.",
                "options": [
                    {"text": "Ask for the treasure", "next": "negotiate_treasure", "score": 15},
                    {"text": "Ask the lord for a quest", "next": "castle_quest", "score": 10}
                ]
            },
            "negotiate_treasure": {
                "text": "The lord respects your honesty.\nHe gives you his family treasure! VICTORY!",
                "options": [
                    {"text": "Accept and claim victory", "next": "ultimate_victory", "score": 30}
                ]
            },
            "castle_quest": {
                "text": "The lord needs you to retrieve something valuable from a dragon's cave.\nYou venture onward...",
                "options": [
                    {"text": "Face the dragon directly", "next": "dragon_fight", "score": -20},
                    {"text": "Steal the item while the dragon sleeps", "next": "dragon_stealth", "score": 15}
                ]
            },
            "dragon_fight": {
                "text": "The dragon is massive and ancient!\nOne fire breath ends you.\nGame Over - Incinerated by dragon fire.",
                "options": [
                    {"text": "Play Again", "action": "restart"}
                ]
            },
            "dragon_stealth": {
                "text": "You carefully steal the item while the dragon sleeps.\nThe lord is amazed and rewards you greatly!",
                "options": [
                    {"text": "Claim your ultimate victory", "next": "ultimate_victory", "score": 32}
                ]
            },
            "castle_sneak": {
                "text": "You sneak past the guards successfully!\nInside, you find a vault room.",
                "options": [
                    {"text": "Open the vault and take everything", "next": "vault_treasure", "score": 25},
                    {"text": "Search for the lord's chambers", "next": "lord_chambers", "score": 10}
                ]
            },
            "vault_treasure": {
                "text": "You successfully raid the vault!\nYou escape with a fortune!",
                "options": [
                    {"text": "Escape and claim victory", "next": "ultimate_victory", "score": 28}
                ]
            },
            "lord_chambers": {
                "text": "You find the lord's personal diary revealing a great secret.\nWith this knowledge, you gain power and influence.",
                "options": [
                    {"text": "Use the knowledge wisely", "next": "ultimate_victory", "score": 25}
                ]
            },
            "castle_fight": {
                "text": "You fight the guards but they are well-trained.\nYou manage to defeat them!\nBut castle reinforcements arrive...",
                "options": [
                    {"text": "Run away", "next": "escape_castle", "score": -5},
                    {"text": "Continue fighting", "next": "final_battle", "score": -15}
                ]
            },
            "escape_castle": {
                "text": "You escape the castle with your life but nothing else.\nYou are now a fugitive.\nGame Over - Hunted.",
                "options": [
                    {"text": "Play Again", "action": "restart"}
                ]
            },
            "final_battle": {
                "text": "Overwhelming numbers defeat you.\nGame Over - Defeated in combat.",
                "options": [
                    {"text": "Play Again", "action": "restart"}
                ]
            },
            "crystal_ending": {
                "text": "The glowing crystals are incredibly valuable!\nYou become immensely wealthy and powerful!\nENDING - MASTER OF CRYSTALS",
                "options": [
                    {"text": "Play Again", "action": "restart"}
                ]
            },
            "tech_master": {
                "text": "You unlock the ancient technology!\nYou become a brilliant inventor and sage!\nENDING - TECHNOLOGICAL PIONEER",
                "options": [
                    {"text": "Play Again", "action": "restart"}
                ]
            },
            "wisdom_ending": {
                "text": "Your respect for history and the ancients grants you profound wisdom.\nYou become a legendary sage!\nENDING - THE WISE ONE",
                "options": [
                    {"text": "Play Again", "action": "restart"}
                ]
            },
            "ultimate_victory": {
                "text": f"🎉 CONGRATULATIONS! 🎉\n\nYou have achieved ULTIMATE VICTORY!\n\nYour journey was legendary, and your name will be remembered forever.\n\nFinal Score: {self.score}",
                "options": [
                    {"text": "Play Again", "action": "restart"}
                ]
            }
        }

        self.setup_ui()

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
            
            bg_label = tk.Label(self.root, image=self.photo)
            bg_label.image = self.photo
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception:
            self._draw_gradient_background(width, height)

    def setup_ui(self):
        self.set_background()

        self.main_frame = tk.Frame(self.root, bg=self.theme["panel"], relief=tk.RAISED, bd=3)
        self.main_frame.pack(expand=True, padx=38, pady=38, fill=tk.BOTH)

        self.title_label = tk.Label(
            self.main_frame,
            text="Interactive Adventure 🗺️",
            font=("Avenir", 32, "bold"),
            bg=self.theme["panel"],
            fg=self.theme["title"],
        )
        self.title_label.pack(pady=(20, 12))

        self.info_label = tk.Label(
            self.main_frame,
            text="Score: 0 | Choices: 0",
            font=("Avenir", 11),
            bg=self.theme["panel"],
            fg="#8B5E34",
        )
        self.info_label.pack(pady=(0, 12))

        self.story_text = tk.Text(
            self.main_frame,
            height=10,
            width=50,
            font=("Avenir", 12),
            relief=tk.SUNKEN,
            bd=2,
            bg="#FFFDF7",
            fg="#1F2933",
            wrap=tk.WORD,
            state=tk.DISABLED,
        )
        self.story_text.pack(pady=(0, 12), padx=2)

        self.buttons_frame = tk.Frame(self.main_frame, bg=self.theme["panel"])
        self.buttons_frame.pack(pady=4, fill=tk.BOTH, expand=True)

        self.show_scene("start")

    def show_scene(self, scene_name):
        if scene_name not in self.story:
            scene_name = "start"

        self.current_scene = scene_name
        scene = self.story[scene_name]

        # Update story text
        self.story_text.config(state=tk.NORMAL)
        self.story_text.delete("1.0", tk.END)
        self.story_text.insert(tk.END, scene["text"])
        self.story_text.config(state=tk.DISABLED)

        # Clear old buttons
        for widget in self.buttons_frame.winfo_children():
            widget.destroy()

        # Create new buttons
        for i, option in enumerate(scene["options"]):
            if option.get("action") == "get_name":
                self._create_name_input()
            else:
                self._create_choice_button(option, i)

        # Update info
        self.info_label.config(
            text=f"Score: {self.score} | Choices: {len(self.choices_made)}"
        )

    def _create_name_input(self):
        name_frame = tk.Frame(self.buttons_frame, bg=self.theme["panel"])
        name_frame.pack(pady=6, fill=tk.X)

        tk.Label(
            name_frame,
            text="Enter your name:",
            font=("Avenir", 11),
            bg=self.theme["panel"],
            fg=self.theme["text"],
        ).pack(side=tk.LEFT, padx=4)

        name_entry = tk.Entry(
            name_frame,
            font=("Avenir", 11),
            width=20,
        )
        name_entry.pack(side=tk.LEFT, padx=4)
        name_entry.focus()

        def start_adventure():
            name = name_entry.get().strip()
            if name:
                self.player_name = name
                self.story_text.config(state=tk.NORMAL)
                self.story_text.delete("1.0", tk.END)
                self.story_text.insert(tk.END, f"Welcome, {name}, to this interactive adventure!\n\nYou stand at the beginning of an epic journey full of choices and consequences. Will you survive?")
                self.story_text.config(state=tk.DISABLED)

                for widget in self.buttons_frame.winfo_children():
                    widget.destroy()

                tk.Button(
                    self.buttons_frame,
                    text="Begin Adventure",
                    command=lambda: self.show_scene("road"),
                    bg=self.theme["button_primary"],
                    fg=self.theme["button_text"],
                    font=("Avenir", 12, "bold"),
                    padx=20,
                    pady=10,
                    relief=tk.RAISED,
                    bd=2,
                    activebackground="#166846",
                    activeforeground=self.theme["button_text"],
                    cursor="hand2",
                ).pack(pady=6)
            else:
                messagebox.showerror("Input Error", "Please enter a name")

        tk.Button(
            name_frame,
            text="Start",
            command=start_adventure,
            bg=self.theme["button_primary"],
            fg=self.theme["button_text"],
            font=("Avenir", 10, "bold"),
            padx=12,
            pady=6,
            relief=tk.RAISED,
            bd=2,
            activebackground="#166846",
            activeforeground=self.theme["button_text"],
            cursor="hand2",
        ).pack(side=tk.LEFT, padx=4)

    def _create_choice_button(self, option, index):
        def on_click():
            choice_text = option["text"]
            self.choices_made.append(choice_text)
            self.score += option.get("score", 0)

            if option.get("action") == "restart":
                self.player_name = ""
                self.choices_made = []
                self.score = 0
                self.show_scene("start")
            else:
                next_scene = option.get("next")
                if next_scene:
                    self.show_scene(next_scene)

        tk.Button(
            self.buttons_frame,
            text=option["text"],
            command=on_click,
            bg=self.theme["button_secondary"] if index % 2 == 0 else self.theme["button_primary"],
            fg=self.theme["button_text"],
            font=("Avenir", 11, "bold"),
            padx=18,
            pady=9,
            relief=tk.RAISED,
            bd=2,
            activebackground="#1D4F91" if index % 2 == 0 else "#166846",
            activeforeground=self.theme["button_text"],
            cursor="hand2",
            wraplength=280,
            justify=tk.CENTER,
        ).pack(pady=4, fill=tk.X, padx=4)


if __name__ == "__main__":
    root = tk.Tk()
    game = AdventureGame(root)
    root.mainloop()