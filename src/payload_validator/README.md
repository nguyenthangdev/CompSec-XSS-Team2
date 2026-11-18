# Payload-length validator

Measures a candidate **Brief Description** payload and checks it against the
**250-character** limit, clearly separating two notions of length:

- **Unicode code points** (`len(str)`) — what the field limit and HTML
  `maxlength` actually count.
- **UTF-8 bytes** — what the value occupies on the wire / in storage.

This matters for the Vietnamese defacement string, where accented characters are
one code point but 2–3 bytes.

## Use

```bash
# via the main CLI
python3 exploit.py validate-payload '<script src="http://localhost:8000/demo.js"></script>'

# or the module directly
python3 -m src.payload_validator.validator --file payload.txt
echo -n '<script src=...>' | python3 -m src.payload_validator.validator --stdin
```

Exit code is `0` if the payload fits, `1` if it exceeds the limit (handy in
scripts).

## As a library

```python
from src.payload_validator.validator import measure_payload
m = measure_payload("Tài khoản này đã bị Hack bởi 23001938")
m.char_count      # 37  (code points -> compared against the 250 limit)
m.byte_count      # 44  (UTF-8 bytes)
m.within_limit    # True
print(m.explain())
```

## Character-counting method

- The limit is enforced on **code points** (`len(str)`), matching browser
  `maxlength` behaviour.
- `byte_count` uses `str.encode("utf-8")`.
- `nfc_char_count` reports the length after Unicode **NFC** normalization, so a
  decomposed input (base letter + combining accent, 2 code points) is not a
  silent surprise versus its composed form (1 code point).

See `tests/test_payload_validator.py` for the full behaviour (empty, 250, 251,
Vietnamese, emoji, NFC, invalid types).
