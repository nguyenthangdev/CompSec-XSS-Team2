# Requirements Matrix

Traceability from the **authoritative** `Resource/README.docx` (and the research
areas A–E in the project brief) to implementation, verification, and evidence.

**Status legend**
- **COMPLETE** — implemented in this repo and verified (test/log/probe).
- **PARTIAL** — infrastructure/analysis done; a manual lab step or screenshot
  remains for the team, *or* the item is deliberately analysis-only (the
  autonomous worm).
- **NOT DONE** — not implemented.

**Scope note.** Per the project brief, the autonomous worm behaviours
(auto friend-add, auto profile-edit, self-propagation) are **analysed, not
weaponized**. They are intentionally kept **PARTIAL** (theory + manual
demonstration), never COMPLETE.

| ID | Requirement (source) | Implementation | Verification | Evidence | Status |
|---|---|---|---|---|---|
| R1 | Stored XSS on the **Brief Description** field (README; area A) | Harmless PoC: store `<script src=…/demo.js>` in Brief Description (samy's own acct); value rendered un-encoded → external `demo.js` runs in Elgg origin | **HTTP-level PoC confirmed** (payload echoed raw) via `scripts/elgg_http_poc.sh`; browser alert screenshot pending | [stored-xss-http-poc.txt](../evidence/logs/stored-xss-http-poc.txt), [elgg-http-poc-run.txt](../evidence/logs/elgg-http-poc-run.txt) | PARTIAL |
| R2 | Confirm the **250-character** limit of Brief Description (area A) | 250 kept as the **spec/target** (`BRIEF_DESCRIPTION_MAX_CHARS=250`). **Measured:** this image does **not** enforce it — a 300-char value was accepted & stored in full (no `maxlength`) | `tests/test_lab_config.py::test_brief_description_limit_is_250` (spec) + live length experiment (behaviour) | [stored-xss-http-poc.txt](../evidence/logs/stored-xss-http-poc.txt); [pytest-output.txt](../evidence/logs/pytest-output.txt) | PARTIAL |
| R3 | Inspect how Elgg **stores/renders** profile descriptions; is HTML sanitized or encoded? (area A) | Source analysis of `output/text.php` (encoding commented out), `input.php` (filter disabled) | Code reading of lab image files | [stored-xss-analysis.md §Sanitization](../analysis/stored-xss-analysis.md) | COMPLETE |
| R4 | Record actual Elgg **version & security configuration** (area A) | Elgg 3.0, MySQL 8.0.22, countermeasures disabled — documented | Dockerfiles + `elgg.sql` inspection | [00-workspace-audit.md](../plans/00-workspace-audit.md) | COMPLETE |
| R5 | **Payload-length restriction bypass** via external `.js` link (README task 2; area C) | Explained: short `<script src>` reference ≪ 250 chars vs. full inline worm | `validate-payload` shows the link payload fits with room to spare | [stored-xss-analysis.md §Length](../analysis/stored-xss-analysis.md) | COMPLETE |
| R6 | Payload-length **validation utility** + tests for the 250 limit (area C) | `src/payload_validator/validator.py` (code points vs UTF-8 bytes) | `tests/test_payload_validator.py` (12 cases incl. empty/250/251/Unicode/NFC) | [pytest-output.txt](../evidence/logs/pytest-output.txt) | COMPLETE |
| R7 | Stand up a **personal web server** to host the `.js` (README task 3; area B) | `src/js_server/server.py` (health, JS MIME, 404, access log, traversal guard) | `tests/test_js_server.py` + live `curl` of `/health`, `/demo.js`, 404 | [logs/js-server-access.log](../evidence/logs/js-server-access.log) | COMPLETE |
| R8 | Provide the external **JavaScript resource** `demo.js` (area B) | Harmless `src/js_server/demo.js` (visual banner + local event only) | Served with `application/javascript; charset=utf-8`; content asserted in tests | [logs/pytest-output.txt](../evidence/logs/pytest-output.txt) | COMPLETE |
| R9 | **Content-Type / Network** inspection of external JS load (area B) | JS MIME override; DevTools Network procedure documented | `test_demo_js_served_with_correct_content_type`; `curl -I` header capture | [logs/js-server-stdout.log](../evidence/logs/js-server-stdout.log) | PARTIAL |
| R10 | Server **health checks, 404, server-unavailable** handling (area B) | `/health` JSON; 404 JSON; connection-refused path | `test_health_*`, `test_missing_resource_returns_404`, `test_server_unavailable_*` | [logs/pytest-output.txt](../evidence/logs/pytest-output.txt) | COMPLETE |
| R11 | Explain inline vs **external** script, and how the browser fetches/executes it (area C) | Written analysis + sequence of browser fetch → execute | Doc review | [stored-xss-analysis.md](../analysis/stored-xss-analysis.md) | COMPLETE |
| R12 | Effect of **CSP / Mixed Content / sanitization** on script loading (area C) | Dedicated section (nonce CSP from lab, HTTP-to-HTTP so no mixed content) | Doc review against lab `http_server.py` CSP header | [stored-xss-analysis.md §Defenses](../analysis/stored-xss-analysis.md) | COMPLETE |
| R13 | **Manual** friend-request / profile-edit workflow + HTTP analysis (area D) | Sanitized HTTP method/endpoint/field analysis; manual steps only | DevTools capture procedure (team performs manually) | [http-profile-workflows.md](../analysis/http-profile-workflows.md) | PARTIAL |
| R14 | Why XSS-origin JS can drive authenticated actions; **why CSRF tokens ≠ XSS defense** (area D) | Explained: same-origin script reads `elgg.security.token`, so CSRF tokens don't stop XSS | Doc review (ties to "10. XSS.docx" written questions) | [http-profile-workflows.md §CSRF-vs-XSS](../analysis/http-profile-workflows.md) | COMPLETE |
| R15 | **Self-propagation** analysis `Samy → Alice → Boby`: sequence + data-flow diagrams (README deliverable; area E) | Analysis doc + two Mermaid diagrams; theory vs demonstrated clearly split | Doc + diagram review | [self-propagation-analysis.md](../analysis/self-propagation-analysis.md), [diagrams/](../diagrams/) | PARTIAL |
| R16 | Worm auto **add-friend** (README worm action 1) | **Analysis only** (not weaponized); mechanism explained from lecture `add_friend.js` | Doc review | [self-propagation-analysis.md](../analysis/self-propagation-analysis.md) | PARTIAL |
| R17 | Worm auto **edit Brief Description = original payload** (self-propagation) (README action 2) | **Analysis only**; link-approach replication explained | Doc review | [self-propagation-analysis.md](../analysis/self-propagation-analysis.md) | PARTIAL |
| R18 | Worm set **About me** = `Tài khoản này đã bị Hack bởi <MSV>` (README action 3) | Message kept as **template** (`<MSV>`); `render_profile_message()` needs explicit ID | `test_profile_message_is_template_without_hardcoded_id` | [logs/pytest-output.txt](../evidence/logs/pytest-output.txt) | PARTIAL |
| R19 | **`exploit.py`** program file (README deliverable) | Safe verification CLI: `--check/--serve/--validate-payload/--test/--report` | `tests/test_exploit_cli.py` (7 cases) + live `--check`/`--report` runs | [verification-report.md](../evidence/verification-report.md) | COMPLETE |
| R20 | Restrict tooling to the **local lab** (brief; safety) | Allow-list (loopback + `10.9.0.0/24` + lab hosts); public targets refused | `test_allowlist_*` (15 cases) + `test_safe_http_get_refuses_public_target` | [logs/pytest-output.txt](../evidence/logs/pytest-output.txt) | COMPLETE |
| R21 | **Automated tests** executed; real output saved (brief Phase 9) | 44 pytest cases across config/validator/server/CLI | `python3 -m pytest tests/ -v` → 44 passed | [logs/pytest-output.txt](../evidence/logs/pytest-output.txt) | COMPLETE |
| R22 | **Elgg lab environment** reproducible (brief Phase 2) | `elgg-lab/Labsetup` (copied SEED setup) + host port override + README; **brought up & verified** (Elgg 3.0, MySQL 8.0.22) | `docker compose up` succeeded; `exploit.py --check` → Elgg confirmed (8/8) | [exploit-check-full.txt](../evidence/logs/exploit-check-full.txt), [elgg-landing-probe.txt](../evidence/logs/elgg-landing-probe.txt) | COMPLETE |
| R23 | **Evidence / screenshots** of each step (README deliverable) | Evidence index + pending checklist; real logs where available | Screenshot checklist; captured logs | [docs/evidence/README.md](../evidence/README.md) | PARTIAL |
| R24 | **PowerPoint** (10 min, Vietnamese) (README deliverable) | `deliverables/Self_Propagation_XSS_Group_Presentation.pptx` with speaker notes | Open in PowerPoint/LibreOffice | deliverables/ | COMPLETE |
| R25 | **Video** script/shotlist/checklist + YouTube unlisted guide (README deliverable) | `deliverables/video_*.md`, `youtube_submission.md` | Doc review (recording done by team) | deliverables/ | PARTIAL |
| R26 | **AI usage disclosure**, 3 levels (README note) | `docs/AI_USAGE_LOG.md` + slide + video section | Doc review | [AI_USAGE_LOG.md](../AI_USAGE_LOG.md) | COMPLETE |
| R27 | **Team responsibilities** recorded (brief §2) | Roster from README; proposed split documented (team confirms) | Doc review | [AI_USAGE_LOG.md](../AI_USAGE_LOG.md), presentation | PARTIAL |

## Summary

- **COMPLETE:** R3, R4, R5, R6, R7, R8, R10, R11, R12, R14, R19, R20, R21, R22, R24, R26 (16).
- **PARTIAL:** R1, R2, R9, R13, R15, R16, R17, R18, R23, R25, R27 (11) — infrastructure/analysis done (and for R1 the stored-XSS *mechanism* is confirmed at HTTP level); remaining items are the **manual, human-in-the-loop browser screenshots**, the corrected 250-char finding, plus the deliberately analysis-only worm behaviours.
- **NOT DONE:** none.

The autonomous self-propagating worm is **PARTIAL by design** (analysed and
manually reasoned, never implemented as a working weapon), consistent with the
project's safety boundaries.
