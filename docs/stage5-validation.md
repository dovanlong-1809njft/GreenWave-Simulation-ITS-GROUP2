# Kiểm chứng Stage5

Đã chạy thực tế trên Linux/Python3.12, Matplotlib3.10.8 và SUMO1.28.0: **46 bài đạt, 0 lỗi, 0 bỏ qua**. Có35 test cũ giữ nguyên và11 test Stage5. Đầu ra nguyên bản: stage5-evidence/tests.txt.

Stage5 không chạy mới18 lượt nghiên cứu; tái sử dụng18 lượt thật của Stage4 đã qua audit. Các test mô phỏng cũ được chạy lại trong bộ test, không dùng các lượt test làm mẫu thống kê nghiên cứu. Dữ liệu Windows chưa được cung cấp nên chưa đối chiếu số liệu Windows.

Kiểm tra gồm: trung bình tính tay; tỷ lệ20%,−20%,50%; mẫu số0; rỗng; xe không hoàn tất; lọc theo route thay vìID; sai duration; IDtrùng; khác tập xe ghép cặp; batch thiếu; đọc18run thật, CSV18dòng kịch bản/9cặp; chống ghi đè; sinh6PNG. Bổ sung smoke test một seed: sinh đủ6hình và SD mẫu để trống, không giả tạo biến thiên.

Đối chiếu gốc: stage5-evidence/hand-check.md. Với hai xe low/seed11: BaselineT=(318+301)/2=309,5s; GreenWaveT=(206+188)/2=197s; tỷ lệ giảm=(309,5−197)/309,5×100≈36,35%. Đây chỉ là mẫu kiểm tra phép tính, không dùng thay trung bình toàn300xe.

Toàn bộ18run trong phân tích khớp số requested/arrived của Stage4. Mỗi cặp giữ nguyên tập xe dự kiến, snapshot và seed; không gộp sáu lượt lặp vào nghiên cứu. Dữ liệu đủ cohort sauxả, nhưngHigh vẫn được gắn cờquá tải. Kiểm tra trực quan sáu hình, không thấy chữ bị cắt hoặc trục gây hiểu nhầm.

Workflow CI hiện tại đã sinh kịch bản trước unittest nên được giữ nguyên. Không chạyGitHub Actions tại đây. Runner không càiSUMO sẽ bỏ qua3 test mô phỏng cũ; nếu không càiMatplotlib thì thêm test vẽ bị bỏ qua. Không coi skipped là đạt tích hợp.

Chưa kiểm chứng Stage5 trực tiếp trênWindows/Python3.13.12 hoặc dữ liệu Windows seed22/33. Không báo cáo p-value/CI. Không thay35 test cũ, workflow, hình học, pha hoặc nhu cầu.
