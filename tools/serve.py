"""Local preview server that mimics Vercel cleanUrls: /products/fans -> products/fans.html.

Run: python tools/serve.py   (serves the repo root on http://localhost:8000)
"""
import os, pathlib
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = pathlib.Path(__file__).resolve().parent.parent

class Handler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        p = super().translate_path(path)
        return p + ".html" if not os.path.exists(p) and os.path.exists(p + ".html") else p

ThreadingHTTPServer(("", 8000), partial(Handler, directory=str(ROOT))).serve_forever()
