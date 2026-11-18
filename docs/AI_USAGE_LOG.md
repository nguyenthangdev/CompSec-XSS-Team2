# Khai báo sử dụng AI / AI Usage Disclosure

> Theo yêu cầu của đề bài, nhóm khai báo rõ ràng những nội dung nào sử dụng AI và
> mức độ áp dụng. Khai báo này cũng được đưa vào slide thuyết trình và video.
>
> *Per the assignment, the team discloses which content used AI and at what level.
> This disclosure also appears in the presentation and the video.*

## Công cụ AI đã dùng / AI tools used

| Công cụ | Vai trò |
|---|---|
| **Claude Code (Anthropic, model Opus)** | Tác nhân lập trình: tạo sinh và kiểm thử mã nguồn, tài liệu, sơ đồ, slide theo prompt của sinh viên. |

## Ba mức độ sử dụng AI (theo đề bài)

### Mức 1 — Dùng AI để tranh luận, phản biện; sinh viên tự triển khai
*AI used for discussion/critique; student implements.*

- Thảo luận cơ chế Stored XSS trên trường **Brief Description**, lý do trường
  giới hạn 250 ký tự buộc phải dùng **external script (link approach)**.
- Phản biện về ranh giới an toàn: vì sao **không** hiện thực hóa worm tự lan
  truyền tự động mà chỉ phân tích + minh hoạ vô hại.
- Bàn về vì sao **CSRF token không chống được XSS** (mã chạy cùng origin).

### Mức 2 — AI đồng sáng tạo từng phần theo thiết kế của sinh viên
*AI co-creates parts per the student's design; student edits & is responsible.*

- Ý tưởng & khung do sinh viên đặt ra (cấu trúc thư mục, các mốc kiểm thử,
  nội dung slide, kịch bản video). AI viết nội dung chi tiết; sinh viên biên tập,
  kiểm chứng và chịu trách nhiệm.
- Ma trận yêu cầu (requirements matrix) và các bản kế hoạch: sinh viên quyết định
  phạm vi và trạng thái; AI soạn thảo.

### Mức 3 — AI tạo sinh thiết kế & triển khai theo prompt của sinh viên
*AI generates design & implementation per the student's prompt; student writes
prompts, verifies, and assembles the final product.*

Thành phần do AI tạo sinh (sinh viên là người viết prompt, kiểm thử, ghép nối):

| Thành phần | Mô tả |
|---|---|
| `src/js_server/server.py` | HTTP server host `demo.js` (health, MIME JS, 404, log) |
| `src/js_server/demo.js` | Payload minh hoạ **vô hại** (banner + alert, không sửa tài khoản) |
| `src/payload_validator/validator.py` | Tiện ích đếm/validate độ dài 250 ký tự |
| `src/lab_config.py` | Cấu hình tập trung + allow-list mục tiêu nội bộ |
| `exploit.py` | CLI kiểm tra lab an toàn (`--check/--serve/--validate-payload/--test/--report`) |
| `tests/` | 44 test tự động (pytest) |
| `docs/` | Phân tích, sơ đồ, kế hoạch, ma trận yêu cầu |
| `deliverables/` | Slide, kịch bản video, tài liệu nộp |

## Kiểm chứng & trách nhiệm của sinh viên / Student verification & responsibility

- **Kiểm chứng:** sinh viên chạy `python3 -m pytest tests/` (44 pass), chạy
  `exploit.py --check`, dựng lab Elgg bằng Docker, và tự tay thực hiện phần minh
  hoạ Stored XSS vô hại trên trình duyệt.
- **Chỉnh sửa của sinh viên:** điền `<MSV>` thật khi trình diễn, chụp ảnh màn
  hình thật, xác nhận phân công công việc, quay và lồng tiếng video.
- **Chịu trách nhiệm:** nhóm chịu trách nhiệm về toàn bộ nội dung nộp; AI là công
  cụ hỗ trợ, không thay thế việc hiểu và kiểm chứng của sinh viên.

## Giới hạn / Limitations

- AI **không** tạo worm tự lan truyền; phần đó chỉ là **phân tích lý thuyết**.
- Các kết quả thực nghiệm (ảnh chụp, log trình duyệt) phải do nhóm thực hiện thật;
  tài liệu này không bịa kết quả. Mục nào chưa chạy được đánh dấu PARTIAL và liệt
  kê trong checklist bằng chứng.
- AI có thể sai sót; nhóm đã kiểm thử tự động và thủ công để giảm thiểu rủi ro.

## Tuyên bố ngắn để đưa vào slide/video / Short statement for slide & video

> "Nhóm sử dụng Claude Code (AI) chủ yếu ở **Mức 3**: AI tạo sinh mã nguồn, test
> và tài liệu theo prompt của nhóm. Nhóm tự viết prompt, kiểm thử (44/44 test
> đạt), dựng lab, thực hiện minh hoạ và chịu trách nhiệm nội dung. Worm tự lan
> truyền **chỉ được phân tích lý thuyết**, không hiện thực hóa."
