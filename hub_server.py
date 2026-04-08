import json
import os
import subprocess
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


ROOT = Path(__file__).resolve().parent
HOST = "127.0.0.1"
PORT = 8765
PYTHON = ROOT / ".venv" / "bin" / "python"

ALLOWED = {
    "aim_finder.py",
    "path_finder.py",
    "NBA_data.py",
    "slot_machine.py",
    "turtlerace.py",
    "quiz_game.py",
    "number_guessing.py",
    "rockpaperscissor.py",
    "PIG.py",
    "time_math_challenge.py",
    "timer_clock.py",
    "madlibs.py",
    "choose_adv.py",
    "tying_test.py",
    "password_generator.py",
    "password_manager.py",
    "currency_convert.py",
    "youtube_download.py",
}


class HubHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def _send_json(self, code, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path != "/api/run":
            self._send_json(404, {"error": "Not found"})
            return

        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"

        try:
            data = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            self._send_json(400, {"error": "Invalid JSON"})
            return

        file_name = str(data.get("file", "")).strip()
        if file_name not in ALLOWED:
            self._send_json(400, {"error": "File not allowed"})
            return

        target = ROOT / file_name
        if not target.exists() or not target.is_file():
            self._send_json(404, {"error": "File not found"})
            return

        python_exec = str(PYTHON if PYTHON.exists() else Path(os.sys.executable))

        try:
            subprocess.Popen(
                [python_exec, str(target)],
                cwd=str(ROOT),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                start_new_session=True,
            )
        except Exception as exc:
            self._send_json(500, {"error": f"Launch failed: {exc}"})
            return

        self._send_json(200, {"ok": True, "file": file_name})


def main():
    server = ThreadingHTTPServer((HOST, PORT), HubHandler)
    print(f"Hub server running: http://{HOST}:{PORT}/game_hub.html")
    server.serve_forever()


if __name__ == "__main__":
    main()
