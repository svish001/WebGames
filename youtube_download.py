import datetime as dt
import importlib
import os
import queue
import re
import ssl
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


_pytube_module = None
YouTube = None
try:
    _pytube_module = importlib.import_module("pytubefix")
    YouTube = getattr(_pytube_module, "YouTube", None)
except Exception:
    try:
        _pytube_module = importlib.import_module("pytube")
        YouTube = getattr(_pytube_module, "YouTube", None)
    except Exception:
        YouTube = None


APP_W = 1120
APP_H = 760

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


def rgb_to_hex(rgb):
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"


def configure_ssl_context():
    """Set an HTTPS context that works reliably on macOS Python installs."""
    try:
        certifi = importlib.import_module("certifi")
        cafile = certifi.where()

        def _certifi_context(*args, **kwargs):
            return ssl.create_default_context(cafile=cafile)

        ssl._create_default_https_context = _certifi_context
        return "certifi"
    except Exception:
        # Last-resort fallback for environments missing local CA cert chains.
        try:
            ssl._create_default_https_context = ssl._create_unverified_context
            return "relaxed"
        except Exception:
            return "system"


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


class DownloadStudio:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Download Studio")
        self.root.geometry(f"{APP_W}x{APP_H}")
        self.root.resizable(False, False)

        self.url_var = tk.StringVar()
        self.path_var = tk.StringVar(value=os.path.expanduser("~/Downloads"))
        self.mode_var = tk.StringVar(value="video")
        self.quality_var = tk.StringVar(value="Highest")
        self.status_var = tk.StringVar(value="Ready")
        self.title_var = tk.StringVar(value="Title: --")
        self.duration_var = tk.StringVar(value="Duration: --")
        self.author_var = tk.StringVar(value="Channel: --")
        self.progress_var = tk.DoubleVar(value=0.0)

        self.quality_map = {}
        self.history = []
        self.pending = queue.Queue()
        self.is_downloading = False
        self.ssl_mode = configure_ssl_context()

        self._build_ui()
        self._pump_events()
        if self.ssl_mode == "certifi":
            self.status_var.set("Ready (SSL: certifi)")
        elif self.ssl_mode == "relaxed":
            self.status_var.set("Ready (SSL: relaxed mode)")
        else:
            self.status_var.set("Ready (SSL: system)")

    def _build_ui(self):
        bg = tk.Canvas(self.root, width=APP_W, height=APP_H, highlightthickness=0)
        bg.pack(fill=tk.BOTH, expand=True)
        self._paint_background(bg)

        panel = tk.Canvas(self.root, width=1060, height=690, bg=rgb_to_hex(COLORS["panel"]), highlightthickness=0)
        panel.place(x=30, y=30)
        panel.create_rectangle(0, 5, 1060, 690, fill="gray20", outline="")
        panel.create_rectangle(
            0,
            0,
            1056,
            684,
            fill=rgb_to_hex(COLORS["panel"]),
            outline=rgb_to_hex((205, 190, 160)),
            width=2,
        )
        panel.create_text(
            40,
            28,
            text="YouTube Download Studio",
            anchor="nw",
            fill=rgb_to_hex(COLORS["title"]),
            font=("Avenir", 34, "bold"),
        )
        panel.create_text(
            40,
            72,
            text="Interactive downloader with metadata preview, quality control, queue and history",
            anchor="nw",
            fill=rgb_to_hex(COLORS["muted"]),
            font=("Avenir", 12),
        )

        self.left = tk.Frame(self.root, bg=rgb_to_hex(COLORS["panel"]))
        self.left.place(x=78, y=140, width=670, height=550)

        self.right = tk.Frame(self.root, bg=rgb_to_hex(COLORS["panel2"]))
        self.right.place(x=760, y=140, width=285, height=550)

        self._build_left()
        self._build_right()

    def _paint_background(self, canvas):
        for y in range(APP_H):
            t = y / max(1, APP_H - 1)
            r = int(COLORS["bg"][0] + (COLORS["bg2"][0] - COLORS["bg"][0]) * t)
            g = int(COLORS["bg"][1] + (COLORS["bg2"][1] - COLORS["bg"][1]) * t)
            b = int(COLORS["bg"][2] + (COLORS["bg2"][2] - COLORS["bg"][2]) * t)
            canvas.create_line(0, y, APP_W, y, fill=rgb_to_hex((r, g, b)))
        canvas.create_oval(-110, -80, 220, 250, fill="#ffb703", outline="")
        canvas.create_oval(860, 450, 1210, 860, fill="#8ecae6", outline="")

    def _build_left(self):
        tk.Label(
            self.left,
            text="Video URL",
            bg=rgb_to_hex(COLORS["panel"]),
            fg=rgb_to_hex(COLORS["title"]),
            font=("Avenir", 12, "bold"),
        ).pack(anchor="w")
        tk.Entry(
            self.left,
            textvariable=self.url_var,
            font=("Avenir", 12),
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=rgb_to_hex(COLORS["accent2"]),
        ).pack(fill=tk.X, pady=(6, 10))

        path_row = tk.Frame(self.left, bg=rgb_to_hex(COLORS["panel"]))
        path_row.pack(fill=tk.X, pady=(0, 10))
        tk.Entry(
            path_row,
            textvariable=self.path_var,
            font=("Avenir", 11),
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=rgb_to_hex(COLORS["accent2"]),
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
        CustomButton(path_row, "Browse", COLORS["accent2"], (35, 141, 214), self._pick_folder, width=96, height=38).pack(side=tk.LEFT, padx=(8, 0))

        pref = tk.Frame(self.left, bg=rgb_to_hex(COLORS["panel"]))
        pref.pack(fill=tk.X, pady=(2, 12))

        tk.Label(pref, text="Mode", bg=rgb_to_hex(COLORS["panel"]), fg=rgb_to_hex(COLORS["title"]), font=("Avenir", 11, "bold")).pack(side=tk.LEFT)
        ttk.Combobox(pref, textvariable=self.mode_var, values=["video", "audio"], state="readonly", width=10).pack(side=tk.LEFT, padx=(8, 16))

        tk.Label(pref, text="Quality", bg=rgb_to_hex(COLORS["panel"]), fg=rgb_to_hex(COLORS["title"]), font=("Avenir", 11, "bold")).pack(side=tk.LEFT)
        self.quality_box = ttk.Combobox(pref, textvariable=self.quality_var, state="readonly", width=24)
        self.quality_box.pack(side=tk.LEFT, padx=(8, 0))
        self.quality_box["values"] = ["Highest"]

        btn_row = tk.Frame(self.left, bg=rgb_to_hex(COLORS["panel"]))
        btn_row.pack(fill=tk.X, pady=(0, 10))
        CustomButton(btn_row, "Analyze", COLORS["accent2"], (35, 141, 214), self.analyze_url, width=130).pack(side=tk.LEFT, padx=(0, 8))
        CustomButton(btn_row, "Download", COLORS["good"], (38, 156, 87), self.start_download, width=130).pack(side=tk.LEFT, padx=(0, 8))
        CustomButton(btn_row, "Queue", COLORS["warn"], (225, 125, 52), self.queue_download, width=130).pack(side=tk.LEFT, padx=(0, 8))
        CustomButton(btn_row, "Clear", COLORS["bad"], (216, 84, 84), self._clear_fields, width=110).pack(side=tk.LEFT)

        meta_box = tk.Frame(self.left, bg=rgb_to_hex(COLORS["panel2"]))
        meta_box.pack(fill=tk.X, pady=(2, 12))
        tk.Label(meta_box, textvariable=self.title_var, anchor="w", bg=rgb_to_hex(COLORS["panel2"]), fg=rgb_to_hex(COLORS["text"]), font=("Avenir", 11, "bold")).pack(fill=tk.X, padx=10, pady=(8, 2))
        tk.Label(meta_box, textvariable=self.author_var, anchor="w", bg=rgb_to_hex(COLORS["panel2"]), fg=rgb_to_hex(COLORS["muted"]), font=("Avenir", 10)).pack(fill=tk.X, padx=10)
        tk.Label(meta_box, textvariable=self.duration_var, anchor="w", bg=rgb_to_hex(COLORS["panel2"]), fg=rgb_to_hex(COLORS["muted"]), font=("Avenir", 10)).pack(fill=tk.X, padx=10, pady=(0, 8))

        tk.Label(self.left, text="Download Progress", bg=rgb_to_hex(COLORS["panel"]), fg=rgb_to_hex(COLORS["title"]), font=("Avenir", 11, "bold")).pack(anchor="w")
        ttk.Progressbar(self.left, variable=self.progress_var, mode="determinate", maximum=100).pack(fill=tk.X, pady=(6, 2))
        tk.Label(self.left, textvariable=self.status_var, anchor="w", bg=rgb_to_hex(COLORS["panel"]), fg=rgb_to_hex(COLORS["muted"]), font=("Avenir", 10, "bold")).pack(fill=tk.X)

        tk.Label(self.left, text="Queue", bg=rgb_to_hex(COLORS["panel"]), fg=rgb_to_hex(COLORS["title"]), font=("Avenir", 11, "bold")).pack(anchor="w", pady=(10, 4))
        self.queue_box = tk.Listbox(self.left, height=8, bg=rgb_to_hex(COLORS["panel2"]), fg=rgb_to_hex(COLORS["text"]), relief=tk.FLAT, font=("Menlo", 10))
        self.queue_box.pack(fill=tk.BOTH, expand=True)

    def _build_right(self):
        tk.Label(
            self.right,
            text="History",
            bg=rgb_to_hex(COLORS["panel2"]),
            fg=rgb_to_hex(COLORS["title"]),
            font=("Avenir", 16, "bold"),
        ).pack(anchor="w", padx=12, pady=(10, 8))

        self.history_box = tk.Listbox(
            self.right,
            height=22,
            bg=rgb_to_hex(COLORS["panel"]),
            fg=rgb_to_hex(COLORS["text"]),
            relief=tk.FLAT,
            font=("Menlo", 9),
        )
        self.history_box.pack(fill=tk.BOTH, expand=True, padx=12)

        foot = tk.Frame(self.right, bg=rgb_to_hex(COLORS["panel2"]))
        foot.pack(fill=tk.X, pady=10, padx=12)
        CustomButton(foot, "Run Queue", COLORS["accent2"], (35, 141, 214), self.run_queue, width=118, height=36).pack(side=tk.LEFT)
        CustomButton(foot, "Clear", COLORS["bad"], (216, 84, 84), self._clear_history, width=96, height=36).pack(side=tk.LEFT, padx=(8, 0))

    def _pick_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.path_var.set(folder)

    def _clear_fields(self):
        self.url_var.set("")
        self.title_var.set("Title: --")
        self.author_var.set("Channel: --")
        self.duration_var.set("Duration: --")
        self.progress_var.set(0)
        self.status_var.set("Ready")

    def _clear_history(self):
        self.history.clear()
        self._sync_history()

    def _sync_history(self):
        self.history_box.delete(0, tk.END)
        for item in self.history:
            self.history_box.insert(tk.END, item)

    def _valid_url(self, text):
        return bool(re.search(r"(youtube\.com/watch\?v=|youtu\.be/)", text))

    def analyze_url(self):
        url = self.url_var.get().strip()
        if not self._valid_url(url):
            messagebox.showerror("Invalid URL", "Enter a valid YouTube watch URL or youtu.be URL")
            return
        if YouTube is None:
            messagebox.showerror("Dependency Missing", "pytube is not installed in this environment")
            return

        self.status_var.set("Analyzing stream metadata...")

        def worker():
            try:
                yt = YouTube(url)
                quality_entries = ["Highest"]
                quality_map = {"Highest": None}
                for s in yt.streams.filter(progressive=True, file_extension="mp4").order_by("resolution").desc():
                    label = f"{s.resolution} | {s.fps}fps"
                    if label not in quality_map:
                        quality_map[label] = s.itag
                        quality_entries.append(label)

                duration_s = int(yt.length)
                mm = duration_s // 60
                ss = duration_s % 60
                payload = {
                    "title": yt.title,
                    "author": yt.author,
                    "duration": f"{mm:02d}:{ss:02d}",
                    "qualities": quality_entries,
                    "quality_map": quality_map,
                }
                self.pending.put(("analyze_ok", payload))
            except Exception as exc:
                err = str(exc)
                if "HTTP Error 400" in err:
                    err += " | YouTube request was rejected. Try Analyze again or switch Mode/Quality."
                self.pending.put(("error", f"Analyze failed: {err}"))

        threading.Thread(target=worker, daemon=True).start()

    def queue_download(self):
        url = self.url_var.get().strip()
        if not self._valid_url(url):
            messagebox.showerror("Invalid URL", "Enter a valid YouTube URL")
            return
        self.queue_box.insert(tk.END, url)
        self.status_var.set("Added to queue")

    def run_queue(self):
        if self.is_downloading:
            messagebox.showinfo("Busy", "A download is already running")
            return
        if self.queue_box.size() == 0:
            messagebox.showinfo("Queue", "No queued links")
            return

        next_url = self.queue_box.get(0)
        self.queue_box.delete(0)
        self.url_var.set(next_url)
        self.start_download(from_queue=True)

    def start_download(self, from_queue=False):
        if self.is_downloading:
            messagebox.showinfo("Busy", "A download is already in progress")
            return

        url = self.url_var.get().strip()
        path = self.path_var.get().strip()

        if not self._valid_url(url):
            messagebox.showerror("Invalid URL", "Enter a valid YouTube URL")
            return
        if not path or not os.path.isdir(path):
            messagebox.showerror("Invalid Folder", "Choose a valid save folder")
            return
        if YouTube is None:
            messagebox.showerror("Dependency Missing", "pytube is not installed in this environment")
            return

        self.is_downloading = True
        self.progress_var.set(0)
        self.status_var.set("Starting download...")

        mode = self.mode_var.get()
        quality_label = self.quality_var.get().strip() or "Highest"

        def on_progress(_stream, chunk, bytes_remaining):
            del chunk
            total = getattr(_stream, "filesize", 0) or 0
            if total <= 0:
                return
            done = total - bytes_remaining
            pct = max(0.0, min(100.0, done * 100.0 / total))
            self.pending.put(("progress", pct))

        def worker():
            try:
                yt = YouTube(url, on_progress_callback=on_progress)
                if mode == "audio":
                    stream = yt.streams.filter(only_audio=True).order_by("abr").desc().first()
                else:
                    if quality_label in self.quality_map and self.quality_map[quality_label] is not None:
                        stream = yt.streams.get_by_itag(self.quality_map[quality_label])
                    else:
                        stream = yt.streams.filter(progressive=True, file_extension="mp4").order_by("resolution").desc().first()

                if stream is None:
                    raise RuntimeError("No stream found for current mode/quality")

                out_file = stream.download(output_path=path)
                size_mb = os.path.getsize(out_file) / (1024 * 1024)
                self.pending.put(("download_ok", {
                    "title": yt.title,
                    "path": out_file,
                    "size": size_mb,
                    "queue": from_queue,
                }))
            except Exception as exc:
                err = str(exc)
                if "HTTP Error 400" in err:
                    err += " | Source stream request rejected. Re-run Analyze and choose another quality."
                self.pending.put(("error", f"Download failed: {err}"))

        threading.Thread(target=worker, daemon=True).start()

    def _pump_events(self):
        try:
            while True:
                kind, payload = self.pending.get_nowait()
                if kind == "progress":
                    self.progress_var.set(payload)
                    self.status_var.set(f"Downloading... {payload:0.1f}%")
                elif kind == "analyze_ok":
                    self.title_var.set(f"Title: {payload['title']}")
                    self.author_var.set(f"Channel: {payload['author']}")
                    self.duration_var.set(f"Duration: {payload['duration']}")
                    self.quality_map = payload["quality_map"]
                    self.quality_box["values"] = payload["qualities"]
                    self.quality_var.set(payload["qualities"][0])
                    self.status_var.set("Analysis complete")
                elif kind == "download_ok":
                    self.is_downloading = False
                    self.progress_var.set(100)
                    now = dt.datetime.now().strftime("%H:%M:%S")
                    row = f"{now} | {payload['title'][:36]} | {payload['size']:.1f} MB"
                    self.history.insert(0, row)
                    self.history = self.history[:80]
                    self._sync_history()
                    self.status_var.set("Download complete")

                    if payload["queue"] and self.queue_box.size() > 0:
                        self.run_queue()
                elif kind == "error":
                    self.is_downloading = False
                    self.status_var.set("Operation failed")
                    messagebox.showerror("Error", payload)
        except queue.Empty:
            pass

        self.root.after(120, self._pump_events)


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

    DownloadStudio(root)
    root.mainloop()


if __name__ == "__main__":
    main()