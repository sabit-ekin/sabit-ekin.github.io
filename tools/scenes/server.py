"""Serve the scene pages and save rendered PNGs posted to /save/<name>.png into ./out/."""
import http.server, os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'out')
os.makedirs(OUT, exist_ok=True)


class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=ROOT, **k)

    def do_POST(self):
        m = re.fullmatch(r'/save/([\w-]+)\.png', self.path)
        if not m:
            self.send_error(404); return
        n = int(self.headers.get('Content-Length', 0))
        if n > 20_000_000:
            self.send_error(413); return
        data = self.rfile.read(n)
        if not data.startswith(b'\x89PNG'):
            self.send_error(400, 'not a PNG'); return
        with open(os.path.join(OUT, m.group(1) + '.png'), 'wb') as f:
            f.write(data)
        self.send_response(200); self.end_headers(); self.wfile.write(b'saved')

    def log_message(self, *a):
        pass


port = int(sys.argv[1]) if len(sys.argv) > 1 else 8793
http.server.ThreadingHTTPServer(('127.0.0.1', port), H).serve_forever()
