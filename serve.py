#!/usr/bin/env python3
"""Dev server for the EPS Route-Checker.

Serves the static files, reverse-proxies /api/* to the local share backend
(default http://localhost:8080), and falls back to index.html for /<uuid> share
links — mirroring the production nginx config so sharing works locally.

    python3 backend/app.py &        # start the share backend on :8080
    python3 serve.py                # http://localhost:8000
    python3 serve.py 9000           # custom port
    BACKEND=http://localhost:8080 python3 serve.py
"""
import os, re, sys, urllib.request, urllib.error
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
BACKEND = os.environ.get("BACKEND", "http://localhost:8080").rstrip("/")
UUID_RE = re.compile(r"^/[0-9a-fA-F-]{36}$")


class Handler(SimpleHTTPRequestHandler):
    def _proxy(self, body=None):
        req = urllib.request.Request(BACKEND + self.path, data=body, method=self.command)
        req.add_header("Content-Type", self.headers.get("Content-Type", "application/json"))
        try:
            with urllib.request.urlopen(req, timeout=30) as up:
                data = up.read()
                self.send_response(up.status)
                self.send_header("Content-Type", up.headers.get("Content-Type", "application/json"))
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
        except urllib.error.HTTPError as e:
            data = e.read()
            self.send_response(e.code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            msg = ('{"error":"backend unreachable: %s"}' % e).encode()
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(msg)))
            self.end_headers()
            self.wfile.write(msg)

    def do_GET(self):
        if self.path.startswith("/api/"):
            return self._proxy()
        if UUID_RE.match(self.path):          # /<uuid> share link -> serve the app
            self.path = "/eps-checker.html"
        return super().do_GET()

    def do_POST(self):
        if self.path.startswith("/api/"):
            length = int(self.headers.get("Content-Length", 0))
            return self._proxy(self.rfile.read(length) if length else None)
        self.send_error(404)


if __name__ == "__main__":
    print(f"Serving http://localhost:{PORT}  (proxying /api/* -> {BACKEND})")
    ThreadingHTTPServer(("", PORT), Handler).serve_forever()
