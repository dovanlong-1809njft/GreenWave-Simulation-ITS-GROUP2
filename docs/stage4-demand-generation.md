# Cách phát sinh nhu cầu và chuẩn bị dữ liệu Giai đoạn 5

## Thuật toán

Phát xe dạng ngẫu nhiên phân tầng theo thời gian, tên phiên bản `stratified_uniform_v1`:

1. Với từng luồng riêng và từng cửa sổ (làm nóng/đo), tính `n=floor(q*T/3600)` bằng số thập phân chính xác.
2. Chia cửa sổ thành n ô bằng nhau; mỗi ô lấy đúng một thời điểm ngẫu nhiên đều.
3. PRNG (bộ sinh số giả ngẫu nhiên) dùng Python Random, seed nguyên lấy từ SHA-256 của `phiên bản|seed|luồng|cohort`. Không dùng hash() phụ thuộc phiên chạy Python.
4. Làm tròn thời điểm tới0,001 s; chặn biên phải để mọi xe vẫn nằm trong khoảng nửa kín đã công bố. Sắp xếp theo thời điểm vàID trước khi ghi.
5. Ghi xe cụ thể bằng thẻ vehicle thay vì để SUMO tự phát một flow ngẫu nhiên khác cho mỗi phương án.

Đây không phải quá trình Poisson: số xe trong từng cửa sổ cố định; seed làm thay đổi thời điểm trong các ô. Khoảng cách thời gian trung bình mục tiêu ở cửa sổ đo hướng chính là12/6/4 s cho300/600/900; từng headway không cố định và có thể ngắn hơn mức an toàn chèn xe. SUMO trì hoãn chèn nếu chưa đủ chỗ.

Ví dụ Low: floor(300×300/3600)=25 xe làm nóng; 300×3600/3600=300 xe measurement, tổng325. Luồng nền100: floor(100×300/3600)=8 xe làm nóng, không làm tròn lên thành9; tốc độ phát hữu hạn thực tế phần làm nóng là96 xe/h, phần đo đúng100 xe/h. Không tuyên bố toàn3900 s luôn đúng100 xe/h.

Seed11 tái sinh cùng nội dung; seed22/33 đổi thời điểm. Luồng nền không chứa tên mức trong seed dẫn xuất nên giữ cùng lịch giữa Low/Medium/High của cùng seed. VType sigma=0 được giữ từ mô hình cũ; thí nghiệm hiện chỉ thay sự ngẫu nhiên thời điểm đến, chưa mô phỏng đủ biến thiên người lái.

## Route, flow và ID

Route (lộ trình) là danh sách cạnh có hướng liên tục. Flow (luồng) trong thiết kế là một dòng phương tiện cùng hướng/rate; file cuối ghi từng vehicle để khóa lịch yêu cầu.

ID gồm `luồng.cohort.số_thứ_tự`, ví dụ east.measurement.00000; east nhận diện riêng tuyến ưu tiên. warmup/measurement được giữ để lọc chính xác. ID không trùng trong một lượt; cùng ID giữa hai phương án là chủ đích ghép cặp.

## Xuất phát dự kiến và thực tế

Thẻ depart trong route là thời điểm yêu cầu. Bước SUMO1 s lượng tử hóa thời điểm phục vụ; hàng chờ có thể gây chậm thêm. `actual_depart_s` lấy từ tripinfo.depart; lưu cả planned_depart_s, departDelay gốc của SUMO và hiệu actual−planned. Hai loại delay có thể khác quy ước lượng tử hóa; không coi hiệu này là chỉ số thời gian chờ trong mạng.

max-depart-delay=-1 và time-to-teleport=-1; không loại xe để làm đẹp số liệu. Xe không thể chèn được giữ ở hàng chờ ngoài mạng. Có các tùy chọn write-unfinished và write-undeparted; đồng thời dùng danh sách requested làm khung dữ liệu, nên không mất ID nếu một xe không có trip hoàn tất.

## Tệp đầu ra và các trường thật

Mỗi lượt có tripinfo.xml, summary.xml, statistics.xml, collisions.xml, A_detector.xml, stdout/stderr, run.json, validation.json và vehicles.csv. inputs/ chứa bản chụp các cấu hình, mạng, nhu cầu và đèn thực sự dùng.

| Trường CSV | Nguồn / ý nghĩa |
| --- | --- |
| planned_depart_s | depart của vehicle trong nhu cầu |
| actual_depart_s | tripinfo.depart, thời điểm thật được chèn |
| arrival_s | tripinfo.arrival nếu đã đến đích |
| travel_time_s | tripinfo.duration; xe chưa đến đích chỉ có giá trị tạm, không trộn với hành trình hoàn tất |
| waiting_time_s | tripinfo.waitingTime, tốc độ ≤0,1m/s, không gồm dừng có lịch |
| time_loss_s | tripinfo.timeLoss, chậm so với tốc độ lý tưởng của xe |
| stops_waiting_episodes | tripinfo.waitingCount, số đợt chờ ở ngưỡng ≤0,1m/s; không phải số lần ghé trạm |
| priority/cohort/status | Nhận diện hướng ưu tiên, nhóm quan sát và arrived/running/not_departed |

Giá trị không có được để trống, không gán0 cho một hành trình chưa bắt đầu. Không tổng hợp trung bình hiệu quả trong GĐ 4.

Hash tái lập hành vi được tính từ dữ liệu xe, detector và summary, bỏ thời gian tính toán `duration` của summary và phần chú thích tự sinh. Hash XML lưu trữ bỏ comment và phần performance; hash của CSV/JSON kiểm tra byte thật. Không đòi toàn bộ file SUMO XML giống byte giữa hai lượt vì ngày tạo/đường dẫn/thời gian máy có thể khác.

## Nguồn kỹ thuật bổ sung

Đối chiếu tài liệu chính thức SUMO ngày 24/10/2026:

- https://sumo.dlr.de/docs/Definition_of_Vehicles,_Vehicle_Types,_and_Routes.html — vehicle, route và thời điểm yêu cầu.
- https://sumo.dlr.de/docs/Simulation/Output/TripInfo.html — duration, waitingTime, waitingCount, timeLoss, xuất xe unfinished/undeparted.
- https://sumo.dlr.de/docs/Simulation/Output/Summary.html — inserted/arrived/running/waiting, lưu ý ended không luôn bằng arrived.
- https://sumo.dlr.de/docs/Simulation/Output/Induction_Loops_Detectors_(E1).html — đếm xe hoàn tất qua vòng từ.

Các quyết định phát xe, cửa sổ xả và cohort là thiết kế project; không gán cho Lecture04.


Mỗi lượt còn có `sealed-run.zip`: bản niêm phong được audit, chứa log gốc và snapshot đã kiểm tra. Các file rời giữ để xem nhanh; nếu chúng không khớp hash thì không dùng thay gói niêm phong.
