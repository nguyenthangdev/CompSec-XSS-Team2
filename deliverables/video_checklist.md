# Checklist quay & nộp video

## Trước khi quay
- [ ] Lab Elgg đã chạy: `cd elgg-lab/Labsetup && docker compose up -d --build`, vào được http://localhost:8080.
- [ ] Reset dữ liệu về trạng thái sạch nếu đã thử nghiệm trước đó (xem elgg-lab/README.md).
- [ ] Server JS chạy: `python3 exploit.py serve`.
- [ ] `python3 -m pytest tests/` đạt 44/44 (quay lại được).
- [ ] Điền `<MSV>` thật vào phần demo "About me" (một MSV của thành viên nhóm) — chỉ khi minh hoạ thủ công.
- [ ] Phân vai thuyết minh (Thắng/Thi/Tiến) đã thống nhất.
- [ ] Đã render sơ đồ Mermaid sang ảnh để chèn (nếu dùng).

## Trong khi quay
- [ ] Độ phân giải ≥ 1080p, phóng to terminal/trình duyệt cho dễ đọc.
- [ ] **Làm mờ** mọi cookie `Elgg=` và `__elgg_token` khi hiện DevTools.
- [ ] Nói rõ "payload vô hại", "không sửa tài khoản" ở phần demo XSS.
- [ ] Nêu rõ phần tự lan truyền là **lý thuyết**, không chạy tự động.
- [ ] Bám mốc thời gian trong `video_script.md` để giữ ~10 phút.

## Sau khi quay
- [ ] Dựng/ghép, kiểm tra âm thanh 3 giọng rõ ràng.
- [ ] Có slide/khung khai báo AI trong video.
- [ ] Xuất file ≤ thời lượng yêu cầu, kiểm tra lại không lộ token.
- [ ] Upload YouTube **Unlisted** (xem youtube_submission.md).
- [ ] Dán link vào form nộp bài trên Classroom kèm `exploit.py` và file PPT.
