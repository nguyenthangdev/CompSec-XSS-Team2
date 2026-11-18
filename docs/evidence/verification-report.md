# Lab Verification Report

- Generated: 2026-11-18T11:03:22
- Tool: `exploit.py --report` (safe verification utility)
- Elgg target: `http://www.seed-server.com`
- JS server target: `http://127.0.0.1:8000`

> This report is generated from **live probes**. Unreachable services
> are reported as such and are never shown as passing.

## Service & configuration checks

| Check | Result | Detail |
|---|---|---|
| Brief Description limit configured | PASS | limit = 250 chars |
| Profile message is a template (no hard-coded MSV) | PASS | 'Tài khoản này đã bị Hack bởi <MSV>' |
| Allow-list permits the local lab target | PASS | http://127.0.0.1:8000 -> host is in the explicit allow-list |
| Allow-list refuses a public target | PASS | http://example.com/ -> host is NOT a configured lab target (public/out-of-scope targets are refused) |
| Local demo.js resource exists | PASS | /home/thang/Documents/hus-k68-khmt/CompSec/src/js_server/demo.js |
| JS server /health reachable | PASS | HTTP 200 |
| JS server serves demo.js | PASS | HTTP 200 |
| Elgg application reachable | PASS | http://10.9.0.5/ (Host: www.seed-server.com) -> HTTP 200, Elgg page confirmed |

**Summary: 8/8 checks passed.**

## Payload-length demonstration

Sample link-approach payload: `<script src="http://localhost:8000/demo.js"></script>`

```
[PASS] Brief Description length check
  Unicode code points : 53  (limit = 250)
  UTF-8 bytes         : 53
  Fits with 197 character(s) to spare.
```

## Scope & safety

- Network probes are restricted to the lab allow-list (`localhost, 127.0.0.1, ::1, www.seed-server.com, www.xsslabelgg.com` and CIDRs `127.0.0.0/8, 10.9.0.0/24`).
- This tool performs **no** account modification, friend request, self-propagation, or credential collection.
