# Plan 03 — JavaScript Hosting, Validator & Verification CLI

## Objective
Provide the isolated infrastructure: an HTTP server hosting the harmless
`demo.js`, a payload-length validator, and the safe `exploit.py` verification CLI.

## Tasks
1. `src/js_server/server.py`: `/health`, correct JS MIME, access logging, 404,
   path-traversal guard, loopback bind by default.
2. `src/js_server/demo.js`: harmless banner + local event only (no account ops).
3. `src/payload_validator/validator.py`: measure code points vs UTF-8 bytes,
   validate the 250 limit, CLI + library API.
4. `src/lab_config.py`: central config + target allow-list (loopback + lab CIDR).
5. `exploit.py`: `--check/--serve/--validate-payload/--test/--report`, allow-list
   enforced, no account modification.

## Dependencies
- Python 3.13 stdlib only (no third-party runtime deps).

## Acceptance criteria
- `curl http://127.0.0.1:8000/demo.js` returns the script with
  `application/javascript; charset=utf-8`.
- `/health` returns JSON with `resource_available: true`.
- `exploit.py --check` prints real PASS/FAIL per service.
- Public targets are refused by the allow-list.

## Tests
- `tests/test_js_server.py`, `tests/test_lab_config.py`, `tests/test_exploit_cli.py`.

## Expected evidence
- `docs/evidence/logs/js-server-access.log`, `verification-report.md`.

## Proposed Git commit
`feat(infra): demo.js host server, payload validator, safe verification CLI`
