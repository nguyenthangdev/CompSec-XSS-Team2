# demo.js host server

A minimal, isolated HTTP server that plays the role of the **external web
server** in the XSS lab: the Elgg Brief Description field stores only a short
`<script src=…>` reference, and the browser fetches the real script (`demo.js`)
from here.

## Run

```bash
# from the repo root
python3 exploit.py serve                      # binds 127.0.0.1:8000, serves this dir
# or directly
python3 -m src.js_server.server --host 127.0.0.1 --port 8000
```

Then:

```bash
curl -i http://127.0.0.1:8000/health          # JSON: {"status":"ok", "resource_available":true,...}
curl -I http://127.0.0.1:8000/demo.js         # Content-Type: application/javascript; charset=utf-8
curl -i http://127.0.0.1:8000/missing.js      # 404 JSON
```

## Features

- `/health` (and `/healthz`) JSON endpoint — used by `exploit.py --check` and tests.
- Correct JavaScript MIME: `application/javascript; charset=utf-8`.
- Per-request access logging to stdout and (optionally) `--log-file`.
- Proper `404` for missing resources; `403` for path traversal attempts.
- Binds to **loopback by default**. Use `--host 10.9.0.1` (or your lab interface)
  only if the browser runs in a separate VM that must reach this server.

## The script it serves: `demo.js`

`demo.js` is deliberately **harmless**. It shows a banner, pops one `alert`, and
records a local in-page event. It does **not** modify any account, send friend
requests, propagate, or read cookies/tokens. It exists only to prove that an
externally-referenced script executes in the Elgg origin.

To suppress the `alert()` (e.g. for automated screenshots), set
`window.XSS_LAB_NO_ALERT = true` before the script loads; the banner still shows.

## Reachability from the Elgg browser

The browser that renders Elgg fetches `demo.js`. If that browser runs on the
**host**, `http://localhost:8000/demo.js` works. Because Elgg is served over
plain HTTP, loading an `http://` script is **not** blocked as mixed content.
