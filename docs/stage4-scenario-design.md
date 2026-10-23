# Thiết kế thí nghiệm Giai đoạn 4

## Nền kiểm tra

Ngày kiểm tra 24/10/2026: nhánh `feature/stage3-greenwave`, commit `8089d6f282b3a99647b7aeb2ca099eb8c150b58f`, có đầy đủ GĐ 2–3. Không dùng main thay thế hoặc tự tạo file nền thiếu. Mạng, tốc độ, pha, offset, vType và các test cũ được tái sử dụng nguyên trạng.

Cơ sở ITS: docs/theory-summary.md — Lecture 02 tr. 4,13–18 về lưu lượng và vị trí đo; Lecture 04 tr. 19–31 về phối hợp và tr. 34–44 về mô phỏng. Chưa cần đọc lại PDF. Cách phát xe ngẫu nhiên phân tầng, lựa chọn luồng nền, thời gian xả và lưu snapshot là quyết định thiết kế bổ sung, không gán cho giảng viên.

## Đại lượng chuẩn

300/600/900 **xe/giờ nhu cầu dự kiến** tại đầu cạnh W_A, đi theo route `W_A A_B B_C C_D D_E`. W_A chỉ có một làn; định nghĩa vẫn là theo hướng vào mạng, không tự mở rộng thành trên mỗi làn hoặc tổng mạng.

Phân biệt:

1. Requested: xe có thời điểm xuất phát dự kiến trong tệp nhu cầu.
2. Departed/inserted: xe thật sự được SUMO chèn vào W_A; có thể trễ vì hàng chờ.
3. Observed flow: số xe hoàn tất đi qua vòng từ riêng trên A_B_0, tại pos=10 m sau A, trong [300,3900), chia 3600 s để quy đổi xe/giờ. Điểm này chỉ đo hướng ưu tiên sau A, không đo xe qua D hoặc tổng mạng.

Không dùng mật độ hay occupancy thay thế lưu lượng.

## Ma trận và luồng nền

| Mức | Nhu cầu hướng A→D (xe/h) | Xe ưu tiên làm nóng | Xe ưu tiên cửa sổ đo | Tổng xe ưu tiên | Tổng xe mọi hướng |
| --- | ---: | ---: | ---: | ---: | ---: |
| Low | 300 | 25 | 300 | 325 | 1297 |
| Medium | 600 | 50 | 600 | 650 | 1622 |
| High | 900 | 75 | 900 | 975 | 1947 |

Chiều ngược D→A: mục tiêu 100 xe/h; hai hướng ngang tại mỗi A/B/C/D: 100 xe/h **cho mỗi hướng**, tổng 8 luồng ngang. Mỗi một trong 9 luồng nền có 8 xe làm nóng và 100 xe trong cửa sổ đo, tổng 108 xe. Tốc độ, loại xe, minGap, sigma... sao từ mẫu GĐ 2; không thay tham số xe để đạt kết quả đẹp.

Mức nền là quyết định thiết kế mới vì experiments.json cũ chỉ ghi cross_direction_vehicles_per_hour=100, chưa nêu chiều ngược và ý nghĩa mỗi hướng. Dùng file riêng stage4-experiments.json để giữ cấu hình cũ và công bố đầy đủ ý nghĩa.

Ba seed 11/22/33 × ba mức × hai phương án = 18 tổ hợp. Có sáu lượt lặp seed11 để kiểm tra tái lập, không tính là sáu mẫu độc lập.

## Cửa sổ thời gian

| Khoảng | Vai trò |
| --- | --- |
| [0,300) s | Làm nóng: có phát xe, không gộp vào cohort đo |
| [300,3900) s | Phát cohort đo, đủ 3600 s/30 chu kỳ |
| [3900,7500) s | Xả xe, không phát thêm nhu cầu mới; xe đã yêu cầu trước 3900 có thể được chèn muộn |
| 7500 s | Giới hạn cứng; lưu xe chưa xuất phát/chưa đến đích, không tự xóa |

300 s không được chứng minh là đủ đạt trạng thái ổn định, nhất là khi quá tải. Lưu trạng thái tại 300,3900 và7500; không dùng hoàn tất sau xả để che tồn đọng trong cửa sổ đo.

Cohort (nhóm quan sát) xác định theo thời điểm **dự kiến** xuất phát; xe measurement chèn muộn sau 3900 vẫn thuộc nhóm đó, không bị loại khỏi mẫu. Khi phân tích GĐ 5, phân biệt thống kê cohort với thống kê theo khoảng thời gian; không lấy một vài xe hoàn thành làm đại diện.

## Tính công bằng

Mỗi cặp mức/seed dùng đúng một .rou.xml có hash chung. Cùng net, loại xe, danh sách route, thời điểm yêu cầu, seed, bước1 s, kết thúc7500 s và chính sách không teleport/không loại xe vì chậm xuất phát. Chỉ additional-files đổi từ baseline.add.xml sang greenwave.add.xml, cả hai giữ6 pha/120 s.

Mỗi lượt chạy được sao tệp đầu vào vào thư mục inputs/ trước; SUMO chạy trên bản chụp đó. Đầu vào và đầu ra có mã kiểm tra; lượt mới không được ghi đè lượt cũ.

## Năng lực mức High

Thời gian xanh chính 45/120=37,5% chu kỳ. Không tự gán năng lực bão hòa1800 xe/h hoặc hằng số chưa đo để tính khả năng phục vụ. Kiểm tra thực nghiệm bằng số xe pending/running, chậm chèn và lưu lượng quan sát sau A.

Mức900 được giữ nguyên. Dữ liệu thực tế cho thấy pending tăng qua cửa sổ đo: đây là bài thử quá tải, không phải kịch bản đã xác nhận phục vụ ổn định900 xe/h. Bảng số liệu nằm ở stage4-validation.md. Giải pháp đề xuất cho giai đoạn sau: giữ High để nghiên cứu quá tải/censoring, hoặc xin thống nhất lại phạm vi thí nghiệm. Không tự giảm900, tăng xanh, thêm làn hoặc sửa offset.
