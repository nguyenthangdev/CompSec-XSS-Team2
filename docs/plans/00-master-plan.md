# Master Plan — Elgg Stored XSS & Self-Propagation (Safe Research Edition)

## Objective

Deliver a reproducible, honestly-evidenced academic project on **Stored XSS via
the Elgg Brief Description field** and the **self-propagation worm concept**,
while staying inside a strict safety boundary: build the infrastructure and a
**harmless** proof of concept, analyse the worm **theoretically**, and never ship
an autonomous, account-modifying worm.

## Guiding principles

1. **Authoritative source = `Resource/README.docx`.** The slides
   (`11_Web_XSS.pdf`) and SEED lab manual provide background only.
2. **Safety first.** Harmless `demo.js`; `exploit.py` is a verification utility;
   no auto friend-add / profile-edit / propagation / credential capture; local
   allow-list only.
3. **Honest evidence.** Report only what was actually run. Unavailable steps go
   on a pending checklist — never fabricated.
4. **Reproducible.** One command to run tests; documented lab bring-up; pinned
   versions (Elgg 3.0, MySQL 8.0.22).

## Work breakdown (sub-plans)

| Plan | Area | Output |
|---|---|---|
| [01-elgg-environment.md](01-elgg-environment.md) | Lab | Dockerized Elgg 3.0, reproducible up/down/reset |
| [02-stored-xss-analysis.md](02-stored-xss-analysis.md) | Vuln | Brief Description stored-XSS PoC + length bypass |
| [03-javascript-hosting.md](03-javascript-hosting.md) | Infra | `demo.js` host server + validator + `exploit.py` |
| [04-testing.md](04-testing.md) | QA | pytest suite, real output, optional Playwright |
| [05-deliverables.md](05-deliverables.md) | Docs | Diagrams, PPT, video materials, AI log, report |

## High-level sequence

```
Audit ─▶ Requirements ─▶ Plans ─▶ Build infra (server/validator/CLI) ─▶ Tests
      ─▶ Elgg lab up ─▶ Harmless PoC + evidence ─▶ HTTP & propagation analysis
      ─▶ Deliverables (PPT/video/AI log) ─▶ Final QA ─▶ Report
```

## Acceptance criteria (project-level)

- `python3 -m pytest tests/` passes with saved output.
- `python3 exploit.py --check` reports real service status.
- Brief Description stored-XSS PoC documented; harmless `demo.js` loads
  externally with correct MIME.
- 250-char limit validated by automated tests (incl. Unicode).
- Self-propagation delivered as analysis + diagrams, marked PARTIAL.
- PPT + video materials + AI disclosure present; final Vietnamese report written.
- Requirements matrix fully populated with COMPLETE/PARTIAL/NOT DONE.

## Proposed Git commits

See [05-deliverables.md](05-deliverables.md) and the root `README.md` for the
15-group commit plan. Commits are **local only**; nothing is pushed without
explicit permission.
