# Định nghĩa chỉ số và đơn vị

| Chỉ số | Cách tính / nguồn | Đơn vị |
| --- | --- | --- |
| travel_time_s | arrival thực − depart thực; đối chiếu duration SUMO sai khác tối đa0,021s do xuất làm tròn | s/xe |
| waiting_time_s | waitingTime: tốc độ≤0,1m/s, không gồm dừng có lịch | s/xe |
| time_loss_s | timeLoss: chậm so với tốc độ lý tưởng của xe; khác thời gian đứng chờ | s/xe |
| stops | waitingCount gốc: số đợt chờ khi tốc độ≤0,1m/s; không tự tính từFCD | lần/xe |
| depart_delay_s | depart thực − depart dự kiến từ nhu cầu; gồm lượng tử hóa bước1s và chờ chèn | s/xe |
| sumo_depart_delay_s | departDelay gốc, lưu riêng vì quy ước lượng tử hóa có thể khác | s/xe |
| total_requested_to_arrival_s | arrival − planned depart = thời gian trong mạng + chậm chèn | s/xe |
| pending/running | chưa được chèn / đã chèn nhưng chưa đến đích, ghi ở3900và7500 | xe |

Tất cả giá trị thời gian dùng giây, không đổi phút/giờ ngầm. Thời gian trung bình tính với số xe có trường hợp lệ, cột *_n cho biết mẫu số. Số xe được yêu cầu vẫn lưu để thấy mức thiếu dữ liệu.

Reduction(%)=(Baseline−GreenWave)/Baseline×100: dương là giảm, âm là tăng. Baseline≤0 hoặc thiếu giá trị: trống/không xác định, không chia0 và không thay bằng0%. Không dùng công thức giảm cho số xe đến đích như một thước đo càng thấp càng tốt.

Nguồn kỹ thuật đối chiếu24/10/2026: https://sumo.dlr.de/docs/Simulation/Output/TripInfo.html. Stage4 đã có đủ tripinfo, summary, statistics, detector, dữ liệu xe chưa xuất phát/hoàn tất; không có FCD và không cần thêm cơ chế xuất dữ liệu cho Stage5.
