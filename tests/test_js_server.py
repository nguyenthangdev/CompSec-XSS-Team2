"""Integration tests for the external demo.js hosting server."""

from __future__ import annotations

import json
import urllib.error
import urllib.request

import pytest

from src.js_server.server import guess_mime


def _get(url: str):
    req = urllib.request.Request(url, method="GET")
    return urllib.request.urlopen(req, timeout=5)


def test_mime_mapping_for_javascript():
    assert guess_mime("demo.js") == "application/javascript; charset=utf-8"
    assert guess_mime("/path/to/x.JS") == "application/javascript; charset=utf-8"
    assert guess_mime("note.txt") == "text/plain; charset=utf-8"
    assert guess_mime("blob.bin") == "application/octet-stream"


def test_health_endpoint_returns_ok_json(running_js_server):
    with _get(running_js_server + "/health") as resp:
        assert resp.status == 200
        assert resp.headers.get("Content-Type", "").startswith("application/json")
        data = json.loads(resp.read().decode("utf-8"))
    assert data["status"] == "ok"
    assert data["resource"] == "demo.js"
    assert data["resource_available"] is True


def test_demo_js_served_with_correct_content_type(running_js_server):
    with _get(running_js_server + "/demo.js") as resp:
        assert resp.status == 200
        ctype = resp.headers.get("Content-Type", "")
        assert ctype == "application/javascript; charset=utf-8"
        body = resp.read().decode("utf-8")
    # The served script is the harmless PoC, not a worm.
    assert "HARMLESS" in body
    assert "demo.js" in body
    assert "self-propagation" in body.lower()


def test_missing_resource_returns_404(running_js_server):
    with pytest.raises(urllib.error.HTTPError) as exc_info:
        _get(running_js_server + "/does-not-exist.js")
    assert exc_info.value.code == 404


def test_path_traversal_is_rejected(running_js_server):
    with pytest.raises(urllib.error.HTTPError) as exc_info:
        _get(running_js_server + "/../../etc/passwd")
    # Normalised traversal maps back inside the dir and 404s, or is forbidden.
    assert exc_info.value.code in (403, 404)


def test_server_unavailable_connection_refused():
    # Nothing is listening on this loopback port -> connection refused.
    with pytest.raises(urllib.error.URLError):
        _get("http://127.0.0.1:1/health")  # port 1 is privileged/closed


def test_health_reports_resource_missing_when_dir_empty(tmp_path):
    from src.js_server import server as js_server

    httpd, thread = js_server.start_in_background(host="127.0.0.1", port=0, directory=str(tmp_path))
    try:
        host, port = httpd.server_address
        with _get(f"http://{host}:{port}/health") as resp:
            data = json.loads(resp.read().decode("utf-8"))
        assert data["resource_available"] is False
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=5)
