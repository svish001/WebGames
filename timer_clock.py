import datetime as dt
import math
from array import array

import pygame


WIDTH, HEIGHT = 1120, 760
FPS = 60

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


def clamp(value, low, high):
    return max(low, min(high, value))


class Button:
    def __init__(self, rect, text, color, hover_color, text_color, action):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.action = action
        self.enabled = True

    def draw(self, screen, font, mouse_pos):
        color = self.hover_color if self.enabled and self.rect.collidepoint(mouse_pos) else self.color
        if not self.enabled:
            color = tuple(max(0, c - 70) for c in color)

        pygame.draw.rect(screen, (32, 32, 32), self.rect.move(0, 3), border_radius=12)
        pygame.draw.rect(screen, color, self.rect, border_radius=12)
        pygame.draw.rect(screen, (40, 44, 52), self.rect, 2, border_radius=12)

        txt = font.render(self.text, True, self.text_color)
        screen.blit(txt, txt.get_rect(center=self.rect.center))

    def handle_event(self, event):
        if self.enabled and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.action()


class InputBox:
    def __init__(self, x, y, w, h, value, max_chars=2):
        self.rect = pygame.Rect(x, y, w, h)
        self.value = value
        self.max_chars = max_chars
        self.active = False

    def draw(self, screen, font):
        fill = COLORS["white"] if self.active else COLORS["panel2"]
        pygame.draw.rect(screen, (40, 40, 40), self.rect.move(0, 2), border_radius=10)
        pygame.draw.rect(screen, fill, self.rect, border_radius=10)
        pygame.draw.rect(screen, COLORS["accent2"] if self.active else COLORS["title"], self.rect, 2, border_radius=10)

        txt = font.render(self.value if self.value else "00", True, COLORS["text"])
        screen.blit(txt, txt.get_rect(center=self.rect.center))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.active = self.rect.collidepoint(event.pos)
            return

        if not self.active or event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_BACKSPACE:
            self.value = self.value[:-1]
        elif event.key in (pygame.K_RETURN, pygame.K_TAB):
            self.active = False
        elif event.unicode.isdigit() and len(self.value) < self.max_chars:
            self.value += event.unicode

    def get_int(self):
        return int(self.value) if self.value else 0

    def set_int(self, number):
        self.value = str(number)


class TimerAlarmApp:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Timer And Alarm Studio")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        self.font_title = pygame.font.SysFont("Avenir Next", 48, bold=True)
        self.font_clock = pygame.font.SysFont("Menlo", 40, bold=True)
        self.font_h1 = pygame.font.SysFont("Avenir", 32, bold=True)
        self.font_h2 = pygame.font.SysFont("Avenir", 26, bold=True)
        self.font_body = pygame.font.SysFont("Avenir", 20)
        self.font_small = pygame.font.SysFont("Avenir", 16)

        self.mode = "timer"
        self.status = "Ready"

        self.timer_hours = InputBox(140, 280, 105, 64, "0")
        self.timer_minutes = InputBox(278, 280, 105, 64, "1")
        self.timer_seconds = InputBox(416, 280, 105, 64, "0")
        self.inputs = [self.timer_hours, self.timer_minutes, self.timer_seconds]

        self.timer_total = 60
        self.timer_remaining = 60
        self.timer_running = False
        self.timer_finished = False
        self.last_tick = pygame.time.get_ticks()

        self.alarm_hour = InputBox(140, 522, 105, 64, "7")
        self.alarm_minute = InputBox(278, 522, 105, 64, "30")
        self.alarm_inputs = [self.alarm_hour, self.alarm_minute]

        self.alarm_enabled = False
        self.alarm_ring = False
        self.last_alarm_date = None
        self.flash_timer = 0.0
        self.snooze_until = None

        self.beep_sound = self._create_beep_sound()
        self.last_beep_tick = 0

        self.btn_mode_timer = Button((820, 206, 230, 56), "Timer Mode", COLORS["accent2"], (35, 141, 214), COLORS["white"], self._switch_timer)
        self.btn_mode_alarm = Button((820, 274, 230, 56), "Alarm Mode", COLORS["accent2"], (35, 141, 214), COLORS["white"], self._switch_alarm)

        self.btn_set_timer = Button((560, 280, 170, 64), "Set", COLORS["good"], (38, 156, 87), COLORS["white"], self._set_timer)
        self.btn_start_pause = Button((140, 365, 180, 56), "Start", COLORS["accent2"], (35, 141, 214), COLORS["white"], self._toggle_timer)
        self.btn_reset = Button((342, 365, 180, 56), "Reset", COLORS["warn"], (221, 111, 55), COLORS["white"], self._reset_timer)

        self.btn_set_alarm = Button((420, 522, 180, 64), "Set Alarm", COLORS["good"], (38, 156, 87), COLORS["white"], self._set_alarm)
        self.btn_toggle_alarm = Button((140, 618, 220, 54), "Enable Alarm", COLORS["accent2"], (35, 141, 214), COLORS["white"], self._toggle_alarm)
        self.btn_snooze = Button((382, 618, 170, 54), "Snooze", COLORS["warn"], (221, 111, 55), COLORS["white"], self._snooze_alarm)
        self.btn_stop_alarm = Button((574, 618, 190, 54), "Stop Alarm", COLORS["bad"], (220, 80, 80), COLORS["white"], self._stop_alarm)

    def _create_beep_sound(self):
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=1)

            sample_rate = 22050
            duration = 0.22
            volume = 0.35
            frequency = 880
            total = int(sample_rate * duration)

            data = array("h")
            for i in range(total):
                sample = int(32767 * volume * math.sin(2 * math.pi * frequency * i / sample_rate))
                data.append(sample)
            return pygame.mixer.Sound(buffer=data.tobytes())
        except pygame.error:
            return None

    def _switch_timer(self):
        self.mode = "timer"
        self.status = "Timer mode active"

    def _switch_alarm(self):
        self.mode = "alarm"
        self.status = "Alarm mode active"

    def _set_timer(self):
        h = clamp(self.timer_hours.get_int(), 0, 99)
        m = clamp(self.timer_minutes.get_int(), 0, 59)
        s = clamp(self.timer_seconds.get_int(), 0, 59)
        total = h * 3600 + m * 60 + s
        if total <= 0:
            self.status = "Set a time greater than 00:00:00"
            return

        self.timer_hours.set_int(h)
        self.timer_minutes.set_int(m)
        self.timer_seconds.set_int(s)
        self.timer_total = total
        self.timer_remaining = total
        self.timer_running = False
        self.timer_finished = False
        self.btn_start_pause.text = "Start"
        self.status = f"Timer set to {self._format_hms(self.timer_total)}"

    def _toggle_timer(self):
        if self.timer_remaining <= 0 and not self.timer_finished:
            self._set_timer()
        if self.timer_remaining <= 0:
            self.status = "Set timer first"
            return

        self.timer_running = not self.timer_running
        self.last_tick = pygame.time.get_ticks()
        self.btn_start_pause.text = "Pause" if self.timer_running else "Resume"
        self.status = "Timer running" if self.timer_running else "Timer paused"

    def _reset_timer(self):
        self.timer_running = False
        self.timer_finished = False
        self.timer_remaining = self.timer_total
        self.btn_start_pause.text = "Start"
        self.status = "Timer reset"

    def _set_alarm(self):
        h = clamp(self.alarm_hour.get_int(), 0, 23)
        m = clamp(self.alarm_minute.get_int(), 0, 59)
        self.alarm_hour.set_int(h)
        self.alarm_minute.set_int(m)
        self.status = f"Alarm set to {h:02d}:{m:02d}"

    def _toggle_alarm(self):
        self.alarm_enabled = not self.alarm_enabled
        self.btn_toggle_alarm.text = "Disable Alarm" if self.alarm_enabled else "Enable Alarm"
        self.status = "Alarm enabled" if self.alarm_enabled else "Alarm disabled"

    def _stop_alarm(self):
        self.alarm_ring = False
        self.flash_timer = 0
        self.status = "Alarm stopped"

    def _snooze_alarm(self):
        if not self.alarm_ring:
            self.status = "Alarm is not ringing"
            return
        self.alarm_ring = False
        self.flash_timer = 0
        self.snooze_until = dt.datetime.now() + dt.timedelta(minutes=5)
        self.status = f"Snoozed until {self.snooze_until.strftime('%H:%M')}"

    def _format_hms(self, seconds):
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f"{h:02d}:{m:02d}:{s:02d}"

    def _handle_timer_tick(self):
        now_tick = pygame.time.get_ticks()
        elapsed_ms = now_tick - self.last_tick
        if self.timer_running and elapsed_ms >= 1000:
            steps = elapsed_ms // 1000
            self.last_tick += steps * 1000
            self.timer_remaining = max(0, self.timer_remaining - steps)
            if self.timer_remaining == 0:
                self.timer_running = False
                self.timer_finished = True
                self.btn_start_pause.text = "Start"
                self.status = "Timer complete"
                self.alarm_ring = True

    def _handle_alarm(self):
        now = dt.datetime.now()

        if self.snooze_until and now >= self.snooze_until:
            self.snooze_until = None
            self.alarm_ring = True
            self.status = "Snooze ended"

        if self.alarm_enabled:
            alarm_h = clamp(self.alarm_hour.get_int(), 0, 23)
            alarm_m = clamp(self.alarm_minute.get_int(), 0, 59)
            key = now.strftime("%Y-%m-%d")
            if now.hour == alarm_h and now.minute == alarm_m and now.second == 0:
                if self.last_alarm_date != key:
                    self.last_alarm_date = key
                    self.alarm_ring = True
                    self.status = "Alarm time reached"

        if self.alarm_ring:
            self.flash_timer += 1 / FPS
            tick = pygame.time.get_ticks()
            if self.beep_sound and tick - self.last_beep_tick > 650:
                self.beep_sound.play()
                self.last_beep_tick = tick

    def _draw_background(self):
        for y in range(HEIGHT):
            t = y / HEIGHT
            r = int(COLORS["bg"][0] + (COLORS["bg2"][0] - COLORS["bg"][0]) * t)
            g = int(COLORS["bg"][1] + (COLORS["bg2"][1] - COLORS["bg"][1]) * t)
            b = int(COLORS["bg"][2] + (COLORS["bg2"][2] - COLORS["bg"][2]) * t)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (WIDTH, y))

        pygame.draw.circle(self.screen, (255, 183, 3), (80, 80), 155)
        pygame.draw.circle(self.screen, (142, 202, 230), (1040, 620), 210)
        pygame.draw.circle(self.screen, (251, 133, 0), (420, 790), 180)

    def _draw_card(self, rect, radius=14):
        pygame.draw.rect(self.screen, (35, 35, 35), rect.move(0, 4), border_radius=radius)
        pygame.draw.rect(self.screen, COLORS["panel2"], rect, border_radius=radius)
        pygame.draw.rect(self.screen, (195, 186, 167), rect, 2, border_radius=radius)

    def _draw_ui(self):
        mouse_pos = pygame.mouse.get_pos()

        panel = pygame.Rect(60, 50, 1000, 660)
        pygame.draw.rect(self.screen, (25, 25, 25), panel.move(0, 5), border_radius=18)
        pygame.draw.rect(self.screen, COLORS["panel"], panel, border_radius=18)
        pygame.draw.rect(self.screen, (205, 190, 160), panel, 2, border_radius=18)

        self.screen.blit(self.font_title.render("Timer + Alarm Studio", True, COLORS["title"]), (95, 76))
        self.screen.blit(self.font_small.render("Focus timer and smart alarm dashboard", True, COLORS["muted"]), (98, 122))

        now = dt.datetime.now()
        self.screen.blit(self.font_h2.render(now.strftime("%A  %d %b %Y   %H:%M:%S"), True, COLORS["text"]), (98, 152))
        self.screen.blit(self.font_body.render(f"Current Mode: {self.mode.title()}", True, COLORS["muted"]), (98, 188))

        if self.mode == "timer":
            self.btn_mode_timer.color = COLORS["good"]
            self.btn_mode_timer.hover_color = (44, 158, 96)
            self.btn_mode_alarm.color = COLORS["accent2"]
            self.btn_mode_alarm.hover_color = (35, 141, 214)
        else:
            self.btn_mode_alarm.color = COLORS["good"]
            self.btn_mode_alarm.hover_color = (44, 158, 96)
            self.btn_mode_timer.color = COLORS["accent2"]
            self.btn_mode_timer.hover_color = (35, 141, 214)

        self.btn_mode_timer.draw(self.screen, self.font_body, mouse_pos)
        self.btn_mode_alarm.draw(self.screen, self.font_body, mouse_pos)

        timer_box = pygame.Rect(100, 238, 680, 220)
        self._draw_card(timer_box)
        self.screen.blit(self.font_h2.render("Timer", True, COLORS["title"]), (118, 246))
        self.screen.blit(self.font_small.render("HH        MM        SS", True, COLORS["muted"]), (148, 268))

        self.timer_hours.draw(self.screen, self.font_h1)
        self.timer_minutes.draw(self.screen, self.font_h1)
        self.timer_seconds.draw(self.screen, self.font_h1)
        self.screen.blit(self.font_h1.render(":", True, COLORS["title"]), (252, 296))
        self.screen.blit(self.font_h1.render(":", True, COLORS["title"]), (390, 296))

        self.btn_set_timer.enabled = self.mode == "timer"
        self.btn_start_pause.enabled = self.mode == "timer"
        self.btn_reset.enabled = self.mode == "timer"

        self.btn_set_timer.draw(self.screen, self.font_body, mouse_pos)
        self.btn_start_pause.draw(self.screen, self.font_body, mouse_pos)
        self.btn_reset.draw(self.screen, self.font_body, mouse_pos)

        remain = self._format_hms(int(self.timer_remaining))
        remain_color = COLORS["bad"] if self.timer_remaining < 15 and self.timer_running else COLORS["text"]
        self.screen.blit(self.font_clock.render(remain, True, remain_color), (540, 366))
        self.screen.blit(self.font_small.render("Remaining", True, COLORS["muted"]), (546, 340))

        alarm_box = pygame.Rect(100, 486, 680, 210)
        self._draw_card(alarm_box)
        self.screen.blit(self.font_h2.render("Alarm", True, COLORS["title"]), (118, 498))

        self.alarm_hour.draw(self.screen, self.font_h1)
        self.alarm_minute.draw(self.screen, self.font_h1)
        self.screen.blit(self.font_h1.render(":", True, COLORS["title"]), (252, 540))
        self.screen.blit(self.font_small.render("Set 24-hour time", True, COLORS["muted"]), (120, 510))

        alarm_state = "Enabled" if self.alarm_enabled else "Disabled"
        alarm_color = COLORS["good"] if self.alarm_enabled else COLORS["muted"]
        self.screen.blit(self.font_body.render(f"Alarm: {alarm_state}", True, alarm_color), (620, 534))
        if self.snooze_until:
            snooze = self.snooze_until.strftime('%H:%M')
            self.screen.blit(self.font_small.render(f"Snoozed to {snooze}", True, COLORS["warn"]), (620, 560))

        self.btn_set_alarm.enabled = self.mode == "alarm"
        self.btn_toggle_alarm.enabled = self.mode == "alarm"
        self.btn_snooze.enabled = self.mode == "alarm" and self.alarm_ring
        self.btn_stop_alarm.enabled = self.mode == "alarm" and self.alarm_ring

        self.btn_set_alarm.draw(self.screen, self.font_body, mouse_pos)
        self.btn_toggle_alarm.draw(self.screen, self.font_body, mouse_pos)
        self.btn_snooze.draw(self.screen, self.font_body, mouse_pos)
        self.btn_stop_alarm.draw(self.screen, self.font_body, mouse_pos)

        status_color = COLORS["bad"] if self.alarm_ring and int(self.flash_timer * 6) % 2 == 0 else COLORS["text"]
        self.screen.blit(self.font_body.render(f"Status: {self.status}", True, status_color), (100, 720))
        self.screen.blit(self.font_small.render("Shortcuts: T timer | A alarm | Space start/pause | R reset | M stop alarm", True, COLORS["muted"]), (100, 695))

    def _handle_keyboard_shortcuts(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_t:
            self._switch_timer()
        elif event.key == pygame.K_a:
            self._switch_alarm()
        elif event.key == pygame.K_SPACE and self.mode == "timer":
            self._toggle_timer()
        elif event.key == pygame.K_r and self.mode == "timer":
            self._reset_timer()
        elif event.key == pygame.K_m:
            self._stop_alarm()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                for box in self.inputs + self.alarm_inputs:
                    box.handle_event(event)

                self.btn_mode_timer.handle_event(event)
                self.btn_mode_alarm.handle_event(event)
                self.btn_set_timer.handle_event(event)
                self.btn_start_pause.handle_event(event)
                self.btn_reset.handle_event(event)
                self.btn_set_alarm.handle_event(event)
                self.btn_toggle_alarm.handle_event(event)
                self.btn_snooze.handle_event(event)
                self.btn_stop_alarm.handle_event(event)
                self._handle_keyboard_shortcuts(event)

            self._handle_timer_tick()
            self._handle_alarm()
            self._draw_background()
            self._draw_ui()

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()


def main():
    app = TimerAlarmApp()
    app.run()


if __name__ == "__main__":
    main()
