"""Centralized configuration for the Elgg Stored-XSS lab (safe research edition).

This module is the single source of truth for:

* the length limit of the Elgg "Brief Description" profile field (250 chars),
* the addresses that the verification tooling is *allowed* to talk to,
* the external-JavaScript hosting server defaults,
* the required "defacement" profile message **template**.

SAFETY / SCOPE
--------------
Everything here targets an **isolated local lab** only. The allow-list below
intentionally contains loopback / RFC-1918 / lab addresses. The verification
CLI (``exploit.py``) refuses to operate against anything outside this list, so
the tooling cannot be pointed at a public website.

The profile message is a *template* containing the ``<MSV>`` placeholder. We do
**not** hard-code any single student's ID into executable logic: the team fills
in a confirmed member ID at demonstration time. See ``PROFILE_MESSAGE_TEMPLATE``.
"""

from __future__ import annotations

import ipaddress
from dataclasses import dataclass, field
from urllib.parse import urlparse

# ---------------------------------------------------------------------------
# Elgg "Brief Description" field
# ---------------------------------------------------------------------------

#: Maximum number of Unicode characters (code points) the Brief Description
#: field is specified to accept by the assignment (and by stock Elgg themes,
#: which set ``maxlength=250`` on this input).
#:
#: NOTE (measured): the SEED lab image used here does NOT actually enforce this
#: — its ``briefdescription`` input has no ``maxlength`` and a 300-char value was
#: accepted and stored in full (see docs/evidence/logs/stored-xss-http-poc.txt).
#: We keep 250 as the *target constraint* the payload must respect, because it is
#: what the assignment grades and what a realistic Elgg deployment enforces.
BRIEF_DESCRIPTION_MAX_CHARS: int = 250


# ---------------------------------------------------------------------------
# Lab network / target allow-list
# ---------------------------------------------------------------------------

#: The Elgg web application inside the SEED Docker network.
#: SEED assigns the ``www`` container the static address 10.9.0.5 and the
#: virtual host ``www.seed-server.com``.
ELGG_CONTAINER_IP: str = "10.9.0.5"
ELGG_HOSTNAME: str = "www.seed-server.com"

#: Canonical URL a BROWSER should use. Elgg hard-codes its wwwroot to
#: http://www.seed-server.com/ (it is a name-based Apache vhost), so the browser
#: must use this hostname — add "10.9.0.5  www.seed-server.com" to /etc/hosts.
#: (Visiting http://localhost:8080 hits Apache's DEFAULT vhost, not Elgg.)
ELGG_BASE_URL: str = "http://www.seed-server.com"

#: How the *tooling* reaches Elgg without an /etc/hosts edit: connect to the
#: container IP and send the right Host header. The host can reach the Docker
#: bridge (10.9.0.5) directly on Linux. Used by exploit.py's availability probe.
ELGG_PROBE_URL: str = "http://10.9.0.5/"
ELGG_PROBE_HOST_HEADER: str = ELGG_HOSTNAME  # www.seed-server.com

#: Optional host port published by docker-compose.override.yml (loopback only).
#: Convenient for `curl -H 'Host: www.seed-server.com' http://localhost:8080/`.
ELGG_HOST_PORT_URL: str = "http://localhost:8080"

#: Defaults for the external JavaScript hosting server (Phase 4).
JS_SERVER_HOST: str = "127.0.0.1"
JS_SERVER_PORT: int = 8000
JS_RESOURCE_NAME: str = "demo.js"
HEALTH_PATH: str = "/health"

#: Host names / IPs the verification tooling may contact. Anything else is
#: rejected as an "out-of-scope / public" target. Loopback and the SEED
#: 10.9.0.0/24 lab subnet are allowed.
ALLOWED_HOSTS: tuple[str, ...] = (
    "localhost",
    "127.0.0.1",
    "::1",
    ELGG_HOSTNAME,          # www.seed-server.com (resolved via /etc/hosts)
    "www.xsslabelgg.com",   # legacy SEED vhost name, kept for compatibility
)

#: CIDR ranges considered "lab-local" and therefore allowed.
ALLOWED_CIDRS: tuple[str, ...] = (
    "127.0.0.0/8",      # loopback
    "10.9.0.0/24",      # SEED lab subnet
)


# ---------------------------------------------------------------------------
# Required profile message (TEMPLATE ONLY - no invented student ID)
# ---------------------------------------------------------------------------

#: The assignment requires the "About me" field to be set to the message below,
#: where <MSV> is the student ID (Mã Sinh Viên) of ONE confirmed team member.
#: We keep it as a template; the team substitutes a real, confirmed ID at
#: demonstration time via ``render_profile_message()``.
PROFILE_MESSAGE_TEMPLATE: str = "Tài khoản này đã bị Hack bởi <MSV>"

#: Confirmed team roster (from the official README.docx). These IDs are recorded
#: for documentation only; they are NOT auto-substituted into any attack logic.
TEAM = (
    {"name": "Nguyễn Văn Thắng", "msv": "23001938", "role": "Nhóm trưởng"},
    {"name": "Đinh Bá Thi", "msv": "23001942", "role": "Thành viên"},
    {"name": "Đinh Quang Tiến", "msv": "23001943", "role": "Thành viên"},
)


def render_profile_message(msv: str) -> str:
    """Return the defacement message with a *caller-supplied* student ID.

    The ID must be provided explicitly; this function never guesses one.
    """
    if not msv or not msv.strip():
        raise ValueError("msv (student ID) must be provided explicitly")
    return PROFILE_MESSAGE_TEMPLATE.replace("<MSV>", msv.strip())


# ---------------------------------------------------------------------------
# Target allow-list enforcement
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ScopeDecision:
    """Result of an allow-list check."""

    allowed: bool
    host: str
    reason: str


def _host_in_allowed_cidrs(host: str) -> bool:
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return False
    return any(ip in ipaddress.ip_network(c) for c in ALLOWED_CIDRS)


def check_target_allowed(url_or_host: str) -> ScopeDecision:
    """Decide whether *url_or_host* is an in-scope lab target.

    Accepts a full URL (``http://localhost:8000/health``) or a bare host.
    Only loopback, the SEED lab subnet, and the configured lab hostnames are
    permitted. Everything else — importantly, any public website — is rejected.
    """
    raw = (url_or_host or "").strip()
    if not raw:
        return ScopeDecision(False, "", "empty target")

    # Extract the host component.
    if "://" in raw:
        host = urlparse(raw).hostname or ""
    else:
        # Could be "host", "host:port" or a bare IP (incl. IPv6 in brackets).
        candidate = raw
        if candidate.startswith("["):  # [::1]:8000
            host = candidate[1 : candidate.find("]")]
        elif candidate.count(":") == 1:  # host:port
            host = candidate.split(":", 1)[0]
        else:
            host = candidate

    host = host.strip().lower()
    if not host:
        return ScopeDecision(False, host, "could not parse host from target")

    if host in {h.lower() for h in ALLOWED_HOSTS}:
        return ScopeDecision(True, host, "host is in the explicit allow-list")

    if _host_in_allowed_cidrs(host):
        return ScopeDecision(True, host, "host is inside an allowed lab CIDR")

    return ScopeDecision(
        False,
        host,
        "host is NOT a configured lab target (public/out-of-scope targets are refused)",
    )


__all__ = [
    "BRIEF_DESCRIPTION_MAX_CHARS",
    "ELGG_CONTAINER_IP",
    "ELGG_HOSTNAME",
    "ELGG_BASE_URL",
    "JS_SERVER_HOST",
    "JS_SERVER_PORT",
    "JS_RESOURCE_NAME",
    "HEALTH_PATH",
    "ALLOWED_HOSTS",
    "ALLOWED_CIDRS",
    "PROFILE_MESSAGE_TEMPLATE",
    "TEAM",
    "render_profile_message",
    "ScopeDecision",
    "check_target_allowed",
]
