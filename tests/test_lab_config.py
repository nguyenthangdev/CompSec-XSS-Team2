"""Tests for the central lab configuration and target allow-list."""

from __future__ import annotations

import pytest

from src import lab_config as cfg


def test_brief_description_limit_is_250():
    assert cfg.BRIEF_DESCRIPTION_MAX_CHARS == 250


def test_profile_message_is_template_without_hardcoded_id():
    assert "<MSV>" in cfg.PROFILE_MESSAGE_TEMPLATE
    # No team member's real ID is baked into the template.
    for member in cfg.TEAM:
        assert member["msv"] not in cfg.PROFILE_MESSAGE_TEMPLATE


def test_render_profile_message_requires_explicit_id():
    assert cfg.render_profile_message("23001938") == "Tài khoản này đã bị Hack bởi 23001938"
    with pytest.raises(ValueError):
        cfg.render_profile_message("")
    with pytest.raises(ValueError):
        cfg.render_profile_message("   ")


@pytest.mark.parametrize(
    "target",
    [
        "http://localhost:8000/demo.js",
        "http://127.0.0.1:8000/health",
        "http://10.9.0.5/",
        "www.seed-server.com",
        "http://www.xsslabelgg.com/action/profile/edit",
        "127.0.0.1:8000",
        "10.9.0.200",
    ],
)
def test_allowlist_permits_lab_targets(target):
    decision = cfg.check_target_allowed(target)
    assert decision.allowed is True, decision.reason


@pytest.mark.parametrize(
    "target",
    [
        "http://example.com/",
        "https://google.com",
        "http://8.8.8.8/",
        "http://10.8.0.5/",   # outside the 10.9.0.0/24 lab subnet
        "http://169.254.0.1/",
        "evil.test",
        "",
    ],
)
def test_allowlist_refuses_out_of_scope_targets(target):
    decision = cfg.check_target_allowed(target)
    assert decision.allowed is False, decision.reason


def test_team_roster_matches_official_readme():
    ids = {m["msv"] for m in cfg.TEAM}
    assert ids == {"23001938", "23001942", "23001943"}
    leader = next(m for m in cfg.TEAM if m["role"] == "Nhóm trưởng")
    assert leader["name"] == "Nguyễn Văn Thắng"
