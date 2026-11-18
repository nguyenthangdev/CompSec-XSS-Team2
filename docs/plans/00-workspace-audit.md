# Phase 0 — Workspace Audit

*Generated during the initial inspection of the project workspace. Facts below
were observed directly with shell commands, not assumed.*

## 1. Environment

| Tool | Version | Notes |
|---|---|---|
| OS | Ubuntu, Linux 6.17.0-41-generic (x86_64) | host machine |
| Python | 3.13.7 (`/usr/bin/python3`) | pip 25.1.1, `pytest` 8.3.5 available |
| Docker | 29.3.0 + Compose v5.1.0 | daemon reachable; 14 images cached |
| Node.js | v24.15.0 | npm 11.12.1 (Playwright installable via `npx`) |
| Browsers | Google Chrome 153, Firefox 158 | available for manual demo / screenshots |
| PHP | 8.4.11 (CLI) | not needed directly; Elgg runs inside Docker |
| git | 2.51.0 | workspace is **not** a git repository at audit time |

## 2. Repository structure (at audit time)

The working directory `…/CompSec` initially contained a single `Resource/`
folder with the course materials:

```
Resource/
├── README.docx            # OFFICIAL assignment (authoritative requirements)
├── 10. XSS.docx           # SEED XSS written questions (book exercises)
├── 10_Web_CSRF.pdf        # previous lab (CSRF) — out of scope
├── 11_Web_XSS.pdf         # lecture slides (49 pages)
└── Lab11 XSS/
    ├── Web_XSS_Elgg.pdf   # SEED lab manual
    └── Labsetup/          # SEED Docker environment for Elgg
        ├── docker-compose.yml
        ├── image_mysql/   # MySQL 8.0.22 + elgg.sql seed data
        └── image_www/     # Elgg 3.0 + Apache + the disabled-countermeasure files
Resource/Lec11 Web_XSS/    # lecture reference scripts (add_friend.js, edit_profile.js,
                           #   self_display_script.js, self_propogating.js, csp/)
```

> The two documents named by the master prompt as `README.md` and
> `11_Web_XSS.pptx` exist here as **`README.docx`** and **`11_Web_XSS.pdf`**.
> We treat `Resource/README.docx` as the single authoritative assignment.

## 3. What the authoritative README.docx requires

Reproduce the **Self-Propagation XSS worm** attack on Elgg, but:

- inject through the **Brief Description** profile field (max **250 characters**),
  **not** the longer "About me" field;
- because 250 chars cannot hold a self-contained worm, store only a **URL
  reference to an external `.js` file** served from a personal web server;
- the worm JS must (per the assignment) auto-add the attacker as a friend,
  re-write Brief Description with the original payload (self-propagation), and
  set "About me" to `Tài khoản này đã bị Hack bởi <MSV>`;
- deliverables: a narrated screen-capture **video** (unlisted YouTube), a 10-minute
  **PowerPoint**, and the program file **`exploit.py`**;
- **AI usage must be disclosed** with the three assignment-defined levels.

## 4. Key technical facts extracted from the lab materials

- **Elgg version:** 3.0 (base image `handsonsecurity/seed-elgg:original`,
  Composer vendor tree under `/var/www/elgg/vendor/elgg/elgg`).
- **Database:** MySQL 8.0.22, database `elgg_seed`.
- **Virtual host / IP:** `www.seed-server.com` at `10.9.0.5` (SEED subnet
  `10.9.0.0/24`). Legacy lecture scripts use the older name `www.xsslabelgg.com`.
- **Countermeasures are intentionally disabled** in the lab image:
  `vendor/elgg/elgg/views/default/output/text.php` has its
  `htmlspecialchars(...)` call **commented out** and replaced with raw
  `echo "{$value}";`. The same is done in `dropdown.php`, and input filtering is
  disabled in `engine/lib/input.php`. This is what makes the stored XSS work.
- **Relevant endpoints** (from the lecture scripts):
  - Add friend: `GET /action/friends/add?friend=<guid>&__elgg_ts=…&__elgg_token=…`
  - Edit profile: `POST /action/profile/edit` (`name`, `description`,
    `accesslevel[description]`, `guid`, `__elgg_ts`, `__elgg_token`).
  - CSRF tokens are exposed to page JS via `elgg.security.token.__elgg_ts` /
    `__elgg_token`.
- **Test accounts** (SEED standard, seeded in `elgg.sql`, verified by login):
  `admin`/`seedelgg`, `samy`/`seedsamy` (guid 59), `alice`/`seedalice`,
  `boby`/`seedboby`, `charlie`/`seedcharlie` (passwords are `seed`+username).

## 5. Pre-existing source code

The only code present at audit time was the **reference lecture material** under
`Resource/Lec11 Web_XSS/` (the SEED-provided example worm and helper scripts).
These are course references; this project **does not** modify, enhance, or
weaponize them. They are analysed theoretically in
[`docs/analysis/self-propagation-analysis.md`](../analysis/self-propagation-analysis.md).

No project source, Docker config, tests, or deliverables existed before this work.

## 6. Decisions taken

1. **Do not touch `Resource/`.** It is kept pristine. A working copy of the lab
   setup was copied to `elgg-lab/Labsetup/` for modification.
2. **Scope = defensive/analytical.** Following the project brief, we build the
   isolated infrastructure (JS host, validator, verification CLI), demonstrate a
   **harmless** stored-XSS proof of concept, and treat the autonomous worm
   (friend-add, profile-edit, self-propagation) as **analysis only**. `exploit.py`
   is a verification utility, not a worm.
3. **Honesty of evidence.** Live experiments are only reported when actually run;
   anything not executed is recorded in a pending-evidence checklist.

## 7. Risks / unknowns identified

- The SEED base image `handsonsecurity/seed-elgg:original` must be pulled from
  Docker Hub (hundreds of MB). If the pull fails, the lab bring-up is documented
  with the real error instead of being faked.
- Automated browser screenshots require a running Elgg + a driver (Playwright).
  If unavailable, the team captures screenshots manually following the evidence
  checklist.
