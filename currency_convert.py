import datetime as dt
import tkinter as tk
from tkinter import messagebox, ttk
from urllib.request import urlopen
import json


APP_W = 1120
APP_H = 760
API_BASE = "https://api.frankfurter.app"
REFRESH_MS = 90000

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

FALLBACK_CURRENCIES = {
    "USD": "US Dollar",
    "EUR": "Euro",
    "GBP": "British Pound",
    "INR": "Indian Rupee",
    "JPY": "Japanese Yen",
    "CAD": "Canadian Dollar",
    "AUD": "Australian Dollar",
    "CHF": "Swiss Franc",
}

FALLBACK_USD_RATES = {
    "USD": 1.0,
    "EUR": 0.92,
    "GBP": 0.79,
    "INR": 83.1,
    "JPY": 151.4,
    "CAD": 1.35,
    "AUD": 1.52,
    "CHF": 0.89,
}


def rgb_to_hex(rgb):
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"


def fetch_json(url, timeout=8):
    with urlopen(url, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


class CustomButton(tk.Canvas):
    def __init__(self, parent, text, color, hover_color, command, width=170, height=46):
        super().__init__(parent, width=width, height=height, bg=parent["bg"], highlightthickness=0)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.command = command
        self.width_val = width
        self.height_val = height
        self.is_hovered = False

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self._draw()

    def _on_enter(self, _event):
        self.is_hovered = True
        self._draw()

    def _on_leave(self, _event):
        self.is_hovered = False
        self._draw()

    def _on_click(self, _event):
        self.command()

    def _draw(self):
        self.delete("all")
        color = self.hover_color if self.is_hovered else self.color
        self.create_rectangle(2, 4, self.width_val, self.height_val, fill="gray20", outline="")
        self.create_rectangle(
            0,
            0,
            self.width_val - 2,
            self.height_val - 4,
            fill=rgb_to_hex(color),
            outline=rgb_to_hex((40, 44, 52)),
            width=2,
        )
        self.create_text(
            self.width_val // 2,
            (self.height_val - 4) // 2,
            text=self.text,
            fill=rgb_to_hex(COLORS["white"]),
            font=("Avenir", 11, "bold"),
        )


class CurrencyStudio:
    def __init__(self, root):
        self.root = root
        self.root.title("Currency Converter Studio")
        self.root.geometry(f"{APP_W}x{APP_H}")
        self.root.resizable(False, False)

        self.currency_map = {}
        self.rate_cache = {}
        self.history_rows = []
        self.last_rate = None
        self.last_fetch_text = ""

        self.amount_var = tk.StringVar(value="100")
        self.from_var = tk.StringVar(value="USD")
        self.to_var = tk.StringVar(value="INR")
        self.result_var = tk.StringVar(value="0.00")
        self.status_var = tk.StringVar(value="Loading currencies...")
        self.quick_var = tk.StringVar(value="EUR,GBP,JPY")

        self._build_ui()
        self._load_currencies()
        self._schedule_refresh()

    def _build_ui(self):
        self.bg_canvas = tk.Canvas(self.root, width=APP_W, height=APP_H, highlightthickness=0)
        self.bg_canvas.pack(fill=tk.BOTH, expand=True)
        self._paint_background(self.bg_canvas)

        self.panel = tk.Canvas(self.root, width=1060, height=690, bg=rgb_to_hex(COLORS["panel"]), highlightthickness=0)
        self.panel.place(x=30, y=30)
        self.panel.create_rectangle(0, 5, 1060, 690, fill="gray20", outline="")
        self.panel.create_rectangle(
            0,
            0,
            1056,
            684,
            fill=rgb_to_hex(COLORS["panel"]),
            outline=rgb_to_hex((205, 190, 160)),
            width=2,
        )
        self.panel.create_text(
            40,
            28,
            text="Currency Converter Studio",
            anchor="nw",
            fill=rgb_to_hex(COLORS["title"]),
            font=("Avenir", 34, "bold"),
        )
        self.panel.create_text(
            40,
            72,
            text="Live exchange rates, quick basket conversion, history and richer conversion flow",
            anchor="nw",
            fill=rgb_to_hex(COLORS["muted"]),
            font=("Avenir", 12),
        )

        self.left = tk.Frame(self.root, bg=rgb_to_hex(COLORS["panel"]))
        self.left.place(x=78, y=144, width=650, height=540)

        self.right = tk.Frame(self.root, bg=rgb_to_hex(COLORS["panel2"]))
        self.right.place(x=752, y=144, width=295, height=540)

        self._build_left_controls()
        self._build_right_panel()

    def _paint_background(self, canvas):
        for y in range(APP_H):
            t = y / max(1, APP_H - 1)
            r = int(COLORS["bg"][0] + (COLORS["bg2"][0] - COLORS["bg"][0]) * t)
            g = int(COLORS["bg"][1] + (COLORS["bg2"][1] - COLORS["bg"][1]) * t)
            b = int(COLORS["bg"][2] + (COLORS["bg2"][2] - COLORS["bg"][2]) * t)
            canvas.create_line(0, y, APP_W, y, fill=rgb_to_hex((r, g, b)))
        canvas.create_oval(-120, -70, 220, 250, fill="#ffb703", outline="")
        canvas.create_oval(860, 460, 1210, 860, fill="#8ecae6", outline="")

    def _build_left_controls(self):
        row = tk.Frame(self.left, bg=rgb_to_hex(COLORS["panel"]))
        row.pack(anchor="w", pady=(4, 12))
        tk.Label(
            row,
            text="Amount",
            bg=rgb_to_hex(COLORS["panel"]),
            fg=rgb_to_hex(COLORS["title"]),
            font=("Avenir", 13, "bold"),
        ).pack(side=tk.LEFT)
        tk.Entry(
            row,
            textvariable=self.amount_var,
            width=14,
            justify="center",
            font=("Avenir", 16, "bold"),
            relief=tk.FLAT,
            bd=2,
            highlightthickness=2,
            highlightbackground=rgb_to_hex(COLORS["accent2"]),
        ).pack(side=tk.LEFT, padx=(14, 0))

        pick_row = tk.Frame(self.left, bg=rgb_to_hex(COLORS["panel"]))
        pick_row.pack(anchor="w", pady=10)

        self.from_box = ttk.Combobox(pick_row, textvariable=self.from_var, state="readonly", width=20, font=("Avenir", 12))
        self.from_box.pack(side=tk.LEFT)

        swap_btn = CustomButton(
            pick_row,
            "Swap",
            COLORS["warn"],
            (225, 125, 52),
            self._swap,
            width=90,
            height=40,
        )
        swap_btn.pack(side=tk.LEFT, padx=12)

        self.to_box = ttk.Combobox(pick_row, textvariable=self.to_var, state="readonly", width=20, font=("Avenir", 12))
        self.to_box.pack(side=tk.LEFT)

        btns = tk.Frame(self.left, bg=rgb_to_hex(COLORS["panel"]))
        btns.pack(anchor="w", pady=(16, 8))
        CustomButton(btns, "Convert", COLORS["good"], (38, 156, 87), self.convert, width=145).pack(side=tk.LEFT, padx=(0, 10))
        CustomButton(btns, "Get Rate", COLORS["accent2"], (35, 141, 214), self.get_rate_only, width=145).pack(side=tk.LEFT, padx=(0, 10))
        CustomButton(btns, "Refresh", COLORS["warn"], (225, 125, 52), self._refresh_live_rates, width=145).pack(side=tk.LEFT)

        result_card = tk.Frame(self.left, bg=rgb_to_hex(COLORS["panel2"]))
        result_card.pack(fill=tk.X, pady=(10, 8))
        tk.Label(
            result_card,
            text="Converted Result",
            bg=rgb_to_hex(COLORS["panel2"]),
            fg=rgb_to_hex(COLORS["title"]),
            font=("Avenir", 12, "bold"),
        ).pack(anchor="w", padx=14, pady=(10, 2))
        tk.Label(
            result_card,
            textvariable=self.result_var,
            bg=rgb_to_hex(COLORS["panel2"]),
            fg=rgb_to_hex(COLORS["accent2"]),
            font=("Avenir", 30, "bold"),
        ).pack(anchor="w", padx=14, pady=(0, 8))

        quick_row = tk.Frame(self.left, bg=rgb_to_hex(COLORS["panel"]))
        quick_row.pack(fill=tk.X, pady=(10, 4))
        tk.Label(
            quick_row,
            text="Quick Targets (comma-separated codes)",
            bg=rgb_to_hex(COLORS["panel"]),
            fg=rgb_to_hex(COLORS["title"]),
            font=("Avenir", 11, "bold"),
        ).pack(anchor="w")
        tk.Entry(
            quick_row,
            textvariable=self.quick_var,
            font=("Avenir", 11),
            relief=tk.FLAT,
            bd=2,
            highlightthickness=1,
            highlightbackground=rgb_to_hex(COLORS["accent2"]),
        ).pack(fill=tk.X, pady=(6, 0))

        quick_btns = tk.Frame(self.left, bg=rgb_to_hex(COLORS["panel"]))
        quick_btns.pack(anchor="w", pady=(8, 8))
        CustomButton(
            quick_btns,
            "Convert Basket",
            COLORS["accent2"],
            (35, 141, 214),
            self._convert_quick_targets,
            width=170,
        ).pack(side=tk.LEFT)

        self.quick_output = tk.Text(
            self.left,
            height=7,
            width=74,
            bg=rgb_to_hex(COLORS["panel2"]),
            fg=rgb_to_hex(COLORS["text"]),
            relief=tk.FLAT,
            font=("Menlo", 11),
        )
        self.quick_output.pack(fill=tk.X, pady=(6, 0))

    def _build_right_panel(self):
        tk.Label(
            self.right,
            text="Session Insights",
            bg=rgb_to_hex(COLORS["panel2"]),
            fg=rgb_to_hex(COLORS["title"]),
            font=("Avenir", 16, "bold"),
        ).pack(anchor="w", padx=12, pady=(10, 8))

        self.meta_label = tk.Label(
            self.right,
            text="",
            justify="left",
            bg=rgb_to_hex(COLORS["panel2"]),
            fg=rgb_to_hex(COLORS["muted"]),
            font=("Avenir", 10),
        )
        self.meta_label.pack(anchor="w", padx=12)

        tk.Label(
            self.right,
            text="History",
            bg=rgb_to_hex(COLORS["panel2"]),
            fg=rgb_to_hex(COLORS["title"]),
            font=("Avenir", 12, "bold"),
        ).pack(anchor="w", padx=12, pady=(14, 6))

        self.history_box = tk.Listbox(
            self.right,
            height=14,
            bg=rgb_to_hex(COLORS["panel"]),
            fg=rgb_to_hex(COLORS["text"]),
            font=("Menlo", 10),
            relief=tk.FLAT,
        )
        self.history_box.pack(fill=tk.BOTH, expand=True, padx=12)

        bottom = tk.Frame(self.right, bg=rgb_to_hex(COLORS["panel2"]))
        bottom.pack(fill=tk.X, padx=12, pady=10)
        CustomButton(bottom, "Clear History", COLORS["bad"], (216, 84, 84), self._clear_history, width=120, height=38).pack(side=tk.LEFT)

        tk.Label(
            self.root,
            textvariable=self.status_var,
            bg=rgb_to_hex(COLORS["panel"]),
            fg=rgb_to_hex(COLORS["muted"]),
            font=("Avenir", 10, "bold"),
        ).place(x=78, y=690)

    def _load_currencies(self):
        try:
            data = fetch_json(f"{API_BASE}/currencies", timeout=8)
            if not isinstance(data, dict) or not data:
                raise ValueError("No currency payload")
            self.currency_map = dict(sorted(data.items()))
            self.status_var.set("Live currency list loaded")
        except Exception:
            self.currency_map = dict(sorted(FALLBACK_CURRENCIES.items()))
            self.status_var.set("Using fallback currency list (offline mode)")

        codes = list(self.currency_map.keys())
        self.from_box["values"] = codes
        self.to_box["values"] = codes

        if self.from_var.get() not in codes:
            self.from_var.set(codes[0])
        if self.to_var.get() not in codes:
            self.to_var.set(codes[min(1, len(codes) - 1)])

        self._refresh_meta()

    def _schedule_refresh(self):
        self._refresh_live_rates(silent=True)
        self.root.after(REFRESH_MS, self._schedule_refresh)

    def _refresh_live_rates(self, silent=False):
        base = self.from_var.get().upper()
        if not base:
            return
        try:
            data = fetch_json(f"{API_BASE}/latest?from={base}", timeout=8)
            if "rates" not in data:
                raise ValueError("No live rates")
            rates = data["rates"]
            rates[base] = 1.0
            self.rate_cache[base] = rates
            stamp = data.get("date", dt.date.today().isoformat())
            self.last_fetch_text = f"{stamp} · live"
            if not silent:
                self.status_var.set(f"Rates refreshed for {base}")
        except Exception:
            if base == "USD":
                self.rate_cache["USD"] = FALLBACK_USD_RATES.copy()
            self.last_fetch_text = f"{dt.date.today().isoformat()} · fallback"
            if not silent:
                self.status_var.set("Rate refresh failed, fallback kept")

        self._refresh_meta()

    def _get_rate(self, c_from, c_to):
        c_from = c_from.upper()
        c_to = c_to.upper()
        if c_from == c_to:
            return 1.0

        if c_from not in self.rate_cache:
            self._refresh_live_rates(silent=True)

        rates = self.rate_cache.get(c_from)
        if rates and c_to in rates:
            return rates[c_to]

        # Fallback through USD synthetic cross-rate if live endpoint is unavailable.
        if c_from in FALLBACK_USD_RATES and c_to in FALLBACK_USD_RATES:
            return FALLBACK_USD_RATES[c_to] / FALLBACK_USD_RATES[c_from]

        raise ValueError("Rate unavailable for selected pair")

    def _swap(self):
        a = self.from_var.get()
        b = self.to_var.get()
        self.from_var.set(b)
        self.to_var.set(a)
        self.status_var.set("Pair swapped")

    def _parse_amount(self):
        text = self.amount_var.get().strip().replace(",", "")
        try:
            amount = float(text)
        except ValueError as exc:
            raise ValueError("Enter a valid numeric amount") from exc
        if amount < 0:
            raise ValueError("Amount cannot be negative")
        return amount

    def convert(self):
        try:
            amount = self._parse_amount()
            c_from = self.from_var.get().upper()
            c_to = self.to_var.get().upper()
            rate = self._get_rate(c_from, c_to)
            converted = amount * rate

            self.last_rate = rate
            self.result_var.set(f"{converted:,.4f} {c_to}")
            self.status_var.set(f"Converted {c_from} -> {c_to}")

            stamp = dt.datetime.now().strftime("%H:%M:%S")
            self.history_rows.insert(0, f"{stamp} | {amount:,.2f} {c_from} -> {converted:,.4f} {c_to} @ {rate:,.6f}")
            self.history_rows = self.history_rows[:50]
            self._sync_history_box()
            self._refresh_meta()
        except Exception as exc:
            messagebox.showerror("Conversion Error", str(exc))

    def get_rate_only(self):
        try:
            c_from = self.from_var.get().upper()
            c_to = self.to_var.get().upper()
            rate = self._get_rate(c_from, c_to)
            self.last_rate = rate
            self.status_var.set(f"Rate loaded: 1 {c_from} = {rate:,.6f} {c_to}")
            messagebox.showinfo("Exchange Rate", f"1 {c_from} = {rate:,.6f} {c_to}")
            self._refresh_meta()
        except Exception as exc:
            messagebox.showerror("Rate Error", str(exc))

    def _convert_quick_targets(self):
        self.quick_output.delete("1.0", tk.END)
        try:
            amount = self._parse_amount()
            source = self.from_var.get().upper()
            raw = [x.strip().upper() for x in self.quick_var.get().split(",") if x.strip()]
            if not raw:
                raise ValueError("Provide at least one target currency code")

            lines = []
            for code in raw[:8]:
                try:
                    rate = self._get_rate(source, code)
                    lines.append(f"{amount:,.2f} {source} -> {amount * rate:,.4f} {code}")
                except Exception:
                    lines.append(f"{source} -> {code}: unavailable")

            self.quick_output.insert(tk.END, "\n".join(lines))
            self.status_var.set("Quick basket conversion completed")
        except Exception as exc:
            messagebox.showerror("Quick Convert Error", str(exc))

    def _clear_history(self):
        self.history_rows.clear()
        self._sync_history_box()
        self.status_var.set("History cleared")

    def _sync_history_box(self):
        self.history_box.delete(0, tk.END)
        for row in self.history_rows:
            self.history_box.insert(tk.END, row)

    def _refresh_meta(self):
        base = self.from_var.get().upper()
        target = self.to_var.get().upper()
        from_name = self.currency_map.get(base, "Unknown")
        to_name = self.currency_map.get(target, "Unknown")
        lines = [
            f"From: {base} ({from_name})",
            f"To: {target} ({to_name})",
            f"Currencies Loaded: {len(self.currency_map)}",
            f"Last Source: {self.last_fetch_text or 'not fetched yet'}",
            f"Last Rate: {self.last_rate:,.6f}" if self.last_rate else "Last Rate: --",
            f"Session Time: {dt.datetime.now().strftime('%H:%M:%S')}",
        ]
        self.meta_label.config(text="\n".join(lines))


def main():
    root = tk.Tk()

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    style.configure(
        "TCombobox",
        fieldbackground=rgb_to_hex(COLORS["panel2"]),
        background=rgb_to_hex(COLORS["panel2"]),
        foreground=rgb_to_hex(COLORS["text"]),
    )

    CurrencyStudio(root)
    root.mainloop()


if __name__ == "__main__":
    main()