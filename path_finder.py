import random
from collections import deque

import pygame


WIDTH, HEIGHT = 1120, 760
FPS = 60
CELL = 32
GRID_COLS, GRID_ROWS = 21, 17
GRID_X, GRID_Y = 70, 110

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
    "wall": (41, 62, 90),
    "path": (173, 214, 255),
    "goal": (240, 177, 69),
    "white": (255, 255, 255),
}


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


class Button:
    def __init__(self, rect, text, color, hover_color, on_click):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.on_click = on_click

    def draw(self, surf, font, mouse_pos):
        fill = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(surf, (30, 30, 30), self.rect.move(0, 3), border_radius=12)
        pygame.draw.rect(surf, fill, self.rect, border_radius=12)
        pygame.draw.rect(surf, (40, 44, 52), self.rect, 2, border_radius=12)
        txt = font.render(self.text, True, COLORS["white"])
        surf.blit(txt, txt.get_rect(center=self.rect.center))

    def handle(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos):
            self.on_click()


class PathFinderArena:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Path Finder Arena")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        self.font_title = pygame.font.SysFont("Avenir Next", 38, bold=True)
        self.font_h = pygame.font.SysFont("Avenir", 20, bold=True)
        self.font_body = pygame.font.SysFont("Avenir", 16)
        self.font_small = pygame.font.SysFont("Avenir", 12)
        self.font_menu = pygame.font.SysFont("Avenir", 26, bold=True)

        self.state = "menu"
        self.difficulty = "Normal"
        self.difficulty_settings = {
            "Easy": {"cores": 3, "enemies": 2, "enemy_tick": 460, "chase_radius": 4},
            "Normal": {"cores": 4, "enemies": 3, "enemy_tick": 340, "chase_radius": 5},
            "Hard": {"cores": 5, "enemies": 4, "enemy_tick": 260, "chase_radius": 6},
        }

        self.menu_play = Button((835, 246, 220, 56), "Start Mission", COLORS["good"], (43, 154, 92), self.start_game)
        self.menu_diff = Button((835, 316, 220, 56), "Difficulty", COLORS["accent2"], (35, 141, 214), self.cycle_difficulty)
        self.menu_quit = Button((835, 386, 220, 56), "Quit", COLORS["bad"], (216, 84, 84), self.quit_game)

        self.btn_restart = Button((820, 616, 220, 44), "New Maze", COLORS["accent2"], (35, 141, 214), self.start_game)
        self.btn_menu = Button((820, 668, 220, 44), "Back To Menu", COLORS["warn"], (225, 125, 52), self.to_menu)

        self.running = True
        self.show_hint = False
        self.status = "Ready"
        self.start_ticks = pygame.time.get_ticks()

        self.grid = []
        self.player = (1, 1)
        self.spawn = (1, 1)
        self.goal = (GRID_COLS - 2, GRID_ROWS - 2)
        self.exits = []
        self.primary_exit = (0, 1)
        self.cores = set()
        self.core_quota = 0
        self.beacon = None
        self.beacon_activated = False
        self.enemies = []
        self.enemy_timer = 0
        self.hp = 3
        self.score = 0
        self.collected = 0
        self.win = False
        self.last_hit_tick = -9999
        self.invuln_ms = 1400
        self.emp_active_until = 0
        self.emp_cooldown_ms = 9000
        self.last_emp_tick = -9000
        self.dash_charges = 2
        self.max_dash = 2
        self.last_dash_regen = pygame.time.get_ticks()
        self.contact_lock = 0

    def cycle_difficulty(self):
        order = ["Easy", "Normal", "Hard"]
        idx = (order.index(self.difficulty) + 1) % len(order)
        self.difficulty = order[idx]

    def to_menu(self):
        self.state = "menu"

    def quit_game(self):
        self.running = False

    def start_game(self):
        self.state = "play"
        self.status = "Collect all energy cores, then reach the gate"
        self.start_ticks = pygame.time.get_ticks()
        self.hp = 3
        self.score = 0
        self.collected = 0
        self.win = False
        self.show_hint = False
        self.enemy_timer = 0
        self.last_hit_tick = -9999
        self.emp_active_until = 0
        self.last_emp_tick = -9000
        self.dash_charges = 2
        self.last_dash_regen = pygame.time.get_ticks()
        self.beacon_activated = False
        self.contact_lock = 0
        self._generate_maze()

    def _generate_maze(self):
        self.grid = [[1 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]

        def carve(cx, cy):
            self.grid[cy][cx] = 0
            dirs = [(2, 0), (-2, 0), (0, 2), (0, -2)]
            random.shuffle(dirs)
            for dx, dy in dirs:
                nx, ny = cx + dx, cy + dy
                if 1 <= nx < GRID_COLS - 1 and 1 <= ny < GRID_ROWS - 1 and self.grid[ny][nx] == 1:
                    self.grid[cy + dy // 2][cx + dx // 2] = 0
                    carve(nx, ny)

        carve(1, 1)

        self.spawn = (1, 1)
        self.player = self.spawn
        self.goal = (GRID_COLS - 2, GRID_ROWS - 2)
        self.grid[self.goal[1]][self.goal[0]] = 0

        # Create multiple map exits on borders.
        self.exits = [
            (0, 1),
            (GRID_COLS - 1, GRID_ROWS - 2),
            (GRID_COLS - 1, 1),
        ]
        self.primary_exit = self.exits[0]

        # Ensure inside tiles next to exits are open.
        self.grid[1][1] = 0
        self.grid[GRID_ROWS - 2][GRID_COLS - 2] = 0
        self.grid[1][GRID_COLS - 2] = 0
        for ex, ey in self.exits:
            self.grid[ey][ex] = 0

        floors = [(x, y) for y in range(1, GRID_ROWS - 1) for x in range(1, GRID_COLS - 1) if self.grid[y][x] == 0]
        random.shuffle(floors)

        cfg = self.difficulty_settings[self.difficulty]
        core_count = cfg["cores"]
        enemy_count = cfg["enemies"]
        self.cores = set()

        for pos in floors:
            if pos != self.spawn and pos != self.goal:
                self.cores.add(pos)
            if len(self.cores) == core_count:
                break

        self.core_quota = max(2, (len(self.cores) * 3 + 4) // 5)

        beacon_choices = [p for p in floors if p != self.spawn and p not in self.cores and p not in self.exits]
        self.beacon = random.choice(beacon_choices) if beacon_choices else self.spawn

        self.enemies = []
        for pos in floors:
            if pos != self.spawn and pos != self.goal and pos not in self.cores and pos not in self.exits and self._dist(pos, self.spawn) > 7:
                self.enemies.append(pos)
            if len(self.enemies) == enemy_count:
                break

    def _check_win_conditions(self):
        if self.player not in self.exits:
            return

        # Path 1: collect all cores, exit anywhere.
        if not self.cores:
            self.win = True
            self.score += 350
            self.status = "Mission complete: Full Sweep Exit"
            return

        # Path 2: quota run, use primary extraction gate.
        if self.player == self.primary_exit and self.collected >= self.core_quota:
            self.win = True
            self.score += 280
            self.status = "Mission complete: Quota Extraction"
            return

        # Path 3: activate beacon then exit anywhere.
        if self.beacon_activated:
            self.win = True
            self.score += 300
            self.status = "Mission complete: Beacon Route"
            return

    def _dist(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def _neighbors(self, node):
        x, y = node
        out = []
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_COLS and 0 <= ny < GRID_ROWS and self.grid[ny][nx] == 0:
                out.append((nx, ny))
        return out

    def _bfs_path(self, start, target):
        q = deque([start])
        prev = {start: None}
        while q:
            cur = q.popleft()
            if cur == target:
                break
            for nb in self._neighbors(cur):
                if nb not in prev:
                    prev[nb] = cur
                    q.append(nb)

        if target not in prev:
            return []

        path = []
        cur = target
        while cur is not None:
            path.append(cur)
            cur = prev[cur]
        path.reverse()
        return path

    def _hint_path(self):
        if self.beacon and self.collected >= 1 and not self.beacon_activated:
            target = self.beacon
        elif self.cores:
            target = min(self.cores, key=lambda c: self._dist(self.player, c))
        else:
            target = self.primary_exit
        return self._bfs_path(self.player, target)

    def _move_player(self, dx, dy):
        if self.state != "play" or self.win:
            return
        nx, ny = self.player[0] + dx, self.player[1] + dy
        if 0 <= nx < GRID_COLS and 0 <= ny < GRID_ROWS and self.grid[ny][nx] == 0:
            self.player = (nx, ny)

            if self.player in self.cores:
                self.cores.remove(self.player)
                self.collected += 1
                self.score += 100
                self.status = f"Core secured: {self.collected}"

            if self.beacon and self.player == self.beacon and self.collected >= 1 and not self.beacon_activated:
                self.beacon_activated = True
                self.score += 80
                self.status = "Beacon activated. Reach any exit"

            self._check_win_conditions()

    def _dash(self):
        if self.state != "play" or self.win:
            return
        if self.dash_charges <= 0:
            self.status = "Dash recharging"
            return

        keys = pygame.key.get_pressed()
        direction = None
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            direction = (0, -1)
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            direction = (0, 1)
        elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
            direction = (-1, 0)
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            direction = (1, 0)

        if direction is None:
            self.status = "Hold a move direction, then press SPACE to dash"
            return

        dx, dy = direction
        moved = False
        for step in (1, 2):
            nx, ny = self.player[0] + dx * step, self.player[1] + dy * step
            if 0 <= nx < GRID_COLS and 0 <= ny < GRID_ROWS and self.grid[ny][nx] == 0:
                self.player = (nx, ny)
                moved = True
            else:
                break

        if moved:
            self.dash_charges -= 1
            self.status = "Dash used"

    def _emp(self):
        if self.state != "play" or self.win:
            return
        now = pygame.time.get_ticks()
        if now - self.last_emp_tick < self.emp_cooldown_ms:
            left = (self.emp_cooldown_ms - (now - self.last_emp_tick)) // 1000 + 1
            self.status = f"EMP cooling down: {left}s"
            return
        self.last_emp_tick = now
        self.emp_active_until = now + 2800
        self.status = "EMP pulse activated"

    def _update_enemies(self, dt_ms):
        if self.state != "play" or self.win:
            return

        now = pygame.time.get_ticks()
        if self.dash_charges < self.max_dash and now - self.last_dash_regen > 4200:
            self.dash_charges += 1
            self.last_dash_regen = now

        self.enemy_timer += dt_ms
        tick = self.difficulty_settings[self.difficulty]["enemy_tick"]
        if self.enemy_timer < tick:
            return
        self.enemy_timer = 0

        if now < self.emp_active_until:
            return

        moved = []
        chase_radius = self.difficulty_settings[self.difficulty]["chase_radius"]
        spawn_safe_radius = 2
        for enemy in self.enemies:
            if self._dist(enemy, self.player) <= chase_radius:
                path = self._bfs_path(enemy, self.player)
                if len(path) >= 2:
                    next_pos = path[1]
                    # Give the player reaction space when drone is adjacent.
                    if self._dist(enemy, self.player) == 1 and random.random() < 0.60:
                        moved.append(enemy)
                    elif self._dist(next_pos, self.spawn) <= spawn_safe_radius:
                        moved.append(enemy)
                    else:
                        moved.append(next_pos)
                else:
                    moved.append(enemy)
            else:
                options = self._neighbors(enemy)
                if options:
                    random.shuffle(options)
                    picked = enemy
                    for opt in options:
                        if self._dist(opt, self.spawn) > spawn_safe_radius:
                            picked = opt
                            break
                    moved.append(picked)
                else:
                    moved.append(enemy)
        self.enemies = moved

        if self.player in self.enemies:
            self.contact_lock += 1
        else:
            self.contact_lock = 0

        # Require sustained contact so a single overlap is dodgeable.
        if self.contact_lock >= 2 and now - self.last_hit_tick > self.invuln_ms:
            self.hp -= 1
            self.last_hit_tick = now
            self.contact_lock = 0
            self.status = "Hit by drone"
            self.player = self.spawn
            if self.hp <= 0:
                self.status = "Mission failed"
                self.state = "fail"

    def _draw_bg(self):
        for y in range(HEIGHT):
            t = y / HEIGHT
            r = int(COLORS["bg"][0] + (COLORS["bg2"][0] - COLORS["bg"][0]) * t)
            g = int(COLORS["bg"][1] + (COLORS["bg2"][1] - COLORS["bg"][1]) * t)
            b = int(COLORS["bg"][2] + (COLORS["bg2"][2] - COLORS["bg"][2]) * t)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (WIDTH, y))
        pygame.draw.circle(self.screen, (255, 183, 3), (60, 60), 130)
        pygame.draw.circle(self.screen, (142, 202, 230), (1040, 640), 180)

    def _draw_panel(self):
        panel = pygame.Rect(45, 35, 1030, 690)
        pygame.draw.rect(self.screen, (24, 24, 24), panel.move(0, 6), border_radius=18)
        pygame.draw.rect(self.screen, COLORS["panel"], panel, border_radius=18)
        pygame.draw.rect(self.screen, (205, 190, 160), panel, 2, border_radius=18)

        self.screen.blit(self.font_title.render("Path Finder Arena", True, COLORS["title"]), (80, 58))
        self.screen.blit(self.font_small.render("Real 2D tactical maze mission", True, COLORS["muted"]), (84, 102))

    def _draw_grid(self):
        box = pygame.Rect(GRID_X - 12, GRID_Y - 12, GRID_COLS * CELL + 24, GRID_ROWS * CELL + 24)
        pygame.draw.rect(self.screen, (34, 34, 34), box.move(0, 4), border_radius=14)
        pygame.draw.rect(self.screen, COLORS["panel2"], box, border_radius=14)
        pygame.draw.rect(self.screen, (194, 184, 166), box, 2, border_radius=14)

        for y in range(GRID_ROWS):
            for x in range(GRID_COLS):
                rect = pygame.Rect(GRID_X + x * CELL, GRID_Y + y * CELL, CELL, CELL)
                if self.grid[y][x] == 1:
                    pygame.draw.rect(self.screen, COLORS["wall"], rect)
                else:
                    pygame.draw.rect(self.screen, (224, 232, 244), rect)
                pygame.draw.rect(self.screen, (185, 194, 208), rect, 1)

        if self.show_hint and self.state == "play":
            for tile in self._hint_path()[1:-1]:
                hrect = pygame.Rect(GRID_X + tile[0] * CELL + 9, GRID_Y + tile[1] * CELL + 9, CELL - 18, CELL - 18)
                pygame.draw.rect(self.screen, COLORS["path"], hrect, border_radius=6)

        for ex, ey in self.exits:
            erect = pygame.Rect(GRID_X + ex * CELL + 5, GRID_Y + ey * CELL + 5, CELL - 10, CELL - 10)
            if (ex, ey) == self.primary_exit:
                col = (92, 179, 255)
            else:
                col = COLORS["goal"]
            pygame.draw.rect(self.screen, col, erect, border_radius=6)

        if self.beacon:
            bx, by = self.beacon
            brect = pygame.Rect(GRID_X + bx * CELL + 8, GRID_Y + by * CELL + 8, CELL - 16, CELL - 16)
            bcol = COLORS["good"] if self.beacon_activated else (120, 120, 120)
            pygame.draw.rect(self.screen, bcol, brect, border_radius=5)

        for cx, cy in self.cores:
            center = (GRID_X + cx * CELL + CELL // 2, GRID_Y + cy * CELL + CELL // 2)
            pygame.draw.circle(self.screen, (255, 206, 92), center, 8)
            pygame.draw.circle(self.screen, (193, 130, 23), center, 8, 2)

        for ex, ey in self.enemies:
            erect = pygame.Rect(GRID_X + ex * CELL + 6, GRID_Y + ey * CELL + 6, CELL - 12, CELL - 12)
            pygame.draw.rect(self.screen, COLORS["bad"], erect, border_radius=6)
            if self._dist((ex, ey), self.player) <= 2:
                cx = GRID_X + ex * CELL + CELL // 2
                cy = GRID_Y + ey * CELL + CELL // 2
                pygame.draw.circle(self.screen, (255, 120, 120), (cx, cy), 13, 2)

        px, py = self.player
        prect = pygame.Rect(GRID_X + px * CELL + 5, GRID_Y + py * CELL + 5, CELL - 10, CELL - 10)
        if pygame.time.get_ticks() - self.last_hit_tick < self.invuln_ms:
            blink = (pygame.time.get_ticks() // 110) % 2 == 0
            pcol = (119, 190, 255) if blink else COLORS["accent2"]
        else:
            pcol = COLORS["accent2"]
        pygame.draw.rect(self.screen, pcol, prect, border_radius=7)

    def _draw_sidebar(self):
        box = pygame.Rect(790, 140, 260, 460)
        pygame.draw.rect(self.screen, (35, 35, 35), box.move(0, 4), border_radius=12)
        pygame.draw.rect(self.screen, COLORS["panel2"], box, border_radius=12)
        pygame.draw.rect(self.screen, (194, 184, 166), box, 2, border_radius=12)

        elapsed = max(0, (pygame.time.get_ticks() - self.start_ticks) // 1000)
        mins, secs = divmod(elapsed, 60)

        info = [
            f"Mode: {self.difficulty}",
            f"HP: {self.hp}",
            f"Score: {self.score}",
            f"Cores Left: {len(self.cores)}",
            f"Quota: {self.collected}/{self.core_quota}",
            f"Beacon: {'ON' if self.beacon_activated else 'OFF'}",
            f"Timer: {mins:02d}:{secs:02d}",
            f"Dash: {self.dash_charges}/{self.max_dash}",
        ]

        self.screen.blit(self.font_h.render("Mission HUD", True, COLORS["title"]), (812, 160))
        y = 206
        for line in info:
            self.screen.blit(self.font_body.render(line, True, COLORS["text"]), (812, y))
            y += 30

        emp_left = max(0, (self.emp_cooldown_ms - (pygame.time.get_ticks() - self.last_emp_tick)) // 1000)
        controls = [
            "WASD / Arrows: Move",
            "SPACE: Dash 2 tiles",
            f"E: EMP freeze ({emp_left}s)",
            "Drones chase only when close",
            "Hit requires short lock-on",
            "H: Hint | R: Restart | ESC: Menu",
        ]
        y = 436
        self.screen.blit(self.font_h.render("Controls", True, COLORS["title"]), (812, 400))
        for c in controls:
            self.screen.blit(self.font_small.render(c, True, COLORS["muted"]), (812, y))
            y += 22

        self.screen.blit(self.font_small.render("Win Paths:", True, COLORS["title"]), (812, 560))
        self.screen.blit(self.font_small.render("1) All cores + any exit", True, COLORS["muted"]), (812, 578))
        self.screen.blit(self.font_small.render("2) Quota + blue exit", True, COLORS["muted"]), (812, 596))

    def _draw_status(self):
        col = COLORS["good"] if self.win else COLORS["bad"] if self.state == "fail" else COLORS["text"]
        self.screen.blit(self.font_body.render(f"Status: {self.status}", True, col), (72, 690))

    def _draw_menu(self):
        self._draw_panel()
        self._draw_grid_shell()

        side = pygame.Rect(808, 140, 270, 360)
        pygame.draw.rect(self.screen, (35, 35, 35), side.move(0, 4), border_radius=12)
        pygame.draw.rect(self.screen, COLORS["panel2"], side, border_radius=12)
        pygame.draw.rect(self.screen, (194, 184, 166), side, 2, border_radius=12)

        self.screen.blit(self.font_h.render("Mission Setup", True, COLORS["title"]), (826, 162))
        self.screen.blit(self.font_small.render("Choose difficulty and launch", True, COLORS["muted"]), (826, 194))
        self.screen.blit(self.font_small.render("your route through the arena.", True, COLORS["muted"]), (826, 216))
        self.screen.blit(self.font_body.render(f"Difficulty: {self.difficulty}", True, COLORS["title"]), (842, 458))

        mp = pygame.mouse.get_pos()
        self.menu_play.draw(self.screen, self.font_body, mp)
        self.menu_diff.draw(self.screen, self.font_body, mp)
        self.menu_quit.draw(self.screen, self.font_body, mp)

    def _draw_grid_shell(self):
        box = pygame.Rect(GRID_X - 12, GRID_Y - 12, GRID_COLS * CELL + 24, GRID_ROWS * CELL + 24)
        pygame.draw.rect(self.screen, (34, 34, 34), box.move(0, 4), border_radius=14)
        pygame.draw.rect(self.screen, COLORS["panel2"], box, border_radius=14)
        pygame.draw.rect(self.screen, (194, 184, 166), box, 2, border_radius=14)
        self.screen.blit(self.font_h.render("Arena Preview", True, COLORS["title"]), (GRID_X, GRID_Y + 10))
        self.screen.blit(self.font_small.render("Press Start Mission to spawn a fresh tactical maze.", True, COLORS["muted"]), (GRID_X, GRID_Y + 46))

        preview = pygame.Rect(GRID_X + 16, GRID_Y + 84, GRID_COLS * CELL - 32, GRID_ROWS * CELL - 110)
        pygame.draw.rect(self.screen, (225, 219, 204), preview, border_radius=8)
        pygame.draw.rect(self.screen, (203, 192, 171), preview, 2, border_radius=8)

        step = 24
        for x in range(preview.left + 8, preview.right - 8, step):
            pygame.draw.line(self.screen, (214, 206, 190), (x, preview.top + 8), (x, preview.bottom - 8), 1)
        for y in range(preview.top + 8, preview.bottom - 8, step):
            pygame.draw.line(self.screen, (214, 206, 190), (preview.left + 8, y), (preview.right - 8, y), 1)

        self.screen.blit(self.font_menu.render("3", True, (214, 92, 92)), (preview.left + 38, preview.top + 26))
        self.screen.blit(self.font_menu.render("2", True, (46, 125, 191)), (preview.left + 132, preview.top + 114))
        self.screen.blit(self.font_menu.render("1", True, (32, 138, 78)), (preview.left + 226, preview.top + 62))
        self.screen.blit(self.font_small.render("Live maze + drones appear after launch", True, COLORS["muted"]), (preview.left + 12, preview.bottom - 28))

    def _draw_play(self):
        self._draw_panel()
        self._draw_grid()
        self._draw_sidebar()
        self._draw_status()

        mp = pygame.mouse.get_pos()
        self.btn_restart.draw(self.screen, self.font_body, mp)
        self.btn_menu.draw(self.screen, self.font_body, mp)

    def _handle_keys(self, event):
        if event.type != pygame.KEYDOWN:
            return

        if event.key in (pygame.K_w, pygame.K_UP):
            self._move_player(0, -1)
        elif event.key in (pygame.K_s, pygame.K_DOWN):
            self._move_player(0, 1)
        elif event.key in (pygame.K_a, pygame.K_LEFT):
            self._move_player(-1, 0)
        elif event.key in (pygame.K_d, pygame.K_RIGHT):
            self._move_player(1, 0)
        elif event.key == pygame.K_h:
            self.show_hint = not self.show_hint
        elif event.key == pygame.K_SPACE:
            self._dash()
        elif event.key == pygame.K_e:
            self._emp()
        elif event.key == pygame.K_r:
            self.start_game()
        elif event.key == pygame.K_ESCAPE:
            self.to_menu()

    def run(self):
        while self.running:
            dt_ms = self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if self.state == "menu":
                    self.menu_play.handle(event)
                    self.menu_diff.handle(event)
                    self.menu_quit.handle(event)
                else:
                    self.btn_restart.handle(event)
                    self.btn_menu.handle(event)
                    self._handle_keys(event)

            if self.state in ("play", "fail"):
                self._update_enemies(dt_ms)

            self._draw_bg()
            if self.state == "menu":
                self._draw_menu()
            else:
                self._draw_play()

            pygame.display.flip()

        pygame.quit()


def main():
    game = PathFinderArena()
    game.run()


if __name__ == "__main__":
    main()
