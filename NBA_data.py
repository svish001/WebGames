import math
import random

import pygame


WIDTH, HEIGHT = 1120, 760
FPS = 60

COURT_RECT = pygame.Rect(70, 95, 740, 620)
HOOP_POS = pygame.Vector2(COURT_RECT.centerx, COURT_RECT.top + 42)

COLORS = {
    "bg": (15, 25, 43),
    "bg2": (44, 28, 68),
    "panel": (248, 244, 233),
    "panel2": (237, 231, 216),
    "title": (21, 50, 72),
    "text": (34, 42, 56),
    "muted": (107, 115, 128),
    "good": (32, 138, 78),
    "warn": (217, 112, 46),
    "bad": (200, 65, 65),
    "accent2": (46, 125, 191),
    "white": (255, 255, 255),
    "court": (228, 186, 120),
    "court_dark": (206, 162, 96),
    "line": (250, 239, 211),
    "hoop": (226, 96, 57),
    "player": (52, 120, 200),
    "enemy": (205, 67, 67),
    "ball": (217, 121, 59),
}

TEAM_POOL = [
    "Lakers", "Celtics", "Warriors", "Bulls", "Heat", "Knicks", "Nuggets", "Suns", "Bucks", "Mavericks"
]


def clamp(value, low, high):
    return max(low, min(high, value))


class Button:
    def __init__(self, rect, text, color, hover_color, action):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.action = action

    def draw(self, screen, font, mouse_pos):
        fill = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(screen, (32, 32, 32), self.rect.move(0, 3), border_radius=12)
        pygame.draw.rect(screen, fill, self.rect, border_radius=12)
        pygame.draw.rect(screen, (40, 44, 52), self.rect, 2, border_radius=12)
        text = font.render(self.text, True, COLORS["white"])
        screen.blit(text, text.get_rect(center=self.rect.center))

    def handle(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos):
            self.action()


class NBARunAndGun:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("NBA Run And Gun 2D")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        self.font_title = pygame.font.SysFont("Avenir Next", 42, bold=True)
        self.font_h = pygame.font.SysFont("Avenir", 22, bold=True)
        self.font_body = pygame.font.SysFont("Avenir", 16)
        self.font_small = pygame.font.SysFont("Avenir", 13)
        self.font_menu = pygame.font.SysFont("Avenir", 27, bold=True)

        self.state = "menu"
        self.running = True
        self.status = "Welcome to street-court simulation"
        self.difficulty = "Normal"
        self.difficulty_cfg = {
            "Rookie": {"defenders": 2, "def_speed": 130, "steal": 0.30, "target": 24},
            "Normal": {"defenders": 3, "def_speed": 155, "steal": 0.38, "target": 30},
            "Legend": {"defenders": 4, "def_speed": 178, "steal": 0.46, "target": 36},
        }

        self.btn_start = Button((850, 250, 220, 56), "Start Match", COLORS["good"], (43, 154, 92), self.start_match)
        self.btn_diff = Button((850, 320, 220, 56), "Difficulty", COLORS["accent2"], (35, 141, 214), self.cycle_difficulty)
        self.btn_quit = Button((850, 390, 220, 56), "Quit", COLORS["bad"], (216, 84, 84), self.quit_game)
        self.btn_restart = Button((845, 612, 220, 44), "Play Again", COLORS["accent2"], (35, 141, 214), self.start_match)
        self.btn_menu = Button((845, 662, 220, 44), "Back To Menu", COLORS["warn"], (225, 125, 52), self.to_menu)

        self.team_home = random.choice(TEAM_POOL)
        self.team_away = random.choice([t for t in TEAM_POOL if t != self.team_home])

        self.player_pos = pygame.Vector2(COURT_RECT.centerx, COURT_RECT.bottom - 110)
        self.player_vel = pygame.Vector2(0, 0)
        self.player_speed = 220
        self.energy = 100.0
        self.max_energy = 100.0
        self.dash_cd = 0.0
        self.combo = 0
        self.combo_time = 0.0

        self.ball_pos = self.player_pos.copy()
        self.ball_vel = pygame.Vector2(0, 0)
        self.has_ball = True
        self.shot_active = False
        self.shot_start = pygame.Vector2(0, 0)
        self.shot_t = 0.0
        self.shot_time = 0.52
        self.last_shot_result = ""

        self.defenders = []
        self.turnovers = 0
        self.rebounds = 0
        self.score = 0
        self.time_left = 120.0
        self.target_score = 30
        self.game_over = False
        self.win = False
        self.shot_clock = 24.0

        self.boost_pos = None
        self.boost_timer = 7.0
        self.speed_boost_until = 0.0

    def cycle_difficulty(self):
        order = ["Rookie", "Normal", "Legend"]
        idx = (order.index(self.difficulty) + 1) % len(order)
        self.difficulty = order[idx]
        self.status = f"Difficulty set: {self.difficulty}"

    def to_menu(self):
        self.state = "menu"

    def quit_game(self):
        self.running = False

    def _spawn_defenders(self):
        cfg = self.difficulty_cfg[self.difficulty]
        self.defenders = []
        for i in range(cfg["defenders"]):
            x = random.randint(COURT_RECT.left + 80, COURT_RECT.right - 80)
            y = random.randint(COURT_RECT.top + 90, COURT_RECT.centery + 120)
            self.defenders.append({
                "pos": pygame.Vector2(x, y),
                "dir": pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)),
                "hes": random.uniform(0.2, 0.55),
                "index": i,
            })

    def start_match(self):
        cfg = self.difficulty_cfg[self.difficulty]
        self.state = "play"
        self.status = "Break defenders, build combo, beat target score"
        self.score = 0
        self.turnovers = 0
        self.rebounds = 0
        self.combo = 0
        self.combo_time = 0.0
        self.time_left = 120.0
        self.target_score = cfg["target"]
        self.shot_clock = 24.0
        self.energy = 100.0
        self.dash_cd = 0.0
        self.player_pos = pygame.Vector2(COURT_RECT.centerx, COURT_RECT.bottom - 110)
        self.player_vel = pygame.Vector2(0, 0)
        self.ball_pos = self.player_pos.copy()
        self.ball_vel = pygame.Vector2(0, 0)
        self.has_ball = True
        self.shot_active = False
        self.shot_t = 0.0
        self.game_over = False
        self.win = False
        self.boost_timer = 6.5
        self.boost_pos = None
        self.speed_boost_until = 0.0
        self.team_home = random.choice(TEAM_POOL)
        self.team_away = random.choice([t for t in TEAM_POOL if t != self.team_home])
        self._spawn_defenders()

    def _dash(self):
        if self.energy < 30 or self.dash_cd > 0:
            return
        keys = pygame.key.get_pressed()
        direction = pygame.Vector2(0, 0)
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            direction.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            direction.y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            direction.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            direction.x += 1

        if direction.length_squared() == 0:
            direction = pygame.Vector2(0, -1)
        direction = direction.normalize()
        self.player_pos += direction * 62
        self.player_pos.x = clamp(self.player_pos.x, COURT_RECT.left + 18, COURT_RECT.right - 18)
        self.player_pos.y = clamp(self.player_pos.y, COURT_RECT.top + 18, COURT_RECT.bottom - 18)
        self.energy -= 30
        self.dash_cd = 1.2
        self.status = "Crossover burst"

    def _shot_success_chance(self):
        dist = self.player_pos.distance_to(HOOP_POS)
        if dist < 130:
            base = 0.78
        elif dist < 240:
            base = 0.58
        else:
            base = 0.42

        pressure = 0.0
        for d in self.defenders:
            gap = d["pos"].distance_to(self.player_pos)
            if gap < 92:
                pressure += 0.12

        diff_adj = {"Rookie": 0.06, "Normal": 0.0, "Legend": -0.08}[self.difficulty]
        combo_adj = min(0.12, self.combo * 0.02)
        chance = base - pressure + diff_adj + combo_adj
        return clamp(chance, 0.12, 0.94)

    def take_shot(self):
        if not self.has_ball or self.shot_active or self.game_over:
            return
        self.shot_active = True
        self.has_ball = False
        self.shot_t = 0.0
        self.shot_start = self.player_pos.copy()
        self.last_shot_result = ""
        self.status = "Shot released"

    def _resolve_shot(self):
        chance = self._shot_success_chance()
        dist = self.shot_start.distance_to(HOOP_POS)
        points = 3 if dist >= 240 else 2
        made = random.random() < chance

        if made:
            bonus = 1 if self.combo >= 3 else 0
            self.score += points + bonus
            self.combo += 1
            self.combo_time = 5.5
            self.has_ball = True
            self.ball_pos = self.player_pos.copy()
            self.last_shot_result = f"Made {points}PT"
            self.status = f"Bucket: +{points + bonus}"
            self.shot_clock = 24.0
        else:
            self.combo = 0
            self.combo_time = 0.0
            self.last_shot_result = "Miss"
            self.status = "Missed shot, rebound!"
            self.ball_pos = pygame.Vector2(
                HOOP_POS.x + random.randint(-48, 48),
                HOOP_POS.y + random.randint(18, 84),
            )
            self.ball_vel = pygame.Vector2(random.uniform(-80, 80), random.uniform(110, 190))

        self.shot_active = False

    def _try_collect_ball(self):
        if self.has_ball or self.shot_active:
            return
        if self.player_pos.distance_to(self.ball_pos) < 22:
            self.has_ball = True
            self.rebounds += 1
            self.shot_clock = max(14.0, self.shot_clock)
            self.status = "Controlled rebound"

    def _update_player(self, dt):
        keys = pygame.key.get_pressed()
        direction = pygame.Vector2(0, 0)
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            direction.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            direction.y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            direction.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            direction.x += 1

        if direction.length_squared() > 0:
            direction = direction.normalize()

        speed = self.player_speed
        if pygame.time.get_ticks() < self.speed_boost_until:
            speed += 80

        self.player_vel = direction * speed
        self.player_pos += self.player_vel * dt
        self.player_pos.x = clamp(self.player_pos.x, COURT_RECT.left + 18, COURT_RECT.right - 18)
        self.player_pos.y = clamp(self.player_pos.y, COURT_RECT.top + 18, COURT_RECT.bottom - 18)

        if self.has_ball:
            wave = math.sin(pygame.time.get_ticks() * 0.018) * 3
            self.ball_pos = pygame.Vector2(self.player_pos.x + 14, self.player_pos.y + 12 + wave)
        elif not self.shot_active:
            self.ball_pos += self.ball_vel * dt
            self.ball_vel *= 0.985
            self.ball_pos.x = clamp(self.ball_pos.x, COURT_RECT.left + 10, COURT_RECT.right - 10)
            self.ball_pos.y = clamp(self.ball_pos.y, COURT_RECT.top + 10, COURT_RECT.bottom - 10)

    def _update_defenders(self, dt):
        cfg = self.difficulty_cfg[self.difficulty]
        speed = cfg["def_speed"]

        target = self.player_pos if self.has_ball else self.ball_pos
        for d in self.defenders:
            vec = target - d["pos"]
            if vec.length_squared() > 1:
                vec = vec.normalize()
            wander = pygame.Vector2(math.sin(pygame.time.get_ticks() * 0.001 + d["index"]), math.cos(pygame.time.get_ticks() * 0.0016 + d["index"] * 2))
            move_dir = (vec * (1.0 - d["hes"]) + wander * d["hes"] * 0.3)
            if move_dir.length_squared() > 0:
                move_dir = move_dir.normalize()
            d["pos"] += move_dir * speed * dt
            d["pos"].x = clamp(d["pos"].x, COURT_RECT.left + 16, COURT_RECT.right - 16)
            d["pos"].y = clamp(d["pos"].y, COURT_RECT.top + 16, COURT_RECT.bottom - 16)

            if self.has_ball and not self.shot_active and d["pos"].distance_to(self.player_pos) < 25:
                if random.random() < cfg["steal"] * dt * 10:
                    self.has_ball = False
                    self.turnovers += 1
                    self.combo = 0
                    self.combo_time = 0.0
                    self.ball_pos = self.player_pos + pygame.Vector2(random.randint(-30, 30), random.randint(-20, 24))
                    self.ball_vel = pygame.Vector2(random.uniform(-90, 90), random.uniform(40, 120))
                    self.status = "Stolen by defense"

    def _update_boosts(self, dt):
        self.boost_timer -= dt
        if self.boost_timer <= 0 and self.boost_pos is None:
            x = random.randint(COURT_RECT.left + 90, COURT_RECT.right - 90)
            y = random.randint(COURT_RECT.top + 120, COURT_RECT.bottom - 120)
            self.boost_pos = pygame.Vector2(x, y)
            self.boost_timer = random.uniform(10.0, 14.0)

        if self.boost_pos and self.player_pos.distance_to(self.boost_pos) < 22:
            self.boost_pos = None
            self.energy = clamp(self.energy + 45, 0, self.max_energy)
            self.speed_boost_until = pygame.time.get_ticks() + 3500
            self.status = "Boost collected: speed and energy up"

    def _update_gameplay(self, dt):
        if self.game_over:
            return

        self.time_left -= dt
        self.shot_clock -= dt
        self.combo_time -= dt
        self.dash_cd = max(0.0, self.dash_cd - dt)
        self.energy = clamp(self.energy + 16 * dt, 0, self.max_energy)

        if self.combo_time <= 0:
            self.combo = 0

        if self.shot_clock <= 0:
            self.turnovers += 1
            self.combo = 0
            self.shot_clock = 24.0
            self.has_ball = True
            self.ball_pos = self.player_pos.copy()
            self.status = "Shot clock violation"

        self._update_player(dt)
        self._update_defenders(dt)
        self._update_boosts(dt)

        if self.shot_active:
            self.shot_t += dt / self.shot_time
            t = clamp(self.shot_t, 0.0, 1.0)
            p = self.shot_start.lerp(HOOP_POS, t)
            arc = -120 * math.sin(math.pi * t)
            self.ball_pos = pygame.Vector2(p.x, p.y + arc)
            if t >= 1.0:
                self._resolve_shot()
        else:
            self._try_collect_ball()

        if self.score >= self.target_score:
            self.game_over = True
            self.win = True
            self.status = "Victory: target score reached"
        elif self.time_left <= 0:
            self.game_over = True
            self.win = self.score >= self.target_score
            if self.win:
                self.status = "Clutch finish!"
            else:
                self.status = "Time up: mission failed"

    def _draw_gradient(self):
        for y in range(HEIGHT):
            t = y / HEIGHT
            r = int(COLORS["bg"][0] + (COLORS["bg2"][0] - COLORS["bg"][0]) * t)
            g = int(COLORS["bg"][1] + (COLORS["bg2"][1] - COLORS["bg"][1]) * t)
            b = int(COLORS["bg"][2] + (COLORS["bg2"][2] - COLORS["bg"][2]) * t)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (WIDTH, y))

        pygame.draw.circle(self.screen, (244, 152, 74), (80, 96), 110)
        pygame.draw.circle(self.screen, (121, 175, 214), (WIDTH - 90, HEIGHT - 55), 140)

    def _draw_court(self):
        shadow = COURT_RECT.move(0, 8)
        pygame.draw.rect(self.screen, (26, 28, 34), shadow, border_radius=20)
        pygame.draw.rect(self.screen, COLORS["court"], COURT_RECT, border_radius=20)
        pygame.draw.rect(self.screen, COLORS["court_dark"], COURT_RECT.inflate(-26, -26), border_radius=18)
        pygame.draw.rect(self.screen, COLORS["line"], COURT_RECT, 3, border_radius=20)

        lane = pygame.Rect(COURT_RECT.centerx - 96, COURT_RECT.top + 18, 192, 174)
        pygame.draw.rect(self.screen, (191, 145, 84), lane, border_radius=10)
        pygame.draw.rect(self.screen, COLORS["line"], lane, 3, border_radius=10)

        pygame.draw.circle(self.screen, COLORS["line"], (COURT_RECT.centerx, COURT_RECT.centery + 70), 70, 3)

        arc_rect = pygame.Rect(COURT_RECT.centerx - 220, COURT_RECT.top + 10, 440, 250)
        pygame.draw.arc(self.screen, COLORS["line"], arc_rect, math.radians(17), math.radians(163), 3)

        backboard = pygame.Rect(int(HOOP_POS.x - 44), int(HOOP_POS.y - 26), 88, 10)
        pygame.draw.rect(self.screen, COLORS["line"], backboard, border_radius=4)
        pygame.draw.circle(self.screen, COLORS["hoop"], (int(HOOP_POS.x), int(HOOP_POS.y)), 15, 4)

    def _draw_entities(self):
        if self.boost_pos:
            pulse = 10 + int(3 * math.sin(pygame.time.get_ticks() * 0.01))
            pygame.draw.circle(self.screen, (120, 226, 145), self.boost_pos, pulse)
            pygame.draw.circle(self.screen, (32, 138, 78), self.boost_pos, pulse, 3)

        for d in self.defenders:
            pygame.draw.circle(self.screen, COLORS["enemy"], d["pos"], 16)
            pygame.draw.circle(self.screen, (115, 28, 28), d["pos"], 16, 2)

        player_color = (88, 176, 255) if pygame.time.get_ticks() < self.speed_boost_until else COLORS["player"]
        pygame.draw.circle(self.screen, player_color, self.player_pos, 17)
        pygame.draw.circle(self.screen, (22, 62, 121), self.player_pos, 17, 2)

        pygame.draw.circle(self.screen, COLORS["ball"], self.ball_pos, 9)
        pygame.draw.line(self.screen, (142, 82, 44), (self.ball_pos.x - 8, self.ball_pos.y), (self.ball_pos.x + 8, self.ball_pos.y), 2)
        pygame.draw.line(self.screen, (142, 82, 44), (self.ball_pos.x, self.ball_pos.y - 8), (self.ball_pos.x, self.ball_pos.y + 8), 2)

    def _draw_hud(self):
        panel = pygame.Rect(830, 98, 255, 610)
        pygame.draw.rect(self.screen, (33, 33, 40), panel.move(0, 6), border_radius=16)
        pygame.draw.rect(self.screen, COLORS["panel"], panel, border_radius=16)
        pygame.draw.rect(self.screen, (206, 198, 176), panel, 2, border_radius=16)

        y = 122
        title = self.font_h.render("Game Hub", True, COLORS["title"])
        self.screen.blit(title, (852, y))
        y += 38

        lines = [
            f"{self.team_home} vs {self.team_away}",
            f"Difficulty: {self.difficulty}",
            f"Score: {self.score}/{self.target_score}",
            f"Time Left: {max(0, int(self.time_left))}s",
            f"Shot Clock: {max(0, int(self.shot_clock))}s",
            f"Turnovers: {self.turnovers}",
            f"Rebounds: {self.rebounds}",
            f"Combo: x{1 + self.combo}",
        ]
        for line in lines:
            txt = self.font_body.render(line, True, COLORS["text"])
            self.screen.blit(txt, (852, y))
            y += 28

        energy_bg = pygame.Rect(852, y + 6, 200, 14)
        pygame.draw.rect(self.screen, COLORS["panel2"], energy_bg, border_radius=7)
        fill_w = int((self.energy / self.max_energy) * energy_bg.width)
        fill = pygame.Rect(energy_bg.x, energy_bg.y, fill_w, energy_bg.height)
        pygame.draw.rect(self.screen, COLORS["accent2"], fill, border_radius=7)
        etxt = self.font_small.render("Energy", True, COLORS["muted"])
        self.screen.blit(etxt, (852, y - 12))

        y += 44
        status = self.font_small.render(self.status, True, COLORS["muted"])
        self.screen.blit(status, (852, y))
        y += 38

        result_color = COLORS["good"] if self.last_shot_result.startswith("Made") else COLORS["warn"]
        if self.last_shot_result:
            recent = self.font_body.render(self.last_shot_result, True, result_color)
            self.screen.blit(recent, (852, y))

        y += 44
        controls = [
            "WASD / Arrows: Move",
            "Space: Shoot",
            "E: Burst Dash",
            "Esc: Menu",
        ]
        for c in controls:
            txt = self.font_small.render(c, True, COLORS["text"])
            self.screen.blit(txt, (852, y))
            y += 22

        if self.game_over:
            card = pygame.Rect(COURT_RECT.left + 118, COURT_RECT.centery - 85, 500, 170)
            pygame.draw.rect(self.screen, (28, 30, 37), card.move(0, 6), border_radius=16)
            pygame.draw.rect(self.screen, COLORS["panel"], card, border_radius=16)
            pygame.draw.rect(self.screen, (206, 198, 176), card, 2, border_radius=16)

            line1 = "VICTORY" if self.win else "DEFEAT"
            line_color = COLORS["good"] if self.win else COLORS["bad"]
            t1 = self.font_menu.render(line1, True, line_color)
            self.screen.blit(t1, t1.get_rect(center=(card.centerx, card.y + 44)))

            t2 = self.font_body.render(f"Final Score: {self.score}   Target: {self.target_score}", True, COLORS["text"])
            self.screen.blit(t2, t2.get_rect(center=(card.centerx, card.y + 88)))

            t3 = self.font_small.render("Use buttons on right to play again", True, COLORS["muted"])
            self.screen.blit(t3, t3.get_rect(center=(card.centerx, card.y + 120)))

    def _draw_header(self):
        title = self.font_title.render("NBA Run And Gun 2D", True, COLORS["white"])
        self.screen.blit(title, (72, 22))
        sub = self.font_small.render("Arcade half-court: AI defense, combos, shot timing, dynamic boosts", True, (219, 226, 236))
        self.screen.blit(sub, (74, 68))

    def _draw_menu(self):
        self._draw_gradient()
        self._draw_header()

        card = pygame.Rect(76, 108, 730, 590)
        pygame.draw.rect(self.screen, (27, 29, 37), card.move(0, 7), border_radius=20)
        pygame.draw.rect(self.screen, COLORS["panel"], card, border_radius=20)
        pygame.draw.rect(self.screen, (207, 199, 177), card, 2, border_radius=20)

        heading = self.font_menu.render("Street Court Simulation", True, COLORS["title"])
        self.screen.blit(heading, (108, 145))

        features = [
            "Advanced 2D movement and dribble physics",
            "Adaptive defender AI with steal pressure",
            "Distance-based shot system and combo scoring",
            "Energy dash mechanics with timing strategy",
            "Dynamic boost pickups for tempo control",
        ]
        y = 205
        for feat in features:
            bullet = self.font_body.render(f"- {feat}", True, COLORS["text"])
            self.screen.blit(bullet, (112, y))
            y += 34

        mode = self.font_h.render(f"Selected Difficulty: {self.difficulty}", True, COLORS["accent2"])
        self.screen.blit(mode, (108, 404))

        matchup = self.font_body.render(f"Tonight Matchup: {self.team_home} vs {self.team_away}", True, COLORS["muted"])
        self.screen.blit(matchup, (108, 448))

        hint = self.font_small.render("Goal: hit target score before 2:00 ends", True, COLORS["muted"])
        self.screen.blit(hint, (108, 486))

        mouse = pygame.mouse.get_pos()
        self.btn_start.draw(self.screen, self.font_body, mouse)
        self.btn_diff.draw(self.screen, self.font_body, mouse)
        self.btn_quit.draw(self.screen, self.font_body, mouse)

    def _draw_play(self):
        self._draw_gradient()
        self._draw_header()
        self._draw_court()
        self._draw_entities()
        self._draw_hud()

        mouse = pygame.mouse.get_pos()
        self.btn_restart.draw(self.screen, self.font_small, mouse)
        self.btn_menu.draw(self.screen, self.font_small, mouse)

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if self.state == "menu":
                self.btn_start.handle(event)
                self.btn_diff.handle(event)
                self.btn_quit.handle(event)
            else:
                self.btn_restart.handle(event)
                self.btn_menu.handle(event)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.to_menu()
                if self.state == "play" and event.key == pygame.K_SPACE:
                    self.take_shot()
                if self.state == "play" and event.key == pygame.K_e:
                    self._dash()

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self._handle_events()

            if self.state == "play":
                self._update_gameplay(dt)
                self._draw_play()
            else:
                self._draw_menu()

            pygame.display.flip()

        pygame.quit()


def main():
    NBARunAndGun().run()


if __name__ == "__main__":
    main()