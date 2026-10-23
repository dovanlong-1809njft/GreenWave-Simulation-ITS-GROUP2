# Kiểm thử / Test Plan

- **UT-01**: `300m / 36km/h = 30s`.
- **UT-02**: 4 giao lộ offset `[0,30,60,90]` với chu kỳ 120s.
- **UT-03**: offset lớn hơn chu kỳ được chuẩn hóa modulo.
- **UT-04**: phát hiện tốc độ đầu vào không hợp lệ.
- **IT-01 (TODO)**: SUMO chạy được 1 kịch bản baseline không báo lỗi mạng/tuyến/đèn.
- **IT-02 (TODO)**: SUMO chạy kịch bản greenwave, kiểm tra thời điểm xanh.
- **IT-03 (TODO)**: kịch bản cùng seed có đúng cùng tổng nhu cầu đầu vào.
- **AT-01 (TODO)**: đủ bảng/chỉ số cho 3 mức lưu lượng ở 2 phương án.
- **AT-02 (TODO)**: chạy demo bằng GUI và giải thích kết quả.

Không coi việc vượt mọi trường hợp bằng greenwave là tiêu chí bắt buộc. Kết quả trái kỳ vọng phải được phân tích.

## Kiểm thử giai đoạn 2

Chạy `py scripts/validate_sample.py --run` và `py -m unittest discover -s tests -v`. Xem [báo cáo kiểm thử](stage2-validation.md). Test tích hợp được đánh dấu bỏ qua nếu không tìm thấy SUMO; không coi bỏ qua là kiểm thử tích hợp đã đạt.
