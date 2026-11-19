# Team

## Thông tin nhóm

- Tên nhóm (`TenNhom`, không dấu, không khoảng trắng): Vinflow
- Lớp: `L3B`
- Repo của bàn: `K5-L3B-DAY10-Vinflow-PoCtoPilotGate1`
- Thẻ sự cố đã bốc (S1–S8): S3

## Thành viên

Họ tên đầy đủ và MSSV của **mọi** thành viên; bàn 3 người thì để trống dòng 4. Vai: Kỹ sư cổng · Sản phẩm và kinh doanh · Vận hành và pháp lý (README mục 3, phút 0–15).

| STT | Họ và tên | MSSV | Vai | Trưởng nhóm |
| --: | --------- | ---- | --- | :---------: |
|   1 | Nguyễn Anh Quân | 2A202603892 | Kỹ sư cổng | x |
|   2 | Nguyễn Đình Nam | 2A202603797 | Kỹ sư cổng | |
|   3 | Nguyễn Ngọc Ninh | 2A202603774 | Vận hành và pháp lý | |
|   4 | Phạm Nguyên Khoa | 2A202603795 | Sản phẩm và kinh doanh | |

Ghi `members` trong `submission/submission.json` theo dạng `"HoVaTen-MSSV"`, khớp bảng trên.

## Cá nhân

Mỗi thành viên tự viết một mục bên dưới (chép mẫu, đổi tiêu đề thành họ tên không dấu và MSSV, ví dụ `## NguyenVanAn-20241234`).

## NguyenAnhQuan-2A202603892

### Phần việc phụ trách

Vai: Kỹ sư cổng 1 (Trưởng nhóm). Phụ trách chạy pipeline, code cổng phòng ngừa `lab10/guards.py`, kiểm thử mốc base/prepared/after, quản lý Git và điều phối kỹ thuật.

### Đóng góp cụ thể

- Thiết lập cấu hình Git, ký Bản tiêu chí chấp nhận Gate 1 với cryptographic lock hash `b210221f5579`.
- Xây dựng các cổng bảo vệ hệ thống trong `lab10/guards.py`: ghim chính sách hiệu lực `pre_guard`, kiểm tra quyền lợi DB cho `issue_refund`, chặn ghi lỗi oan `file_carrier_fault`, khử PII cho `notify_carrier`, và bổ sung cổng khống chế trần `max_auto_strikes_per_carrier_per_day = 2` cho đối tác vận chuyển ở Vòng 2.
- Chạy toàn bộ pipeline kiểm thử các mốc base, prepared, after; thực thi lệnh tự kiểm tra `lab10.grade --incident S3` đạt chuẩn `PASS-VISIBLE` (100% xanh) và gom bài nộp `check_submission --collect`.

### Bằng chứng

- Các commit bài nộp trên GitHub: `103882a`, `e46cf9b`, `16d9384`, `adb86eb`, `e072e04`, `5ae94a8`.
- Báo cáo kiểm tra `runs/R-S3-grade-20261119-170849-d140db.json`: pass_rate = 1.0, 0 lỗi hoàn sai, 0 lỗi hãng oan, 0 rò rỉ PII.

### Exit ticket

Một điều học được: Cổng bảo vệ hệ thống (system guard) độc lập với model ở tầng máy chủ là bức tường lửa cốt lõi để đưa AI từ PoC vào Pilot thực tế, đặc biệt là cơ chế đếm tần suất tích lũy theo ngày để khống chế rủi ro cho đối tác.
Một điều còn chưa chắc: Làm thế nào để tự động điều tiết trần lỗi tự động của các hãng vận chuyển linh hoạt theo cấp độ thời tiết thực tế mà không cần cấu hình thủ công.

## NguyenDinhNam-2A202603797

### Phần việc phụ trách

Vai: Kỹ sư cổng 2 (Observability & Testing). Phụ trách trace ticket lỗi, thiết kế offline metric, behavioral test & ticket hiểm, xây dựng custom monitor `lab10/monitors.py`.

### Đóng góp cụ thể

- Dò trace các ticket lỗi đại diện trên seed 11 (`T-002`, `S3-01`, `S3-20`, `S3-42`), hoàn thiện Bảng soát lỗi C2 (phân loại chính xác lỗi chìm và giới hạn hệ thống).
- Thiết kế Offline Metric cho bước chọn chính sách (Câu 1.3), giải thích đọc khoảng tin cậy 95% (Câu 1.5).
- Xây dựng và tối ưu các custom monitors trong `lab10/monitors.py` (`carrier_dispute_risk_rate`, `carrier_strike_ceiling_breach_rate`, `carrier_fault_denial_rate`, `max_carrier_daily_strikes`, `missing_delay_cause_rate`) giúp bài test `6 monitor ✅` sáng đèn đạt chuẩn.

### Bằng chứng

- File `lab10/monitors.py`, mục C2 và C8 trong `templates/form-c-incident.md`.
- Kết quả kiểm tra `6 monitor ✅` sáng đèn từ 0.50 về 0.00 trên báo cáo `R-S3-grade-20261119-170849-d140db`.

### Exit ticket

Một điều học được: Một telemetry monitor tốt trong production không cần nhãn đúng/sai mà phải dựa trên các tín hiệu quan hệ dữ liệu và tần suất hành vi (như tracking null, bão lũ, dồn dập lỗi) để phát hiện rủi ro trước khi có khiếu nại.
Một điều còn chưa chắc: Cách đặt ngưỡng cảnh báo động (dynamic threshold) cho monitor khi lưu lượng ticket giữa ngày thường và ngày siêu sale chênh nhau 10 lần.

## NguyenNgocNinh-2A202603774

### Phần việc phụ trách

Vai: Vận hành và pháp lý. Phụ trách mục tiêu vận hành (kế toán, CSKH), HAZOP mở rộng ngoài kỹ thuật, checklist 9 nhóm việc, cổng vận hành & pháp lý, viết Runbook và chuẩn bị file bài nộp `submission/`.

### Đóng góp cụ thể

- Thiết lập mục tiêu từ góc nhìn người dùng nội bộ (Chị Oanh Kế toán đối soát, Chị Hạnh Trưởng ca CSKH - Câu 1.2), thiết kế Telemetry production (Câu 1.4).
- Phân tích bản đồ dữ liệu C3.5 về rủi ro pháp lý "đảo ngược nghĩa vụ chứng minh", xây dựng bảng HAZOP 4 dòng (Mục C4 có dòng WRONG).
- Thiết lập Risk Register 2 dòng (Mục C10), cập nhật checklist 9 nhóm việc và viết chi tiết Runbook 4 & Runbook 5 (Mục C11) với quy trình bồi hoàn đối soát trong 2h-24h và 3 kịch bản vận hành thực tế.

### Bằng chứng

- Các mục A1, A2 trong `templates/form-a-criteria.md`, các mục C3.5, C4, C10, C11 trong `templates/form-c-incident.md`.
- Cấu hình pháp lý và vận hành trong `config/operating_gates.json`.

### Exit ticket

Một điều học được: Mọi quyết định AI ghi vào sổ cái hay biên bản phạt đối tác đều có giá trị pháp lý ràng buộc; nếu thiếu chứng cứ tracking thì biên bản phạt hoàn toàn vô hiệu và gây rủi ro đứt gãy đối tác vận chuyển.
Một điều còn chưa chắc: Cơ chế pháp lý để phân định trách nhiệm bồi thường giữa nền tảng e-commerce và hãng vận chuyển cấp 3 khi hệ thống AI gặp sự cố gián đoạn kết nối.

## PhamNguyenKhoa-2A202603795

### Phần việc phụ trách

Vai: Sản phẩm và kinh doanh. Phụ trách mục tiêu hệ thống, bản đồ dữ liệu & data drift, thiết lập tiêu chí chấp nhận `config/acceptance_criteria.json`, cổng kinh doanh và soạn thảo quyết định Gate 1 (v1, v2).

### Đóng góp cụ thể

- Thiết lập mục tiêu cấp hệ thống (Câu 1.1), dự thảo các ngưỡng an toàn, kinh doanh và vận hành trong `config/acceptance_criteria.json`.
- Phân tích nguyên nhân Concept Drift bão số 9 tại C1, viết Specification và Giả định môi trường (Câu 3.2, 3.3 tại C5), vẽ Fault Tree trước và sau khi sửa (Mục C6, C9).
- Soạn thảo và bảo vệ Quyết định Gate 1 v1 và v2 (Mục B8, C12) dựa trên 3 nhánh của `decision_rule`, chứng minh các chỉ số ROI (1.46) và chi phí mỗi ticket (4.072đ) đạt xuất sắc.

### Bằng chứng

- Mục A0 trong `templates/form-a-criteria.md`, `config/acceptance_criteria.json`.
- Các mục C1, C5, C6, C9, C12 trong `templates/form-c-incident.md`, Quyết định Gate 1 v1 và v2.

### Exit ticket

Một điều học được: Quyết định chuyển từ PoC sang Pilot (Gate 1) phải được xây dựng dựa trên bằng chứng đo lường thực tế và các quy tắc `decision_rule` đã ký trước, tuyệt đối không ra quyết định dựa trên cảm tính hay chỉ nhìn vào độ chính xác của model.
Một điều còn chưa chắc: Làm sao để định lượng chính xác chi phí ẩn (hidden cost) của việc xói mòn lòng tin đối tác khi hệ thống thử nghiệm có những sai lệch nhỏ trong giai đoạn Pilot.
