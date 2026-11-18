"""Tests for the Brief Description payload-length validator."""

from __future__ import annotations

import pytest

from src.payload_validator.validator import (
    is_within_limit,
    measure_payload,
)

LIMIT = 250


def test_empty_payload_is_within_limit():
    m = measure_payload("")
    assert m.char_count == 0
    assert m.byte_count == 0
    assert m.within_limit is True
    assert m.remaining == LIMIT


def test_typical_valid_link_payload():
    payload = '<script src="http://localhost:8000/demo.js"></script>'
    m = measure_payload(payload)
    assert m.within_limit is True
    assert m.char_count == len(payload)
    # ASCII: code points == bytes.
    assert m.char_count == m.byte_count


def test_exactly_250_characters_passes():
    payload = "a" * 250
    m = measure_payload(payload)
    assert m.char_count == 250
    assert m.within_limit is True
    assert m.remaining == 0


def test_251_characters_fails():
    payload = "a" * 251
    m = measure_payload(payload)
    assert m.char_count == 251
    assert m.within_limit is False
    assert m.remaining == -1


def test_unicode_vietnamese_counts_code_points_not_bytes():
    # "Tài khoản này đã bị Hack bởi 23001938" — Vietnamese diacritics.
    payload = "Tài khoản này đã bị Hack bởi 23001938"
    m = measure_payload(payload)
    # Code-point count is what the 250 limit measures.
    assert m.char_count == len(payload)
    # UTF-8 byte length is strictly larger because of multi-byte accents.
    assert m.byte_count > m.char_count
    assert m.within_limit is True


def test_unicode_single_emoji_is_one_or_two_code_points_but_several_bytes():
    payload = "😀"  # one astral code point, 4 UTF-8 bytes
    m = measure_payload(payload)
    assert m.char_count == 1
    assert m.byte_count == 4


def test_limit_boundary_with_unicode():
    payload = "á" * 250  # 250 code points, 500 bytes
    m = measure_payload(payload)
    assert m.char_count == 250
    assert m.byte_count == 500
    assert m.within_limit is True
    assert measure_payload("á" * 251).within_limit is False


def test_non_string_payload_raises_type_error():
    with pytest.raises(TypeError):
        measure_payload(b"bytes-not-str")  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        measure_payload(None)  # type: ignore[arg-type]


def test_negative_limit_raises_value_error():
    with pytest.raises(ValueError):
        measure_payload("x", limit=-1)


def test_custom_limit_is_respected():
    assert is_within_limit("abc", limit=3) is True
    assert is_within_limit("abcd", limit=3) is False


def test_explain_mentions_pass_or_fail():
    assert "PASS" in measure_payload("ok").explain()
    assert "FAIL" in measure_payload("a" * 251).explain()


def test_nfc_normalization_reported_for_decomposed_input():
    # 'á' as base 'a' + combining acute accent == 2 code points, NFC == 1.
    decomposed = "á" * 130  # 260 code points raw, 130 after NFC
    m = measure_payload(decomposed)
    assert m.char_count == 260
    assert m.nfc_char_count == 130
    # Raw count exceeds the limit even though the NFC form would fit — the
    # validator surfaces both so the team is not surprised by normalization.
    assert m.within_limit is False
