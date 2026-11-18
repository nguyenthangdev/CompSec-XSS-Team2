# Shot list — video demo

Thứ tự quay gợi ý (có thể quay rời rồi ghép). Cột "Nguồn" là màn hình cần hiện.

| # | Cảnh | Nguồn màn hình | Ghi chú |
|---|---|---|---|
| S1 | Slide tiêu đề + thành viên | PPT slide 1 | 0:00 |
| S2 | Slide yêu cầu + phạm vi an toàn | PPT slide 3, 4 | 0:45 |
| S3 | `docker compose ps` + đăng nhập Elgg (samy) | Terminal + trình duyệt localhost:8080 | 1:40 |
| S4 | `output/text.php` dòng htmlspecialchars bị comment | Editor mở file trong elgg-lab image | nhấn mạnh countermeasure bị tắt |
| S5 | Edit profile → trường Brief Description (maxlength 250) | Trình duyệt | 2:50 |
| S6 | Dán payload `<script src=.../demo.js>` và Save | Trình duyệt | payload vô hại |
| S7 | `python3 exploit.py serve` | Terminal | 4:10 |
| S8 | `curl -I .../demo.js` + `curl .../health` | Terminal | thấy MIME + JSON |
| S9 | Alice xem profile Samy → banner + alert | Trình duyệt (cửa sổ ẩn danh/2nd profile) | 5:00 |
| S10 | DevTools Network (GET demo.js) + Console log | DevTools | **làm mờ cookie/token** |
| S11 | `exploit.py validate-payload` PASS 53/250, FAIL 251 | Terminal | 6:10 |
| S12 | Sơ đồ http-profile + DevTools request thủ công | PPT/diagram + DevTools | 7:00, làm mờ token |
| S13 | Sơ đồ self-propagation (sequence + dataflow) + bảng demo/theory | PPT/diagram | 8:00 |
| S14 | `python3 -m pytest tests/` → 44 passed | Terminal | 8:50 |
| S15 | Slide countermeasures + slide khai báo AI + cảm ơn | PPT | 9:25 |

## Tài nguyên cần mở sẵn
- 2 phiên đăng nhập Elgg (Samy và Alice) — dùng 2 trình duyệt hoặc cửa sổ ẩn danh.
- Terminal 1: `exploit.py serve` (để nguyên, thấy access log chạy).
- Terminal 2: chạy các lệnh validate/pytest.
- Mở sẵn các sơ đồ trong `docs/diagrams/` (đã render PNG nếu có).
