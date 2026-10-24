# Phương pháp phân tích

Mạng/chu kỳ/pha/offset và nhu cầu của Stage4 được giữ nguyên. Đầu vào là đúng một batch có batch.json cùng sealed-run.zip cho từng trường hợp. Dùng audit_batch/check_seal của Stage4 để xác minh CRC, hash và tính công bằng, không trộn batch lặp vào mẫu nghiên cứu.

Nguồn sử dụng: batch sealed_primary từ docs/stage4-evidence/raw-runs.zip, 18 lượt Linux SUMO1.28.0, seed11/22/33. Sáu lượt sealed_repeat chỉ phục vụ kiểm tra tái lập Stage4, không đưa vào phép tính trung bình Stage5. Không có dữ liệu từ đường dẫn Windows results/raw/stage4/20261024T024249811236Z trong workspace.

Đọc lại tripinfo.xml và snapshot nhu cầu trong từng gói; không chỉ tin CSV đã tính trước. Phân loại hướng theo route thực của từng vehicle: W_A A_B B_C C_D D_E là hướng ưu tiên; chuỗi ngược là chiều ngược; phần còn lại là nhánh. Không đoán từ tiền tốID. Giữ cả bốn nhóm trong vehicle_metrics, chỉ hướng ưu tiên có planned depart thuộc[300,3900) dùng cho chỉ số chính. Loại nhóm làm nóng theo thời điểm dự kiến, không loại xe xuất phát muộn sau3900.

Thời gian chính là arrival−depart thực tế, toàn tuyến W→E: gồm tiếp cậnA và rờiD. Chưa có dữ liệu thời điểm qua từng vạch để tính riêng A→D giữa hai vạch dừng; không gọi sai phạm vi đo.

Ghép đúng tập xe dự kiến theo level/seed, kiểm tra route và thời điểm yêu cầu. Tính chỉ số từng seed trước; ba seed có trọng số bằng nhau. Tỷ lệ giảm tổng hợp là trung bình ba tỷ lệ giảm theo cặp, không phải tỷ lệ trên tập xe gộp. SD là độ lệch chuẩn mẫu giữa seed (n−1); không có CI/p-value.

Nếu tập hoàn tất khác nhau, bảng ghi n_requested/n_common_arrived, chỉ cung cấp trung bình có điều kiện trên giao tập hoàn tất và gắn nhãn; không xuất tỷ lệ giảm chính, không vẽ hình chính như đủ dữ liệu. Xe chưa đến đích không được gán thời gian0. Các trường thiếu giữ trống và có mẫu số riêng cho từng chỉ số.

Dữ liệu thực hiện tại hoàn tất đủ cohort sau xả:300/600/900 xe measurement mỗi seed/mỗi phương án. High vẫn không ổn định trong[300,3900), nên phân tích riêng chậm chèn và tồn đọng, không coi xả hết là phục vụ900xe/h ổn định. Xem theory-summary.md, Lecture04 tr.19–31 và34–44; không đọc lại PDF khi chưa cần xác minh.
