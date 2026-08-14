#!/usr/bin/env python3
"""Minimal share backend for the EPS Route-Checker.

Stores an uploaded GPX under a random UUID and serves it back, so a route (and the
findings the frontend recomputes from it) can be shared via eps-route-checker.<host>/<uuid>.

    POST /api/routes        body = GPX text          -> {"uuid": "..."}
    GET  /api/routes/<uuid>                           -> the GPX text
    GET  /api/health                                  -> {"ok": true}

Dependency-free (Python stdlib). GPX files are written to DATA_DIR (default /data),
which should be a mounted volume so shared routes survive restarts.
"""
import json, os, re, uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

DATA_DIR = os.environ.get("DATA_DIR", "/data")
PORT = int(os.environ.get("PORT", "8080"))
MAX_BYTES = 3 * 1024 * 1024          # 3 MB cap per upload
UUID_RE = re.compile(r"^[0-9a-fA-F-]{36}$")

os.makedirs(DATA_DIR, exist_ok=True)


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _send(self, code, body, ctype="application/json"):
        if isinstance(body, (dict, list)):
            body = json.dumps(body).encode()
        elif isinstance(body, str):
            body = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/api/health":
            return self._send(200, {"ok": True})
        m = re.match(r"^/api/routes/([^/?]+)$", self.path)
        if m:
            rid = m.group(1)
            if not UUID_RE.match(rid):
                return self._send(400, {"error": "bad id"})
            fp = os.path.join(DATA_DIR, rid + ".gpx")
            if not os.path.isfile(fp):
                return self._send(404, {"error": "not found"})
            with open(fp, "rb") as f:
                return self._send(200, f.read(), "application/gpx+xml")
        return self._send(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/api/routes":
            return self._send(404, {"error": "not found"})
        length = int(self.headers.get("Content-Length", 0))
        if length <= 0 or length > MAX_BYTES:
            return self._send(413, {"error": "empty or too large"})
        body = self.rfile.read(length)
        if b"<gpx" not in body.lower():
            return self._send(400, {"error": "not a GPX file"})
        rid = str(uuid.uuid4())
        with open(os.path.join(DATA_DIR, rid + ".gpx"), "wb") as f:
            f.write(body)
        return self._send(200, {"uuid": rid})

    def log_message(self, *args):
        pass  # quiet


if __name__ == "__main__":
    print(f"EPS share backend on :{PORT}, storing GPX in {DATA_DIR}", flush=True)
    ThreadingHTTPServer(("", PORT), Handler).serve_forever()
