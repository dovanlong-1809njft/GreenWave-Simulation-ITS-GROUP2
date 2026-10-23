# Thuật toán Giai đoạn 3 và cơ sở học thuật

## 1. Nguồn và ranh giới

Nguồn học thuật là [theory-summary.md](theory-summary.md), đã tổng hợp Lecture 04. Không đọc lại PDF trong giai đoạn này vì nguồn trang và công thức đã đủ dùng.

| Nội dung | Nguồn |
| --- | --- |
| Định thời cố định và phối hợp theo thời gian | Lecture 04 tr. 5–15 |
| Đoàn xe và phối hợp tín hiệu liên hoàn | Lecture 04 tr. 19–21 |
| Biểu đồ thời gian–không gian | Lecture 04 tr. 22–23, 29–30 |
| Độ lệch giữa hai đèn và công thức L/V | Lecture 04 tr. 24–27 |
| Băng thông và giới hạn phối hợp hai chiều | Lecture 04 tr. 28–31; chưa tính băng thông/hiệu quả thực nghiệm ở GĐ3 |

Cộng dồn độ lệch theo mốc A, phép modulo, biểu diễn XML, ánh xạ linkIndex và cơ chế ghi log là cách triển khai của project. Không gán chúng thành yêu cầu trực tiếp từ giảng viên.

## 2. Tham số đang dùng

| Tham số | Giá trị | Nguồn gốc |
| --- | --- | --- |
| Hướng ưu tiên | A→B→C→D | config/network.json, thiết kế project |
| Khoảng cách giữa tâm nút | 300/300/300 m | config/network.json và kiểm tra tọa độ mạng thật |
| Tốc độ thiết kế | 36 km/h = 10 m/s | config/network.json, giả định |
| Chu kỳ C | 120 s | config/signals.json, giả định |
| Thời lượng 6 pha | 45/3/2/65/3/2 s | config/signals.json, giả định |
| Baseline offset | 0/0/0/0 s | config/signals.json |
| Xe và mạng | Giữ nguyên mẫu GĐ2, 85 xe | sample.rou.xml, corridor.net.xml |
| Cửa sổ chạy và seed | 0–1800 s, bước 1 s, seed 11 | sample.sumocfg, giữ giống nhau cho cả hai phương án |

Baseline gọi chính xác là đối chứng định thời đồng thời, chưa phối hợp theo thời gian đi để tạo làn sóng xanh. Không đại diện mọi kiểu điều khiển không phối hợp và không cố tình thay chu kỳ hay luồng xe để tạo khác biệt.

## 3. Công thức và tính tay

Theo L04 tr. 25, thời gian đi lý tưởng giữa hai đèn: `t_i = L_i / V`.

Với mốc đầu xanh chính tại A bằng 0:

`T_A = 0; T_B = t_AB; T_C = t_AB + t_BC; T_D = t_AB + t_BC + t_CD`.

`O_i = T_i mod C` biểu diễn mốc thời gian trong chu kỳ; T_i giữ ý nghĩa thời gian tích lũy, không lấy modulo từng đoạn rồi làm mất số chu kỳ đã qua.

V = 36/3.6 = 10 m/s; mỗi đoạn 300/10 = 30 s. Do đó T và O hiện tại đều là `[0,30,60,90]` giây.

| Nút | Tích lũy lý tưởng T (s) | O Baseline (s) | O Green Wave (s) |
| --- | --- | --- | --- |
| A | 0 | 0 | 0 |
| B | 30 | 0 | 30 |
| C | 60 | 0 | 60 |
| D | 90 | 0 | 90 |

Hàm `corridor_offsets` và `travel_time_seconds` đã có từ giai đoạn trước được tái sử dụng nguyên trạng. Lớp mới kiểm tra số hữu hạn, đơn vị, miền giá trị và tính khớp với mạng. Thời lượng/offset phải nằm trên lưới 1 giây cho bài kiểm chứng này; không tự làm tròn giá trị lẻ. Đổi tham số gây lệch mạng hoặc không phù hợp lưới sẽ báo lỗi.

## 4. Ánh xạ sang SUMO

Mỗi phương án dùng chương trình static riêng và cùng thứ tự 6 pha. Bộ tạo đọc các connection/linkIndex từ mạng thật; không đoán thứ tự màu theo làn.

Quy ước đã kiểm chứng trên SUMO 1.28.0:

`age_i(t) = (t - O_i) mod C`.

Lấy age để tra 6 khoảng `[0,45)`, `[45,48)`, `[48,50)`, `[50,115)`, `[115,118)`, `[118,120)`. Chúng tương ứng xanh chính, vàng chính, đỏ toàn phần, xanh ngang, vàng ngang, đỏ toàn phần. Thời gian vàng không được coi như xanh tự do.

Hai chiều trục chính cùng được xanh; hai chiều ngang cùng được xanh ở pha khác. Không có rẽ hoặc người đi bộ. Mỗi pha được đối chiếu ma trận foes (các kết nối xung đột) trong mạng; kiểm tra này không phải chứng nhận an toàn cho giao lộ thật.

Tại Green Wave D ở t=0: age=(0−90) mod120=30, nên D đang ở xanh chính thuộc khoảng bắt đầu t=−30. Xanh này kết thúc t=15; lần bật xanh mới sau mốc mô phỏng bắt đầu ở t=90. Log phân biệt sự kiện tại biên bắt đầu với pha đã đang hoạt động.

Nguồn kỹ thuật ngoài bài giảng, đối chiếu 23/10/2026:

- [SUMO Traffic Lights](https://sumo.dlr.de/docs/Simulation/Traffic_Lights.html): tlLogic, offset, phase, linkIndex và nạp chương trình từ additional-file.
- [SUMO Traffic Lights State](https://sumo.dlr.de/docs/Simulation/Output/Traffic_Lights.html): ghi trạng thái đèn bằng SaveTLSStates.

Lý do chọn XML cố định: đủ diễn tả cơ chế đã học, mở trực tiếp trên Windows, không cần TraCI, AI hoặc tối ưu phức tạp. Dấu offset không chỉ được suy luận từ tài liệu mà còn được đối chiếu từng bản ghi tín hiệu thực.

## 5. Lý tưởng khác thực tế

Khoảng cách 300 m là khoảng tâm nút; chiều dài làn ngoài nút có thể ngắn hơn do vùng giao lộ. Chưa hiệu chỉnh theo quỹ đạo, vị trí vạch dừng, hàng chờ, tăng/giảm tốc hoặc phân tán đoàn xe. Vận tốc thiết kế không đồng nhất với tốc độ trung bình đo được.

Lịch bật xanh đúng offset chưa chứng minh xe sẽ qua cả tuyến không dừng hoặc Green Wave tốt hơn. Các mốc t=20/140/260 trong đường nét đứt trên sơ đồ là ví dụ khởi hành lý tưởng tại A, không phải thời điểm xe thực tế trong log.

## 6. Luồng thực hiện

1. Đọc cấu hình và mạng đang có; xác minh tọa độ, hướng, kết nối và tốc độ.
2. Tính offset theo mốc A và kiểm tra tổng thời lượng bằng chu kỳ.
3. Tạo baseline.add.xml / greenwave.add.xml theo linkIndex thực.
4. Sao cấu hình mẫu sang hai sumocfg mới, chỉ đổi additional-files.
5. Chạy SUMO, đối chiếu trạng thái tại mọi giây và các mốc chuyển xanh.
6. Chạy lại mỗi phương án, đối chiếu hash lịch đèn và dấu vết hành trình.

Giai đoạn này không thay đổi file nguồn của GĐ2. Xem [báo cáo kiểm chứng](stage3-validation.md).
