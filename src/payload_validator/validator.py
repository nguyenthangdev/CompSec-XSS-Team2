"""Payload-length validator for the Elgg "Brief Description" field.

The Brief Description field accepts at most 250 characters, which is far too
small to hold a complete self-contained XSS worm. This utility measures a
candidate payload and reports whether it fits, clearly separating two different
notions of "length":

* **Unicode code points** (``len(str)`` in Python) — this is what a browser /
  HTML ``maxlength`` counts, and what the 250-char limit refers to.
* **UTF-8 byte length** — what the payload occupies on the wire / in storage.

The distinction matters because the required defacement text is Vietnamese
("Tài khoản này đã bị Hack bởi <MSV>"): accented characters are a single code
point each but take 2-3 UTF-8 bytes, so byte length overstates the field cost.

The validator is pure (no network, no side effects) and is reused by the
automated tests and by ``exploit.py --validate-payload``.
"""

from __future__ import annotations

import argparse
import sys
import unicodedata
from dataclasses import dataclass

try:  # Package-relative import (python -m src.payload_validator.validator ...)
    from ..lab_config import BRIEF_DESCRIPTION_MAX_CHARS
except ImportError:  # Executed as a loose script
    BRIEF_DESCRIPTION_MAX_CHARS = 250


@dataclass(frozen=True)
class PayloadMeasurement:
    """The result of measuring a payload against the field limit."""

    char_count: int           # Unicode code points (the limit is measured in these)
    byte_count: int           # UTF-8 bytes
    nfc_char_count: int       # code points after NFC normalization
    limit: int                # the configured maximum (250)
    within_limit: bool        # char_count <= limit
    remaining: int            # limit - char_count (negative if over)

    def explain(self) -> str:
        """Human-readable verdict suitable for CLI output."""
        status = "PASS" if self.within_limit else "FAIL"
        lines = [
            f"[{status}] Brief Description length check",
            f"  Unicode code points : {self.char_count}  (limit = {self.limit})",
            f"  UTF-8 bytes         : {self.byte_count}",
        ]
        if self.nfc_char_count != self.char_count:
            lines.append(
                f"  NFC code points     : {self.nfc_char_count}  "
                f"(input was not in NFC form; Elgg/browser may re-count after normalization)"
            )
        if self.within_limit:
            lines.append(f"  Fits with {self.remaining} character(s) to spare.")
        else:
            lines.append(
                f"  Over limit by {-self.remaining} character(s) — this payload "
                f"would be rejected / truncated by the field."
            )
        return "\n".join(lines)


def measure_payload(payload: str, limit: int = BRIEF_DESCRIPTION_MAX_CHARS) -> PayloadMeasurement:
    """Measure *payload* against *limit*.

    Parameters
    ----------
    payload:
        The candidate Brief Description content. Must be ``str``; passing bytes
        or ``None`` is an error (callers decode first and decide the encoding).
    limit:
        Maximum number of Unicode code points allowed (default 250).

    Raises
    ------
    TypeError:
        If *payload* is not a ``str``.
    ValueError:
        If *limit* is negative.
    """
    if not isinstance(payload, str):
        raise TypeError(
            f"payload must be str, got {type(payload).__name__}; "
            "decode bytes to str before measuring"
        )
    if limit < 0:
        raise ValueError("limit must be >= 0")

    char_count = len(payload)
    byte_count = len(payload.encode("utf-8"))
    nfc_char_count = len(unicodedata.normalize("NFC", payload))
    within = char_count <= limit
    return PayloadMeasurement(
        char_count=char_count,
        byte_count=byte_count,
        nfc_char_count=nfc_char_count,
        limit=limit,
        within_limit=within,
        remaining=limit - char_count,
    )


def is_within_limit(payload: str, limit: int = BRIEF_DESCRIPTION_MAX_CHARS) -> bool:
    """Convenience boolean wrapper around :func:`measure_payload`."""
    return measure_payload(payload, limit).within_limit


def _read_payload(args: argparse.Namespace) -> str:
    if args.payload is not None:
        return args.payload
    if args.file is not None:
        with open(args.file, "r", encoding="utf-8") as fh:
            return fh.read()
    # Fall back to stdin (allows: echo -n '<script..>' | validator --stdin)
    return sys.stdin.read()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="payload-validator",
        description=(
            "Measure a candidate Elgg Brief Description payload and check it "
            "against the 250-character limit."
        ),
    )
    src = parser.add_mutually_exclusive_group()
    src.add_argument("payload", nargs="?", help="payload text given directly on the command line")
    src.add_argument("-f", "--file", help="read the payload from a UTF-8 file")
    src.add_argument("--stdin", action="store_true", help="read the payload from standard input")
    parser.add_argument(
        "-l",
        "--limit",
        type=int,
        default=BRIEF_DESCRIPTION_MAX_CHARS,
        help=f"character limit to check against (default: {BRIEF_DESCRIPTION_MAX_CHARS})",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="print only PASS/FAIL and the character count",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Returns 0 if the payload fits, 1 if it does not."""
    args = build_parser().parse_args(argv)
    if args.payload is None and args.file is None and not args.stdin:
        build_parser().error("provide a payload argument, --file, or --stdin")

    payload = _read_payload(args)
    measurement = measure_payload(payload, args.limit)

    if args.quiet:
        verdict = "PASS" if measurement.within_limit else "FAIL"
        print(f"{verdict} {measurement.char_count}/{measurement.limit}")
    else:
        print(measurement.explain())

    return 0 if measurement.within_limit else 1


if __name__ == "__main__":
    raise SystemExit(main())
