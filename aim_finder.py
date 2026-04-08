import random

import pygame


WIDTH, HEIGHT = 1120, 760
FPS = 60
ARENA = pygame.Rect(70, 110, 740, 610)

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
}


def clamp(value, lo, hi):
    return max(lo, min(hi, value))


class Button:
    def __init__(self, rect, text, color, hover_color, action):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.action = action

    def draw(self, surface, font, mouse_pos):
        fill = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(surface, (30, 30, 30), self.rect.move(0, 3), border_radius=12)
        pygame.draw.rect(surface, fill, self.rect, border_radius=12)
        pygame.draw.rect(surface, (40, 44, 52), self.rect, 2, border_radius=12)
        text = font.render(self.text, True, COLORS["white"])
        surface.blit(text, text.get_rect(center=self.rect.center))

    def handle(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos):
            self.action()


class Target:
    def __init__(self, pos, radius, life, velocity, bonus=False):
        self.pos = pygame.Vector2(pos)
        self.radius = radius
        self.life = life
        self.max_life = life
        self.velocity = pygame.Vector2(velocity)
        self.bonus = bonus

    def update(self, dt):
        self.life -= dt
        self.pos += self.velocity * dt
        if self.pos.x - self.radius < ARENA.left or self.pos.x + self.radius > ARENA.right:
            self.velocity.x *= -1
        if self.pos.y - self.radius < ARENA.top or self.pos.y + self.radius > ARENA.bottom:
            self.velocity.y *= -1
        self.pos.x = clamp(self.pos.x, ARENA.left + self.radius, ARENA.right - self.radius)
        self.pos.y = clamp(self.pos.y, ARENA.top + self.radius, ARENA.bottom - self.radius)

    def draw(self, surface):
        life_scale = max(0.2, self.life / self.max_life)
        pulse = 2 + int(2 * abs((pygame.time.get_ticks() // 60) % 8 - 4) / 4)
        outer = (241, 176, 79) if self.bonus else (200, 65, 65)
        inner = (252, 239, 211) if self.bonus else (255, 255, 255)
        pygame.draw.circle(surface, outer, self.pos, int(self.radius + pulse * life_scale))
        pygame.draw.circle(surface, inner, self.pos, int(self.radius * 0.72))
        pygame.draw.circle(surface, outer, self.pos, int(self.radius * 0.45))

    def hit(self, point):
        return self.pos.distance_to(pygame.Vector2(point)) <= self.radius


class AimFinderArena:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Aim Finder Arena")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        self.font_title = pygame.font.SysFont("Avenir Next", 38, bold=True)
        self.font_h = pygame.font.SysFont("Avenir", 20, bold=True)
        self.font_body = pygame.font.SysFont("Avenir", 16)
        self.font_small = pygame.font.SysFont("Avenir", 12)
        self.font_menu = pygame.font.SysFont("Avenir", 27, bold=True)

        self.state = "menu"
        self.running = True
        self.difficulty = "Normal"
        self.diff_cfg = {
            "Easy": {"spawn": 1.0, "lives": 6, "speed": 70, "life": 2.6},
            "Normal": {"spawn": 0.75, "lives": 5, "speed": 110, "life": 2.2},
            "Hard": {"spawn": 0.58, "lives": 4, "speed": 155, "life": 1.9},
        }

        self.btn_play = Button((840, 250, 220, 56), "Start Session", COLORS["good"], (43, 154, 92), self.start_session)
        self.btn_diff = Button((840, 320, 220, 56), "Difficulty", COLORS["accent2"], (35, 141, 214), self.cycle_difficulty)
        self.btn_quit = Button((840, 390, 220, 56), "Quit", COLORS["bad"], (216, 84, 84), self.quit_game)
        self.btn_restart = Button((828, 620, 220, 42), "Restart", COLORS["accent2"], (35, 141, 214), self.start_session)
        self.btn_menu = Button((828, 668, 220, 42), "Back To Menu", COLORS["warn"], (225, 125, 52), self.to_menu)

        self.targets = []
        self.spawn_timer = 0.0
        self.elapsed = 0.0
        self.hits = 0
        self.shots = 0
        self.misses = 0
        self.combo = 0
        self.best_combo = 0
        self.score = 0
        self.lives = 5
        self.focus_until = 0
        self.result_text = ""

    def cycle_difficulty(self):
        order = ["Easy", "Normal", "Hard"]
        idx = (order.index(self.difficulty) + 1) % len(order)
        self.difficulty = order[idx]

    def quit_game(self):
        self.running = False

    def to_menu(self):
        self.state = "menu"

    def start_session(self):
        cfg = self.diff_cfg[self.difficulty]
        self.state = "play"
        self.targets = []
        self.spawn_timer = 0.0
        self.elapsed = 0.0
        self.hits = 0
        self.shots = 0
        self.misses = 0
        self.combo = 0
        self.best_combo = 0
        self.score = 0
        self.lives = cfg["lives"]
        self.focus_until = 0
        self.result_text = ""

    def _spawn_target(self):
        cfg = self.diff_cfg[self.difficulty]
        radius = random.randint(18, 34)
        x = random.randint(ARENA.left + radius, ARENA.right - radius)
        y = random.randint(ARENA.top + radius, ARENA.bottom - radius)
        vx = random.choice([-1, 1]) * random.uniform(cfg["speed"] * 0.45, cfg["speed"] * 1.1)
        vy = random.choice([-1, 1]) * random.uniform(cfg["speed"] * 0.45, cfg["speed"] * 1.1)
        bonus = random.random() < 0.12
        life = cfg["life"] * (1.35 if bonus else 1.0)
        self.targets.append(Target((x, y), radius, life, (vx, vy), bonus=bonus))

    def _shoot(self, pos):
        if self.state != "play":
            return
        self.shots += 1
        hit = False
        for target in self.targets[:]:
            if target.hit(pos):
                self.targets.remove(target)
                hit = True
                self.hits += 1
                self.combo += 1
                self.best_combo = max(self.best_combo, self.combo)
                add = 12 + int(target.radius * 0.6) + (8 if target.bonus else 0)
                if self.combo >= 3:
                    add += self.combo * 2
                self.score += add
                if target.bonus:
                    self.focus_until = pygame.time.get_ticks() + 3500
                break

        if not hit:
            self.combo = 0
            self.score = max(0, self.score - 4)

    def _update_play(self, dt):
        cfg = self.diff_cfg[self.difficulty]
        time_scale = 0.58 if pygame.time.get_ticks() < self.focus_until else 1.0
        self.elapsed += dt
        self.spawn_timer += dt

        spawn_gap = cfg["spawn"] * time_scale
        while self.spawn_timer >= spawn_gap:
            self.spawn_timer -= spawn_gap
            self._spawn_target()

        for target in self.targets[:]:
            target.update(dt * time_scale)
            if target.life <= 0:
                self.targets.remove(target)
                self.combo = 0
                self.misses += 1
                self.lives -= 1

        if self.lives <= 0:
            self.state = "end"
            accuracy = (self.hits / self.shots * 100) if self.shots else 0.0
            speed = self.hits / self.elapsed if self.elapsed > 0 else 0.0
            self.result_text = f"Accuracy {accuracy:.1f}% | Speed {speed:.2f}/s"

    def _draw_gradient(self):
        for y in range(HEIGHT):
            t = y / HEIGHT
            r = int(COLORS["bg"][0] + (COLORS["bg2"][0] - COLORS["bg"][0]) * t)
            g = int(COLORS["bg"][1] + (COLORS["bg2"][1] - COLORS["bg"][1]) * t)
            b = int(COLORS["bg"][2] + (COLORS["bg2"][2] - COLORS["bg"][2]) * t)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (WIDTH, y))
        pygame.draw.circle(self.screen, (244, 152, 74), (78, 90), 110)
        pygame.draw.circle(self.screen, (121, 175, 214), (WIDTH - 95, HEIGHT - 45), 138)

    def _draw_header(self):
        title = self.font_title.render("Aim Finder Arena", True, COLORS["white"])
        self.screen.blit(title, (72, 22))
        sub = self.font_small.render("Precision speed trainer with moving targets, combo chain and focus boosts", True, (219, 226, 236))
        self.screen.blit(sub, (74, 68))

    def _draw_arena(self):
        pygame.draw.rect(self.screen, (28, 30, 37), ARENA.move(0, 6), border_radius=18)
        pygame.draw.rect(self.screen, (43, 66, 94), ARENA, border_radius=18)
        pygame.draw.rect(self.screen, (70, 93, 122), ARENA.inflate(-26, -26), border_radius=16)
        pygame.draw.rect(self.screen, (214, 224, 236), ARENA, 2, border_radius=18)

        for target in self.targets:
            target.draw(self.screen)

        mx, my = pygame.mouse.get_pos()
        if ARENA.collidepoint((mx, my)):
            pygame.draw.circle(self.screen, (250, 250, 250), (mx, my), 18, 1)
            pygame.draw.line(self.screen, (250, 250, 250), (mx - 8, my), (mx + 8, my), 2)
            pygame.draw.line(self.screen, (250, 250, 250), (mx, my - 8), (mx, my + 8), 2)

    def _draw_sidebar(self):
        panel = pygame.Rect(828, 112, 255, 600)
        pygame.draw.rect(self.screen, (33, 33, 40), panel.move(0, 6), border_radius=16)
        pygame.draw.rect(self.screen, COLORS["panel"], panel, border_radius=16)
        pygame.draw.rect(self.screen, (206, 198, 176), panel, 2, border_radius=16)

        y = 134
        self.screen.blit(self.font_h.render("Session Hub", True, COLORS["title"]), (850, y))
        y += 36

        accuracy = (self.hits / self.shots * 100) if self.shots else 0.0
        speed = self.hits / self.elapsed if self.elapsed > 0 else 0.0
        lines = [
            f"Difficulty: {self.difficulty}",
            f"Score: {self.score}",
            f"Lives: {self.lives}",
            f"Hits: {self.hits}",
            f"Shots: {self.shots}",
            f"Misses: {self.misses}",
            f"Combo: x{max(1, self.combo)}",
            f"Best Combo: x{max(1, self.best_combo)}",
            f"Accuracy: {accuracy:.1f}%",
            f"Speed: {speed:.2f}/s",
            f"Time: {int(self.elapsed)}s",
        ]
        for line in lines:
            self.screen.blit(self.font_body.render(line, True, COLORS["text"]), (850, y))
            y += 25

        if pygame.time.get_ticks() < self.focus_until:
            self.screen.blit(self.font_small.render("Focus Boost Active", True, COLORS["good"]), (850, y + 8))
            y += 26

        y += 12
        controls = ["LMB: Shoot", "Bonus target: slow time", "ESC: Menu"]
        for line in controls:
            self.screen.blit(self.font_small.render(line, True, COLORS["muted"]), (850, y))
            y += 21

        mouse = pygame.mouse.get_pos()
        self.btn_restart.draw(self.screen, self.font_small, mouse)
        self.btn_menu.draw(self.screen, self.font_small, mouse)

    def _draw_menu(self):
        self._draw_gradient()
        self._draw_header()

        card = pygame.Rect(76, 112, 730, 588)
        pygame.draw.rect(self.screen, (27, 29, 37), card.move(0, 7), border_radius=20)
        pygame.draw.rect(self.screen, COLORS["panel"], card, border_radius=20)
        pygame.draw.rect(self.screen, (207, 199, 177), card, 2, border_radius=20)

        self.screen.blit(self.font_menu.render("Precision Aim Simulation", True, COLORS["title"]), (108, 148))

        features = [
            "Dynamic moving targets with finite lifespan",
            "Combo chain scoring and hit-speed analytics",
            "Difficulty tuning for spawn, velocity and survival",
            "Bonus focus targets that trigger slow-time window",
            "Live sidebar telemetry with instant performance feedback",
        ]
        y = 208
        for line in features:
            self.screen.blit(self.font_body.render(f"- {line}", True, COLORS["text"]), (112, y))
            y += 33

        self.screen.blit(self.font_h.render(f"Selected Difficulty: {self.difficulty}", True, COLORS["accent2"]), (108, 408))
        self.screen.blit(self.font_small.render("Start a session and clear as many targets as possible before lives run out.", True, COLORS["muted"]), (108, 445))

        mouse = pygame.mouse.get_pos()
        self.btn_play.draw(self.screen, self.font_body, mouse)
        self.btn_diff.draw(self.screen, self.font_body, mouse)
        self.btn_quit.draw(self.screen, self.font_body, mouse)

    def _draw_end(self):
        self._draw_gradient()
        self._draw_header()
        self._draw_arena()
        self._draw_sidebar()

        box = pygame.Rect(188, 260, 505, 190)
        pygame.draw.rect(self.screen, (28, 30, 37), box.move(0, 6), border_radius=16)
        pygame.draw.rect(self.screen, COLORS["panel"], box, border_radius=16)
        pygame.draw.rect(self.screen, (206, 198, 176), box, 2, border_radius=16)

        self.screen.blit(self.font_menu.render("SESSION COMPLETE", True, COLORS["title"]), (240, 296))
        self.screen.blit(self.font_body.render(f"Final Score: {self.score}", True, COLORS["text"]), (240, 345))
        self.screen.blit(self.font_body.render(self.result_text, True, COLORS["muted"]), (240, 374))

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.to_menu()

            if self.state == "menu":
                self.btn_play.handle(event)
                self.btn_diff.handle(event)
                self.btn_quit.handle(event)
            else:
                self.btn_restart.handle(event)
                self.btn_menu.handle(event)

            if self.state == "play" and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._shoot(event.pos)

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self._handle_events()

            if self.state == "play":
                self._update_play(dt)
                self._draw_gradient()
                self._draw_header()
                self._draw_arena()
                self._draw_sidebar()
            elif self.state == "end":
                self._draw_end()
            else:
                self._draw_menu()

            pygame.display.flip()

        pygame.quit()


def main():
    AimFinderArena().run()


if __name__ == "__main__":
    main()