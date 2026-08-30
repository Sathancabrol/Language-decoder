"""
Language-decoder — Static UI + engine API server
================================================

Serves the `ui/` directory and exposes a couple of tiny JSON endpoints so the
interface can read the latest decoded profile and re-trigger a decode by text.

    python -m language_decoder serve --port 9000

Endpoints:
    GET  /                      -> ui/index.html
    GET  /data/profile.json     -> latest DecodedHuman
    POST /api/decode            -> {text, title, person, year} -> DecodedHuman JSON

Binds 0.0.0.0 so the preview environment can reach it; accepts the generated
preview hostname (allowedHosts on the dev server side).
"""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from .profile import decode_human

UI_ROOT = Path(__file__).resolve().parent.parent / "ui"
DATA_PATH = UI_ROOT / "data" / "profile.json"

MIME = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".svg": "image/svg+xml",
    ".png": "image/png",
    ".md": "text/plain; charset=utf-8",
}


class Handler(BaseHTTPRequestHandler):
    server_version = "LanguageDecoder/0.1"

    def _send(self, code: int, body: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json(self, payload: dict, code: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self._send(code, body, "application/json; charset=utf-8")

    def do_GET(self) -> None:  # noqa: N802
        path = self.path.split("?")[0]
        if path == "/data/profile.json":
            if DATA_PATH.exists():
                self._send(200, DATA_PATH.read_bytes(), "application/json; charset=utf-8")
            else:
                self._json({"error": "No profile yet. Run: python -m language_decoder decode …"},
                           code=404)
            return
        if path == "/api/health":
            self._json({"ok": True, "version": "0.1.0"})
            return
        # static file
        rel = path.lstrip("/") or "index.html"
        target = (UI_ROOT / rel).resolve()
        # prevent path traversal
        if not str(target).startswith(str(UI_ROOT.resolve())):
            self._send(403, b"Forbidden", "text/plain")
            return
        if target.is_file():
            self._send(200, target.read_bytes(), MIME.get(target.suffix, "application/octet-stream"))
        else:
            # SPA-ish fallback to index.html for unknown routes
            index = UI_ROOT / "index.html"
            if index.exists():
                self._send(200, index.read_bytes(), "text/html; charset=utf-8")
            else:
                self._send(404, b"Not found", "text/plain")

    def do_POST(self) -> None:  # noqa: N802
        if self.path.startswith("/api/decode"):
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length) if length else b"{}"
            try:
                body = json.loads(raw)
            except json.JSONDecodeError:
                self._json({"error": "Invalid JSON"}, code=400)
                return
            profile = decode_human(
                text=body.get("text", ""),
                items=body.get("items"),
                ai_json=body.get("ai_json", ""),
                source_title=body.get("title", "Décodage humain"),
                person_id=body.get("person", "h-001"),
                current_year=body.get("year", 2026),
            )
            DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
            DATA_PATH.write_text(profile.to_json(), encoding="utf-8")
            self._json(profile.as_dict())
            return
        self._json({"error": "Unknown endpoint"}, code=404)

    def log_message(self, fmt: str, *args) -> None:  # silence default logging
        return


def serve(port: int = 9000) -> None:
    httpd = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"Language-decoder UI served on http://0.0.0.0:{port}  (bind 0.0.0.0)")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()


if __name__ == "__main__":
    serve()
