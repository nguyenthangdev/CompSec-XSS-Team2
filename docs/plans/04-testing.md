# Plan 04 — Automated Testing

## Objective
Verify every testable component with real, reproducible automated tests, and
save the real output as evidence.

## Tasks
1. Unit tests: payload validator (empty/valid/250/251/Unicode/NFC/invalid).
2. Integration tests: JS server (health, JS MIME, 404, traversal, unavailable).
3. Config/allow-list tests (lab targets allowed, public refused).
4. CLI tests (`validate-payload`, `check`, `report`, public-host rejection).
5. Optional: Playwright browser check of `demo.js` execution if the env supports it.
6. Run, inspect failures, fix real defects, re-run, save output.

## Dependencies
- `pytest` (present). Playwright optional (`npx playwright`).

## Acceptance criteria
- `python3 -m pytest tests/` is green; output saved to
  `docs/evidence/logs/pytest-output.txt`.
- No fabricated results; unreachable services reported as such.

## Tests
- The suite itself (44 cases at time of writing).

## Expected evidence
- `docs/evidence/logs/pytest-output.txt`.

## Proposed Git commit
`test: automated suite for validator, server, config, and CLI`
