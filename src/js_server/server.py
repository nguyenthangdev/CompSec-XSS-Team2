#!/usr/bin/env python3
"""Minimal, isolated HTTP server for hosting the demonstration JavaScript.

This server plays the role of the "external web server" in the lab: the Elgg
Brief Description field stores only a short ``<script src=...>`` reference, and
the browser fetches the actual script (``demo.js``) from here.

Features
--------
* ``/health`` endpoint returning JSON (used by ``exploit.py --check`` and tests).
* Correct JavaScript MIME type (``application/javascript; charset=utf-8``).
* Per-request access logging to stdout and (optionally) a log file.
* Proper ``404`` handling for missing resources.
* Path-traversal protection — only files inside the served directory are returned.
* Binds to ``127.0.0.1`` by default (loopback only). Use ``--host`` to expose it
  on a specific lab interface if the browser runs in a separate VM.

The script it serves (``demo.js``) is intentionally **harmless**: it shows a
visual banner and records a local, in-page demonstration event. It performs no
account modification, sends no friend request, and exfiltrates nothing.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import posixpath
import sys
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlparse

DEFAULT_DIR = os.path.dirname(os.path.abspath(__file__))

#: Explicit MIME overrides (do not rely on the platform mimetypes database,
#: which has historically returned text/plain or application/x-javascript for .js).
_MIME_BY_EXT = {
    ".js": "application/javascript; charset=utf-8",
    ".mjs": "application/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".html": "text/html; charset=utf-8",
    ".htm": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".txt": "text/plain; charset=utf-8",
    ".map": "application/json; charset=utf-8",
}


def guess_mime(path: str) -> str:
    _, ext = os.path.splitext(path)
    return _MIME_BY_EXT.get(ext.lower(), "application/octet-stream")


class DemoJSRequestHandler(BaseHTTPRequestHandler):
    """Serves static files from ``self.directory`` plus a ``/health`` endpoint."""

    server_version = "DemoJSHost/1.0"
    protocol_version = "HTTP/1.1"

    # Set per-server (see build_server).
    directory: str = DEFAULT_DIR
    log_file_path: str | None = None

    # -- logging ----------------------------------------------------------
    def log_message(self, fmt: str, *args) -> None:  # noqa: A003 (name from base class)
        stamp = _dt.datetime.now().isoformat(timespec="seconds")
        line = f"{stamp} {self.address_string()} {fmt % args}"
        sys.stdout.write(line + "\n")
        sys.stdout.flush()
        if self.log_file_path:
            try:
                with open(self.log_file_path, "a", encoding="utf-8") as fh:
                    fh.write(line + "\n")
            except OSError:
                pass  # logging must never crash the server

    # -- routing ----------------------------------------------------------
    def do_GET(self) -> None:  # noqa: N802 (name from base class)
        parsed = urlparse(self.path)
        route = parsed.path
        if route in ("/health", "/healthz"):
            return self._handle_health()
        if route in ("/", ""):
            route = "/index.html"
        return self._serve_file(route)

    def do_HEAD(self) -> None:  # noqa: N802
        # Serve headers only (used by some availability checks).
        parsed = urlparse(self.path)
        if parsed.path in ("/health", "/healthz"):
            body = self._health_body()
            self._send_headers(HTTPStatus.OK, "application/json; charset=utf-8", len(body))
            return
        self._serve_file(parsed.path, head_only=True)

    # -- handlers ---------------------------------------------------------
    def _health_body(self) -> bytes:
        resource = os.path.join(self.directory, "demo.js")
        payload = {
            "status": "ok",
            "server": self.server_version,
            "directory": self.directory,
            "resource": "demo.js",
            "resource_available": os.path.isfile(resource),
            "time": _dt.datetime.now().isoformat(timespec="seconds"),
        }
        return json.dumps(payload, ensure_ascii=False).encode("utf-8")

    def _handle_health(self) -> None:
        body = self._health_body()
        self._send_headers(HTTPStatus.OK, "application/json; charset=utf-8", len(body))
        self.wfile.write(body)

    def _resolve_safe_path(self, url_path: str) -> str | None:
        """Map a URL path to a filesystem path inside ``self.directory``.

        Returns ``None`` if the request escapes the served directory.
        """
        clean = posixpath.normpath(unquote(url_path))
        # Reject absolute-after-normalization traversal.
        parts = [p for p in clean.split("/") if p not in ("", ".", "..")]
        candidate = os.path.join(self.directory, *parts)
        base = os.path.realpath(self.directory)
        real = os.path.realpath(candidate)
        if real != base and not real.startswith(base + os.sep):
            return None
        return real

    def _serve_file(self, url_path: str, head_only: bool = False) -> None:
        fs_path = self._resolve_safe_path(url_path)
        if fs_path is None:
            return self._send_error(HTTPStatus.FORBIDDEN, "path traversal rejected")
        if not os.path.isfile(fs_path):
            return self._send_error(HTTPStatus.NOT_FOUND, f"resource not found: {url_path}")

        try:
            with open(fs_path, "rb") as fh:
                data = fh.read()
        except OSError as exc:
            return self._send_error(HTTPStatus.INTERNAL_SERVER_ERROR, f"read error: {exc}")

        self._send_headers(HTTPStatus.OK, guess_mime(fs_path), len(data))
        if not head_only:
            self.wfile.write(data)

    # -- low-level helpers ------------------------------------------------
    def _send_headers(self, status: HTTPStatus, content_type: str, length: int) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(length))
        # Make it obvious in DevTools that this is the isolated lab host.
        self.send_header("X-Lab-Server", "demo-js-host")
        # No caching, so re-tests always hit the server (visible in access log).
        self.send_header("Cache-Control", "no-store")
        self.end_headers()

    def _send_error(self, status: HTTPStatus, message: str) -> None:
        body = json.dumps({"error": status.phrase, "detail": message}).encode("utf-8")
        self._send_headers(status, "application/json; charset=utf-8", len(body))
        self.wfile.write(body)


def build_server(
    host: str = "127.0.0.1",
    port: int = 8000,
    directory: str = DEFAULT_DIR,
    log_file_path: str | None = None,
) -> ThreadingHTTPServer:
    """Construct (but do not start) a ThreadingHTTPServer serving *directory*.

    Pass ``port=0`` to let the OS pick a free port (used by the test-suite);
    read the chosen port back from ``server.server_address[1]``.
    """

    handler = type(
        "BoundDemoJSRequestHandler",
        (DemoJSRequestHandler,),
        {"directory": os.path.abspath(directory), "log_file_path": log_file_path},
    )
    return ThreadingHTTPServer((host, port), handler)


def serve_forever(host: str, port: int, directory: str, log_file_path: str | None = None) -> None:
    httpd = build_server(host, port, directory, log_file_path)
    bound_host, bound_port = httpd.server_address[0], httpd.server_address[1]
    print(f"[demo-js-host] serving {os.path.abspath(directory)}")
    print(f"[demo-js-host] listening on http://{bound_host}:{bound_port}")
    print(f"[demo-js-host] health:   http://{bound_host}:{bound_port}/health")
    print(f"[demo-js-host] resource: http://{bound_host}:{bound_port}/demo.js")
    print("[demo-js-host] press Ctrl+C to stop")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[demo-js-host] shutting down")
    finally:
        httpd.server_close()


def start_in_background(
    host: str = "127.0.0.1", port: int = 0, directory: str = DEFAULT_DIR
) -> tuple[ThreadingHTTPServer, threading.Thread]:
    """Start the server on a background thread; return (server, thread).

    Convenience helper for tests. Stop with ``server.shutdown()``.
    """
    httpd = build_server(host, port, directory)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd, thread


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="demo-js-host",
        description="Isolated HTTP server that hosts the harmless demo.js for the XSS lab.",
    )
    parser.add_argument("--host", default="127.0.0.1", help="bind address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="bind port (default: 8000)")
    parser.add_argument(
        "--dir",
        default=DEFAULT_DIR,
        help="directory to serve (default: the js_server directory containing demo.js)",
    )
    parser.add_argument("--log-file", default=None, help="append access log to this file as well")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    serve_forever(args.host, args.port, args.dir, args.log_file)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
