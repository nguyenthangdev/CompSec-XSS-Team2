# BÁO CÁO DỰ ÁN — Stored XSS tự lan truyền trên Elgg (phiên bản an toàn)

**Môn:** An toàn máy tính · **Lớp:** HUS K68 KHMT
**Nhóm:** Nguyễn Văn Thắng (23001938, nhóm trưởng) · Đinh Bá Thi (23001942) · Đinh Quang Tiến (23001943)

> **Phạm vi an toàn:** Toàn bộ thực hiện trong lab cô lập (loopback + mạng Docker
> `10.9.0.0/24`). Nhóm xây hạ tầng thật + minh hoạ **vô hại**, phân tích worm tự
> lan truyền ở **mức lý thuyết**. `exploit.py` là công cụ **kiểm tra lab**, không
> phải worm. Không bịa kết quả, ảnh chụp, commit hay trạng thái upload.

---

## 1. Cấu trúc thư mục dự án

```
CompSec/
├── README.md                      # tổng quan + cách tái lập
├── BAO_CAO.md                     # báo cáo này
├── exploit.py                     # CLI kiểm tra lab an toàn
├── src/
│   ├── lab_config.py              # cấu hình tập trung + allow-list mục tiêu
│   ├── js_server/{server.py,demo.js,README.md}
│   └── payload_validator/{validator.py,README.md}
├── tests/                         # 44 test pytest
├── scripts/elgg_http_poc.sh       # PoC HTTP có tự reset (tài khoản của mình)
├── elgg-lab/
│   ├── README.md                  # dựng/tắt/reset + tài khoản
│   └── Labsetup/                  # Docker Elgg 3.0 (bản sao SEED) + override cổng
├── docs/
│   ├── requirements/requirements-matrix.md
│   ├── plans/                     # audit + master plan + 5 kế hoạch con
│   ├── analysis/                  # stored-xss, http-workflows, self-propagation
│   ├── diagrams/*.mmd             # 5 sơ đồ Mermaid
│   ├── evidence/                  # log thật + báo cáo + checklist ảnh
│   └── AI_USAGE_LOG.md
├── deliverables/
│   ├── Self_Propagation_XSS_Group_Presentation.pptx
│   └── video_script.md, video_shotlist.md, video_checklist.md, youtube_submission.md
└── Resource/                      # tài liệu gốc của môn (GIỮ NGUYÊN)
```

## 2. Thành phần đã hiện thực

| Thành phần                  | Mô tả                                                | Trạng thái        |
| --------------------------- | ---------------------------------------------------- | ----------------- |
| Lab Elgg 3.0 (Docker)       | Mục tiêu dễ tổn thương, đã dựng & kiểm chứng chạy    | ✅                |
| Web server JS (`server.py`) | health, MIME JS đúng, 404, log, chống path traversal | ✅                |
| `demo.js`                   | Payload minh hoạ **vô hại** (banner + alert)         | ✅                |
| Validator độ dài            | Đếm code point vs byte UTF-8, chuẩn 250              | ✅                |
| `exploit.py`                | `--check/--serve/--validate-payload/--test/--report` | ✅                |
| 44 test pytest              | validator, server, config, CLI                       | ✅ (44/44)        |
| PoC HTTP (`scripts/`)       | Chứng minh Stored XSS mức HTTP, tự reset             | ✅                |
| Tài liệu + sơ đồ            | audit, kế hoạch, phân tích, 5 sơ đồ                  | ✅                |
| PowerPoint (13 slide, VN)   | có speaker notes, khai báo AI                        | ✅                |
| Tài liệu video              | kịch bản/shotlist/checklist/YouTube                  | ✅                |
| Worm tự lan truyền          | **chỉ phân tích lý thuyết**                          | ⚠️ PARTIAL (cố ý) |

## 3. Lệnh cài đặt

```bash
python3 -m pip install pytest          # phụ thuộc runtime: chỉ stdlib + pytest để test
cd elgg-lab/Labsetup && docker compose up -d --build   # lần đầu kéo image seed-elgg + mysql:8.0.22
# Thêm vào /etc/hosts để trình duyệt vào được Elgg:
echo "10.9.0.5  www.seed-server.com" | sudo tee -a /etc/hosts
```

## 4. Lệnh chạy

```bash
python3 exploit.py serve                               # host demo.js tại 127.0.0.1:8000
python3 exploit.py validate-payload '<script src="http://localhost:8000/demo.js"></script>'
python3 exploit.py --check                             # kiểm tra toàn lab
python3 exploit.py --report --json                     # xuất báo cáo verification
bash scripts/elgg_http_poc.sh                          # PoC Stored XSS mức HTTP (tự reset)
# Trình duyệt: http://www.seed-server.com  (đăng nhập samy / seedsamy)
```

## 5. Lệnh kiểm thử

```bash
python3 -m pytest tests/ -v            # 44 test
python3 exploit.py --test              # tương đương, qua CLI
```

## 6. Phiên bản & cấu hình Elgg

- **Elgg 3.0** (image `handsonsecurity/seed-elgg:original`), Apache/PHP trong container.
- **MySQL 8.0.22**, database `elgg_seed`.
- Vhost `www.seed-server.com` tại `10.9.0.5`; mạng `10.9.0.0/24` cô lập; map host `127.0.0.1:8080`.
- **Cơ chế chống XSS bị tắt có chủ đích:** `htmlspecialchars` trong
  `vendor/elgg/elgg/views/default/output/text.php` bị comment → in thô.
- Tài khoản: `admin/seedelgg`, `samy/seedsamy` (guid 59), `alice/seedalice`, `boby/seedboby`, `charlie/seedcharlie`.

## 7. Kết quả thực nghiệm (thật)

1. **Elgg chạy được:** trả trang "Elgg For SEED Labs", đặt cookie phiên (qua Host `www.seed-server.com`). Lưu ý: vào `localhost:8080` trực tiếp sẽ ra trang Apache mặc định.
2. **Giới hạn 250 KHÔNG được image enforce:** gửi 300 ký tự vào Brief Description vẫn lưu đủ; input không có `maxlength`. Nhóm vẫn giữ 250 làm ràng buộc thiết kế theo đề bài.
3. **Stored XSS xác nhận ở mức HTTP:** payload `XSSLAB-POC<script src="http://localhost:8000/demo.js"></script>` được trả **nguyên vẹn, không mã hoá** trong thân trang `/profile/samy`. → trình duyệt thật sẽ tải & chạy `demo.js` trong origin Elgg. Đã reset sạch tài khoản.
4. **Server JS:** `/demo.js` trả đúng `Content-Type: application/javascript; charset=utf-8`; `/health` trả JSON; 404 đúng.
5. **Allow-list:** từ chối mục tiêu công khai (vd `example.com`), chỉ cho loopback + `10.9.0.0/24`.

Bằng chứng: `docs/evidence/logs/stored-xss-http-poc.txt`, `elgg-http-poc-run.txt`, `elgg-landing-probe.txt`, `exploit-check-full.txt`, `docs/evidence/verification-report.md`.

## 8. Kết quả kiểm thử tự động

```
44 passed in ~3.6s     (docs/evidence/logs/pytest-output.txt)
exploit.py --check:  8/8 checks passed   (docs/evidence/logs/exploit-check-full.txt)
```

Phủ: giới hạn 250, đúng/vượt giới hạn, Unicode tiếng Việt, NFC, emoji, kiểu dữ liệu sai; health/MIME/404/unavailable của server; allow-list cho/ từ chối; CLI validate/check/report; từ chối host công khai.

## 9. Git commits

Khởi tạo repo cục bộ và commit theo nhóm (xem `git log --oneline`). **Không push** nếu chưa được cho phép. Danh sách commit thực tế:

```
docs: AI usage disclosure, project README, final report
docs(deliverables): Vietnamese PowerPoint + video materials
docs(evidence): evidence index, real logs, verification report
docs(analysis): stored-XSS, HTTP workflow, self-propagation + diagrams
test: automated suite (44 cases) for validator, server, config, CLI
feat(cli): safe exploit.py verification CLI + self-resetting HTTP PoC
feat(infra): demo.js host server, payload validator, central config + allow-list
feat(lab): reproducible Elgg 3.0 docker environment + lab docs
chore: workspace audit, requirements matrix, and project plans
```

(9 commit cục bộ trên nhánh `main`; chưa push.)

## 10. File PowerPoint

`deliverables/Self_Propagation_XSS_Group_Presentation.pptx` — 13 slide tiếng Việt,
có speaker notes, đã qua `validate.py` (PASSED). _Lưu ý: môi trường dựng không có
LibreOffice nên nhóm nên mở lại bằng PowerPoint để rà soát thị giác lần cuối._

## 11. Tài liệu video

`deliverables/video_script.md` (kịch bản ~10 phút, 3 người), `video_shotlist.md`,
`video_checklist.md`, `youtube_submission.md` (hướng dẫn upload Unlisted). **Chưa
quay/upload** — nhóm thực hiện rồi điền link.

## 12. Ảnh chụp bằng chứng

Log thật đã có trong `docs/evidence/logs/`. Ảnh chụp trình duyệt (banner/alert,
Network tab, cross-account, before/after) **chưa chụp** — danh sách chờ trong
`docs/evidence/README.md`. Không dùng sơ đồ thay cho ảnh thực nghiệm.

## 13. Khai báo AI

`docs/AI_USAGE_LOG.md` — chủ yếu **Mức 3** (AI sinh mã/test/tài liệu theo prompt;
nhóm kiểm thử & chịu trách nhiệm). Có trong slide 13 và kịch bản video.

## 14. Checklist nộp bài

- [ ] `exploit.py` (đã có).
- [ ] `Self_Propagation_XSS_Group_Presentation.pptx` (đã có) — rà soát lại bằng PowerPoint.
- [ ] Video quay + upload YouTube **Unlisted** → dán link.
- [ ] Điền `<MSV>` thật khi minh hoạ "About me".
- [ ] Chụp đủ ảnh theo `docs/evidence/README.md`.
- [ ] Nộp theo form trên Classroom.

## 15. Ma trận yêu cầu

Xem `docs/requirements/requirements-matrix.md` (27 mục): **16 COMPLETE, 11 PARTIAL, 0 NOT DONE**.

## 16. Yêu cầu chưa hoàn tất (PARTIAL)

- Worm tự lan truyền tự động: **cố ý** chỉ phân tích lý thuyết (R15–R18).
- Ảnh chụp trình duyệt cho PoC/Network/cross-account (R1, R9, R13, R23).
- Finding 250: đã sửa lại trung thực (R2 — image không enforce).
- Quay & upload video; xác nhận phân công thực tế (R25, R27).

## 17. Việc thủ công còn lại của nhóm

1. Thêm `/etc/hosts` và đăng nhập 4 tài khoản, kiểm tra profile/kết bạn thủ công.
2. Thực hiện minh hoạ Stored XSS vô hại trên **trình duyệt**, chụp ảnh (che token).
3. Điền `<MSV>` thật cho phần "About me" khi minh hoạ.
4. Quay video theo kịch bản, chia lời cho 3 thành viên, upload YouTube Unlisted.
5. Mở lại PPTX bằng PowerPoint để rà soát thị giác, chèn ảnh thật.
6. Xác nhận phân công đóng góp, nộp theo form.
