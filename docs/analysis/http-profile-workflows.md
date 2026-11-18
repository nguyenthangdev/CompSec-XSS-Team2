# HTTP & Profile Workflow Analysis (Sanitized)

> This documents the **normal, manually-initiated** Elgg requests observed with
> browser DevTools. All workflows are performed by the team logged into their own
> test accounts. **No** request here is automated through another user's session.
> Session cookies and CSRF token *values* are **redacted** — only field names and
> shapes are recorded.

## 1. Authentication model (what a request needs)

An authenticated state-changing Elgg action requires three things to travel
together:

1. **Session cookie** — `Elgg=<session id>` (HttpOnly). Sent automatically by the
   browser for same-origin requests. *Value redacted.*
2. **CSRF timestamp** — `__elgg_ts` (a Unix timestamp).
3. **CSRF token** — `__elgg_token` (HMAC of the timestamp + session + site secret).

Elgg exposes the current `__elgg_ts`/`__elgg_token` to in-page JavaScript via the
global object `elgg.security.token`. This detail is central to §5.

## 2. Add-friend (manual)

Observed when a user clicks "Add friend" on another profile:

| Property | Value (sanitized) |
|---|---|
| Method | `GET` |
| Endpoint | `/action/friends/add` |
| Query | `friend=<target_guid>&__elgg_ts=<ts>&__elgg_token=<token>` |
| Auth | session cookie (auto) + `__elgg_ts` + `__elgg_token` |
| Response | `302` redirect (or JSON for AJAX) + success system message |
| State change | target GUID added to the acting user's friends list |

`<target_guid>` is the numeric user id of the account to befriend (e.g. Samy's
GUID in the lecture is `47`).

## 3. Edit-profile (manual)

Observed when a user saves profile edits (Brief Description / About me):

| Property | Value (sanitized) |
|---|---|
| Method | `POST` |
| Endpoint | `/action/profile/edit` |
| Content-Type | `application/x-www-form-urlencoded` |
| Key fields | `name`, `description` (About me), `briefdescription`, `accesslevel[...]`, `guid`, `__elgg_ts`, `__elgg_token` |
| `accesslevel[x]` | visibility: `2` = public |
| Auth | session cookie (auto) + `__elgg_ts` + `__elgg_token` |
| Response | `302` redirect back to the profile; new values rendered |
| State change | the named fields are persisted for `guid` |

## 4. Sequence of a normal manual edit

See [../diagrams/http-profile-sequence.mmd](../diagrams/http-profile-sequence.mmd).
In prose: browser GETs the edit form → user types → browser POSTs
`/action/profile/edit` with the form fields + CSRF pair → server validates the
token, writes metadata, responds `302` → browser reloads the profile and the
output view renders the stored value.

## 5. Why CSRF tokens are **not** a defense against XSS

This is the conceptual crux (and a written question in `10. XSS.docx`).

- **CSRF** is an attack from a *different* origin (evil.com) that cannot read the
  Elgg page, so it cannot know `__elgg_token`. The secret token defeats CSRF
  precisely because the attacker is **off-origin and blind**.
- **XSS** runs code **inside** the Elgg origin. An injected script can simply read
  `elgg.security.token.__elgg_ts` and `__elgg_token` from the page's own
  JavaScript context and attach them to a forged request. The token is not a
  secret *to same-origin code*.

Therefore:

> CSRF defenses (secret token, SameSite cookies) stop cross-site forgery but do
> **nothing** against XSS, because XSS is same-origin. The lecture's add-friend
> and edit-profile scripts demonstrate this by reading `elgg.security.token.*`
> directly. The real fix for XSS is **not** a token — it is output encoding /
> input filtering / CSP (see the stored-XSS analysis).

- **SameSite cookies** similarly don't help: the malicious request originates
  from the Elgg page itself (same site), so the cookie is sent normally.
- A **secret token** would only help if it were *unavailable* to page scripts;
  once XSS executes in-origin, nothing on the page is secret from it.

## 6. What we deliberately did **not** do

- We did **not** script `/action/friends/add` or `/action/profile/edit` through a
  victim's browser session.
- We did **not** capture, store, or transmit any real session cookie or token
  value.
- The add-friend / edit-profile requests above were observed for **manual,
  self-initiated** actions only, to document their shape.

## 7. Evidence to attach (team, manual)

- DevTools Network screenshots of a manual add-friend GET and a manual
  edit-profile POST, with cookie/token values blurred.
- The resulting profile/friends-list state before and after.
