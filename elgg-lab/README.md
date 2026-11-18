# Elgg Lab Environment (SEED XSS, Elgg 3.0)

Isolated, reproducible target for the Stored-XSS experiments. This is a working
copy of the SEED `Labsetup` (the originals under `Resource/` are left untouched)
plus a host-port override for convenience.

## Versions (pinned)

| Component | Version |
|---|---|
| Elgg | 3.0 (`handsonsecurity/seed-elgg:original`) |
| Web | Apache + PHP (inside the Elgg image) |
| Database | MySQL 8.0.22, database `elgg_seed` |
| Virtual host | `www.seed-server.com` at `10.9.0.5` |
| Network | `net-10.9.0.0` (`10.9.0.0/24`), isolated bridge |

> ⚠️ **Countermeasures are intentionally disabled** in this image (output
> encoding in `output/text.php` is commented out, input filtering disabled). This
> is what makes the Brief Description field exploitable. Never expose this
> container to a public network.

## Start

```bash
cd elgg-lab/Labsetup
docker compose up -d --build        # first run pulls seed-elgg + mysql:8.0.22
docker compose ps                   # elgg-10.9.0.5 and mysql-10.9.0.6 should be Up
```

### ⚠️ How to actually reach Elgg (name-based vhost)

Elgg hard-codes its site URL to `http://www.seed-server.com/` and is served as a
**name-based Apache vhost**. Two consequences we verified:

- Browsing **http://localhost:8080 hits Apache's *default* "It works" page**, NOT
  Elgg (the Host header doesn't match the vhost).
- The **correct** way is to use the hostname. Add this line to `/etc/hosts`:

  ```
  10.9.0.5    www.seed-server.com
  ```

  then browse to **http://www.seed-server.com** (the host can reach the Docker
  bridge IP `10.9.0.5` directly on Linux). All Elgg asset/link URLs then match.

- The `localhost:8080` mapping is still handy for quick checks **with a Host
  header**: `curl -H 'Host: www.seed-server.com' http://localhost:8080/`.

## Test accounts (seeded) — per-account passwords

| Username | Password | Role in the experiment |
|---|---|---|
| `admin` | `seedelgg` | site admin |
| `samy` | `seedsamy` | source / attacker-owned profile (guid **59** in this image) |
| `alice` | `seedalice` | victim / test account 1 |
| `boby` | `seedboby` | victim / test account 2 |
| `charlie` | `seedcharlie` | secondary test account |

> Passwords are **per-account** (`seed` + username), from the SEED lab manual
> (`Resource/Lab11 XSS/Web_XSS_Elgg.pdf`, verified by logging in). They are
> **lab-only** test credentials.

### Measured behaviour note (important, honest finding)

In **this** SEED image the Brief Description (`briefdescription`) input has **no
`maxlength`** and the server accepted a **300-character** value in full — i.e. the
assignment's "250-char limit" is **not enforced here**. We still treat 250 as the
design constraint (it is what the assignment grades and what stock Elgg themes
set). See [`docs/analysis/stored-xss-analysis.md`](../docs/analysis/stored-xss-analysis.md)
and [`docs/evidence/logs/stored-xss-http-poc.txt`](../docs/evidence/logs/stored-xss-http-poc.txt).

## Verify

```bash
# from the repo root, with the lab up:
python3 exploit.py --check --elgg-url http://localhost:8080
```

Manual checks: log in as each account; open a profile; edit Brief Description and
About me; perform a manual add-friend; confirm DevTools can see the requests.

## Stop

```bash
cd elgg-lab/Labsetup
docker compose down                 # stop & remove containers (keeps DB volume)
```

## Reset to a clean seeded state

The MySQL data lives in `elgg-lab/Labsetup/mysql_data/` (a bind mount). To wipe
all experiment changes and re-seed from `elgg.sql`:

```bash
cd elgg-lab/Labsetup
docker compose down
rm -rf mysql_data                   # removes the persisted DB; re-seeded on next up
docker compose up -d --build
```

> `mysql_data/` is git-ignored. Removing it is the supported way to return every
> profile to its original content between demo takes.

## Troubleshooting

- **Port 8080 busy:** change the host port in `docker-compose.override.yml`
  (e.g. `127.0.0.1:8081:80`) and re-run `up`.
- **Image pull fails / offline:** the bring-up error is recorded honestly; retry
  when Docker Hub is reachable. See `docs/evidence/` for the captured log.
- **Can't reach 10.9.0.5 directly:** use the `localhost:8080` mapping instead.
