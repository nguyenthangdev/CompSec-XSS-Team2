# Plan 01 — Elgg Lab Environment

## Objective
Provide a reproducible, isolated Elgg 3.0 instance (the vulnerable target) that
any teammate can start, reset, and shut down identically.

## Tasks
1. Reuse the SEED `Labsetup` (copied to `elgg-lab/Labsetup/`, originals untouched).
2. Add `docker-compose.override.yml` to publish Elgg on `127.0.0.1:8080` (host
   browser access without editing `/etc/hosts`).
3. Document version facts (Elgg 3.0, MySQL 8.0.22, host `www.seed-server.com`,
   subnet `10.9.0.0/24`) and the **disabled countermeasures**.
4. Write `elgg-lab/README.md` with start/stop/reset and the four test accounts.
5. Bring the stack up; capture the real build/up log.

## Dependencies
- Docker 29.3 + Compose v5.1 (present).
- Network access to Docker Hub to pull `handsonsecurity/seed-elgg:original` and
  `mysql:8.0.22`.

## Acceptance criteria
- `docker compose up -d --build` succeeds (or the real failure is documented).
- Elgg responds at `http://localhost:8080` (HTTP 200/302 to login).
- `samy`, `alice`, `boby`, `charlie` can authenticate (password `seedelgg`).
- Reset procedure returns the DB to its seeded state.

## Tests
- `exploit.py --check --elgg-url http://localhost:8080` → "Elgg reachable" PASS.
- Manual: log in as each test account; load a profile; edit Brief Description.

## Expected evidence
- Build/up log (`docs/evidence/logs/` or linked from the lab README).
- Screenshots: login page, Samy profile, Brief Description edit form
  (`docs/evidence/screenshots/`, captured by the team if not automated).

## Proposed Git commit
`feat(lab): reproducible Elgg 3.0 docker environment with host port + docs`
