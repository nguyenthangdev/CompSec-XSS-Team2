# Evidence Index

Two kinds of evidence live here:

1. **Captured automatically (real, already here).** Command output and logs
   produced by running the tooling.
2. **Pending manual capture (team).** Screenshots that require a human driving a
   browser against the running Elgg lab. These are **not** faked — until a
   teammate captures them, they stay on the checklist below.

> Rule: a diagram or illustration is **never** labelled as experimental evidence.
> Only real screenshots/logs count.

## 1. Captured automatically (present in this repo)

| File | What it shows |
|---|---|
| [`logs/pytest-output.txt`](logs/pytest-output.txt) | Real run of the 44-test suite (all passing) |
| [`logs/js-server-access.log`](logs/js-server-access.log) | Access log of the demo.js server (health/demo.js/404 requests) |
| [`logs/js-server-stdout.log`](logs/js-server-stdout.log) | Server startup banner + per-request log lines |
| [`verification-report.md`](verification-report.md) | `exploit.py --report` output (live probe results) |
| [`verification-report.json`](verification-report.json) | Same, machine-readable |

Regenerate any of these:

```bash
python3 -m pytest tests/ -v | tee docs/evidence/logs/pytest-output.txt
python3 exploit.py --report --json
```

## 2. Pending manual screenshots (team captures against the live lab)

Save PNGs under `docs/evidence/screenshots/` using the suggested names. Capture
them once the Elgg lab is up (`elgg-lab/README.md`) and the demo.js server is
running (`python3 exploit.py serve`).

- [ ] `01-elgg-login.png` — Elgg login page at http://localhost:8080
- [ ] `02-samy-profile.png` — Samy's profile page
- [ ] `03-brief-description-field.png` — the Brief Description edit field (show the 250 maxlength)
- [ ] `04-payload-validation.png` — terminal running `exploit.py validate-payload …` (PASS and FAIL)
- [ ] `05-js-server-terminal.png` — `exploit.py serve` running with access-log lines
- [ ] `06-demo-js-resource.png` — browser/`curl` showing demo.js content + `application/javascript` type
- [ ] `07-network-tab.png` — DevTools Network showing the external GET for demo.js
- [ ] `08-xss-execution.png` — the harmless banner/alert firing on the profile
- [ ] `09-cross-account.png` — Alice viewing Samy's profile and seeing the same banner
- [ ] `10-aboutme-before.png` / `11-aboutme-after.png` — About me before/after a **manual** edit
- [ ] `12-friends-before.png` / `13-friends-after.png` — friends list before/after a **manual** add-friend
- [ ] `14-devtools-editprofile.png` — DevTools showing a **manual** `/action/profile/edit` POST (cookie/token blurred)
- [ ] `15-pytest-results.png` — the test run in a terminal

### Screenshot hygiene

- **Blur/redact** any session cookie (`Elgg=…`) and `__elgg_token` value before
  saving a Network screenshot.
- Prefer the harmless `demo.js` banner for the "execution" shots.
- Keep every screenshot inside this lab (localhost / 10.9.0.0/24).
