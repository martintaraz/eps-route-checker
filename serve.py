#!/usr/bin/env python3
"""Dev server for the EPS Route-Checker.

Serves the static files AND reverse-proxies /valhalla/* to a local Valhalla
instance (default http://localhost:8002). This keeps the routing API same-origin,
so the browser never hits a CORS wall (Valhalla itself sends no CORS headers).

    python3 serve.py            # http://localhost:8000
    python3 serve.py 9000       # custom port
    VALHALLA=http://localhost:8002 python3 serve.py

No network downloads. Requires Valhalla running only for the detour feature;
everything else works without it.
"""
import os, sys, urllib.request, urllib.error
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
VALHALLA = os.environ.get("VALHALLA", "http://localhost:8002").rstrip("/")
PREFIX = "/valhalla/"


class Handler(SimpleHTTPRequestHandler):
    def _proxy(self, body=None):
        target = VALHALLA + "/" + self.path[len(PREFIX):]
        req = urllib.request.Request(target, data=body, method=self.command)
        req.add_header("Content-Type", "application/json")
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
            msg = ('{"error":"valhalla unreachable: %s"}' % e).encode()
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(msg)))
            self.end_headers()
            self.wfile.write(msg)

    def do_GET(self):
        if self.path.startswith(PREFIX):
            return self._proxy()
        return super().do_GET()

    def do_POST(self):
        if self.path.startswith(PREFIX):
            length = int(self.headers.get("Content-Length", 0))
            return self._proxy(self.rfile.read(length) if length else None)
        self.send_error(404)


if __name__ == "__main__":
    print(f"Serving http://localhost:{PORT}  (proxying {PREFIX}* -> {VALHALLA})")
    ThreadingHTTPServer(("", PORT), Handler).serve_forever()
