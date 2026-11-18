"""Shared pytest fixtures and path setup."""

from __future__ import annotations

import os
import sys

import pytest

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from src.js_server import server as js_server  # noqa: E402


@pytest.fixture()
def running_js_server():
    """Start the demo.js server on an ephemeral loopback port for the test.

    Yields the base URL (e.g. ``http://127.0.0.1:54321``) and shuts the server
    down afterwards.
    """
    httpd, thread = js_server.start_in_background(host="127.0.0.1", port=0)
    host, port = httpd.server_address[0], httpd.server_address[1]
    base_url = f"http://{host}:{port}"
    try:
        yield base_url
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=5)
