# Cơ sở lý thuyết ITS cho mô phỏng làn sóng xanh

Ngày đối chiếu: 23/10/2026. Tài liệu dùng trước khi lập trình và khi giải thích báo cáo.
Đây là bản tổng hợp theo phạm vi project, không phải bản chép toàn bộ bài giảng hoặc yêu cầu chính thức của giảng viên.

## 1. Quy tắc sử dụng nguồn và tiết kiệm thao tác

- Đọc bản tổng hợp này và các file mã nguồn liên quan trước; không đọc lại toàn bộ PDF ở mỗi giai đoạn.
- Chỉ mở PDF gốc ở trang cần xác minh công thức, ký hiệu, hình hoặc nội dung còn thiếu.
- Chỉ kiểm tra module đang sửa và thành phần phụ thuộc; không quét lại toàn bộ repository (kho mã nguồn) khi không cần.
- Vẫn chạy kiểm thử phù hợp; phân biệt kiểm thử Python, kiểm thử tích hợp SUMO và thực nghiệm đánh giá.
- Khi thêm phương pháp ngoài bài giảng, ghi lý do, nguồn và cách kiểm chứng ngay tại mục liên quan.
- Không gán giả định thiết kế, dữ liệu mẫu hoặc kết quả chưa đo cho giảng viên.

## 2. Danh mục nguồn và quy ước trang

Số trang dưới đây là số trang PDF, tính từ 1. Lecture 04 có số hiển thị `04.n` tương ứng trang n; Lecture 01 và 02 có các trang trình chiếu tăng dần nội dung nên số trang PDF có thể khác số slide hiển thị.

| Mã | Tệp nguồn | Phần cần dùng |
| --- | --- | --- |
| L04 | `lecture-04(2).pdf` | Tr. 5–17: các chiến lược; tr. 18–31: phối hợp đèn; tr. 34–50: mô phỏng |
| L02 | `lecture-02(3).pdf` | Tr. 4, 13–19, 21: đại lượng dòng xe, phương pháp quan trắc |
| L01 | `lecture-01(2).pdf` | Tr. 20 (slide 01.10), 24 (01.12), 39 (01.24): mục đích ứng dụng ITS |
| L03 | `lecture-03(2).pdf` | Tr. 2: phạm vi quản lý và phát hiện sự cố; chưa cần triển khai cho kịch bản hiện tại |
| L05 | `lecture-05(2).pdf` | Tr. 5, 8: định vị xe và ưu tiên xe buýt; chỉ liên quan nếu mở rộng |
| GT | `Giaotrinh - Van Hong Tan - 2006 -He Thong Giao Thong Thong Minh-ITS(2).pdf` | Tài liệu đối chiếu bổ sung; chưa dùng làm nguồn cho công thức trong bản này |

## 3. Kiến thức từ Lecture 04

### 3.1. Điều khiển cố định và phối hợp

[Bài giảng: L04, tr. 5–15]

- Pretimed (định thời sẵn): thời gian tín hiệu được xác định trước; khác với actuated control (điều khiển kích hoạt) dựa trên cảm biến.
- Uncoordinated control (không phối hợp): không xét hoạt động các đèn lân cận.
- Time-based coordinated control (phối hợp theo thời gian): dùng kế hoạch thời gian để hỗ trợ đoàn xe đi qua tuyến.
- Bài giảng còn giới thiệu các dạng điều chỉnh, đáp ứng và thích nghi. Chúng không bắt buộc phải được triển khai trong project này.

[Lựa chọn của project]

Dùng phối hợp định thời theo một hướng trước, phù hợp hàm offset hiện có và dễ giải thích theo L04. Không tự bổ sung AI, học tăng cường hoặc điều khiển thích nghi.
Baseline (phương án đối chứng) hiện đặt mọi offset bằng 0: gọi chính xác là phương án đồng thời chưa tối ưu cho tiến trình; không đồng nhất nó với mọi dạng điều khiển không phối hợp.

### 3.2. Làn sóng xanh và điều kiện phối hợp

[Bài giảng: L04, tr. 19–21]

Green wave (làn sóng xanh) điều chỉnh thời điểm bật xanh tại các nút kế tiếp để hỗ trợ platoon (đoàn xe) vượt nhiều nút mà không dừng.
Hiệu quả phụ thuộc khả năng dự đoán đoàn xe đến nút; khoảng cách quá xa có thể làm đoàn xe phân tán.
Bài giảng nêu chu kỳ chung để phối hợp, đồng thời nêu trường hợp nút có lưu lượng lớn dùng chu kỳ gấp đôi. Phạm vi hiện tại chỉ dùng chu kỳ chung.

Không suy ra rằng mọi xe đều không dừng hoặc rằng phối hợp luôn tốt hơn đối chứng ở mọi mức lưu lượng.

### 3.3. Chu kỳ, offset và mốc tham chiếu

[Bài giảng: L04, tr. 21, 24–27]

- Cycle C (chu kỳ): khoảng thời gian lặp lại chương trình tín hiệu.
- Offset (độ lệch): chênh lệch thời điểm bắt đầu xanh giữa hai nút theo hướng xét.
- Offset lý tưởng một chiều giữa hai nút: `O_ideal = L / V`.
- L: khoảng cách giữa hai đèn; V: tốc độ trung bình dòng xe. Để kết quả là giây, dùng L theo mét và V theo m/s; `V_mps = V_kmh / 3.6`.

[Suy ra để lập trình, không phải công thức được chép nguyên văn từ slide]

Đặt nút A làm mốc thời gian 0. Với thời gian đi đoạn j là `t_j = L_j / V`, offset nút i theo mốc A được biểu diễn bằng:

`O_A = 0; O_i = (t_1 + ... + t_i) mod C`.

Cộng dồn chuyển độ lệch giữa hai nút sang mốc chung; modulo (phép lấy phần dư) đưa thời điểm về một chu kỳ. Công thức này phù hợp chu kỳ chung và giả thiết tốc độ thiết kế cố định.
Ví dụ tính toán, không phải thực nghiệm: ba đoạn 300 m, tốc độ 36 km/h, C = 120 s cho `[0, 30, 60, 90]` giây.

Trong code hiện tại, `src/greenwave/algorithms/offset.py` thực hiện phép tính này. Nó chưa chứng minh chương trình đèn SUMO bắt đầu xanh đúng tại các mốc trên.

### 3.4. Biểu đồ thời gian–không gian

[Bài giảng: L04, tr. 22–23, 29–30]

Time–space diagram (biểu đồ thời gian–không gian) biểu diễn vị trí các giao lộ, các khoảng tín hiệu và chuyển động theo thời gian. Hình ở tr. 23 đặt thời gian trên trục ngang, khoảng cách trên trục đứng.
Quỹ đạo đoàn xe cần đi qua các cửa sổ xanh liên tiếp. Biểu đồ dùng để giải thích offset và xác định dải xanh xuyên tuyến.

[Đề xuất triển khai]

Vẽ thời gian bắt đầu/kết thúc xanh ở từng nút từ chương trình thực tế đã nạp; thể hiện nhiều chu kỳ để tránh sai ở biên modulo. Phân biệt đường quỹ đạo lý tưởng với quỹ đạo xe lấy từ mô phỏng.

### 3.5. Băng thông xanh và công thức đánh giá lý thuyết

[Bài giảng: L04, tr. 28]

- Bandwidth BW (băng thông xanh, giây): khoảng thời gian xanh hữu hiệu cho đoàn xe đi xuyên chuỗi tín hiệu.
- Bandwidth efficiency (hiệu suất băng thông): `BE = BW / C * 100%`.
- Bandwidth capacity (năng lực thông qua theo băng thông): `BC = 3600 * BW * N / (C * h)`.
- N: số làn theo hướng xét; h: headway (giãn cách thời gian) giữa hai xe trong đoàn, tính bằng giây/xe; BC có đơn vị xe/giờ.

BW phải được xác định từ sự phối hợp các cửa sổ xanh và thời gian đi; không lấy thời gian xanh của một nút bất kỳ làm BW cho toàn tuyến.
Bài giảng nêu hiệu suất xấp xỉ 50% là hữu hiệu; đây không phải tiêu chí nghiệm thu bắt buộc của giảng viên đối với project.
BC là đại lượng lý thuyết theo các giả thiết trên, không phải số xe hoàn tất hành trình đo được trong SUMO.

[Bài giảng: L04, tr. 29–31]

Ví dụ trên slide dùng C = 80 s; BW hai hướng lần lượt 35 s và 6 s, BE tương ứng 43.75% và 7.5%. Đây là ví dụ bài giảng, không phải kết quả project. Phối hợp tốt một chiều có thể bất lợi cho chiều ngược lại.

### 3.6. Xanh hữu hiệu và tín hiệu mô phỏng

[Bài giảng: L04, tr. 24]

Slide mô tả effective green (xanh có hiệu) bằng cách diễn giải giản lược liên quan xanh và vàng.

[Giới hạn khi chuyển sang mô hình]

Không tự coi toàn bộ thời gian vàng là thời gian mọi xe mới được phép vào nút. Phải tách xanh hiển thị, vàng, đỏ toàn phần và giả thiết xanh hữu hiệu khi tính BW. Chưa chốt cách quy đổi xanh hữu hiệu trong project; cần ghi rõ trước khi triển khai tính BW.

### 3.7. Cơ sở mô phỏng

[Bài giảng: L04, tr. 34, 36, 39, 41–49]

- Đầu vào: mạng đường và nhu cầu di chuyển; đầu ra: kết quả phân tích và biểu diễn đồ họa.
- Mô phỏng cho phép so sánh phương án trong điều kiện có kiểm soát; độ chi tiết và mức sát thực bị giới hạn bởi mô hình và tài nguyên.
- Quy trình tr. 44: xác định bài toán, nghiên cứu đầu vào, phát triển logic, xây dựng chương trình, canh chỉnh, kiểm tra đánh giá.
- Car-following (xe theo xe) và lane-changing (chuyển làn) là các thành phần hành vi được giới thiệu. Không khẳng định mô hình mặc định của SUMO chính là phương trình ví dụ trong slide nếu chưa đối chiếu.

Mạng giả lập chưa hiệu chỉnh bằng khảo sát chỉ cho kết luận trong phạm vi giả lập, chưa đại diện một tuyến đường thực.

## 4. Đối chiếu các bài giảng liên quan

| Nguồn đã đối chiếu | Ý nghĩa cho project |
| --- | --- |
| L01 tr. 20, 24, 39 | Điều khiển tín hiệu và mô phỏng là ứng dụng ITS; giảm dừng là mục tiêu, không phải kết quả đã đạt |
| L02 tr. 4, 13 | Phân biệt lưu lượng, tốc độ, mật độ, thời gian hành trình và occupancy (tỷ lệ thời gian chiếm dụng) |
| L02 tr. 15–18 | Dữ liệu tại điểm khác dữ liệu trên đoạn; không dùng số xe qua điểm như mật độ trực tiếp, không đồng nhất occupancy với mật độ |
| L02 tr. 19 | Xe thăm dò có giới hạn đại diện; không coi một xe hoặc một tốc độ đặt trước là tốc độ trung bình đo được của mọi xe |
| L02 tr. 21 | Quan trắc gồm dò tìm, phần cứng, phần mềm và thông tin; trong project dùng dữ liệu mô phỏng, không khẳng định đã có cảm biến thật |
| L03 tr. 2 | Quản lý/phát hiện sự cố là hướng riêng; không cần thêm giải thuật phát hiện sự cố cho mô hình phối hợp định thời hiện tại |
| L05 tr. 5, 8 | AVL là định vị xe; ưu tiên bus có thể điều chỉnh xanh/đỏ và phải chú ý phối hợp. Không tự thêm ưu tiên bus vào phạm vi hiện tại |

## 5. Phân biệt kỹ thuật SUMO/Python với lý thuyết giảng dạy

[Nguồn ngoài bài giảng, chính thức]

SUMO, “Traffic Lights”: https://sumo.dlr.de/docs/Simulation/Traffic_Lights.html (đối chiếu ngày 23/10/2026).
Các mục cần tra: Defining New TLS-Programs, tlLogic Attributes, phase Attributes và Signal state definitions.

Đề xuất dùng chương trình đèn cố định, khai báo các pha và độ lệch trong SUMO; lý do là giữ mô hình gần phương pháp định thời đã học. Python tính tham số, tổ chức chạy và tổng hợp dữ liệu. Đây là lựa chọn kỹ thuật của project, không phải yêu cầu từ slide.
TraCI là lựa chọn kết nối Python với mô phỏng nếu cần; không mặc định phải dùng để điều khiển từng bước.

Trước khi áp dụng offset, phải kiểm tra quy ước thời gian của SUMO bằng trạng thái đèn thực tế. Không chép thẳng giá trị offset lý thuyết vào thuộc tính phần mềm rồi mặc định đúng mốc bật xanh.
Phải kiểm tra ánh xạ tín hiệu sang các kết nối qua nút và thứ tự pha; không tự suy đoán chuỗi ký tự trạng thái.

## 6. Các giá trị hiện có là giả định thiết kế

Nguồn: `README.md`, `config/signals.json`, `docs/experiment-plan.md`, `docs/requirements.md` trong ZIP đã cung cấp.

- Tuyến 4 nút A–B–C–D, ưu tiên A → D.
- Chu kỳ 120 s; tốc độ thiết kế 36 km/h.
- Pha hiện có: xanh chính 45, vàng 3, đỏ toàn phần 2, xanh ngang 65, vàng 3, đỏ toàn phần 2 (giây); tổng 120 s.
- Nhu cầu 300/600/900 xe/giờ; dòng ngang dự kiến 100 xe/giờ; khởi động 300 s, đo 3600 s; seed (hạt giống ngẫu nhiên) 11/22/33.
- Ma trận dự kiến: 2 phương án × 3 mức nhu cầu × 3 seed = 18 lượt, chưa phải 18 kết quả đã chạy.

Những con số này không phải yêu cầu đã xác nhận của giảng viên hoặc số liệu khảo sát. Cần thống nhất đơn vị lưu lượng theo hướng/làn và khoảng đo khoảng cách giữa nút trước khi xây dựng mạng.

## 7. Kiểm chứng cần thực hiện khi lập trình

1. Kiểm thử tính L/V, đổi đơn vị, cộng dồn và modulo; đối chiếu ví dụ tính tay.
2. Kiểm tra tổng thời lượng pha bằng chu kỳ, kết nối xe hợp lệ và các dòng xung đột không cùng được cấp quyền đi ưu tiên.
3. Ghi thời điểm bật xanh thực tế theo nút để kiểm tra offset, kể cả qua ranh giới chu kỳ.
4. Nếu tính BW: kiểm tra giao các cửa sổ xanh theo thời gian đi; có trường hợp BW bằng 0 và trường hợp đi qua biên chu kỳ.
5. So sánh hai phương án cùng mạng, nhu cầu, thời gian pha và seed. Không chỉ so các xe hoàn thành khi tỷ lệ xe chưa hoàn thành khác biệt lớn.
6. Định nghĩa rõ cửa sổ đo, thời gian chờ, ngưỡng dừng, cách đếm một lần dừng và xử lý xe chưa hoàn thành trước khi báo cáo kết quả.
7. Phân biệt tốc độ thiết kế, tốc độ xe đo được, nhu cầu đưa vào và lưu lượng thực tế qua điểm đo.

Trạng thái cập nhật giai đoạn 2: đã tạo mạng và chạy xe mẫu bằng SUMO; bằng chứng kiểm thử ở `docs/stage2-validation.md`. Chưa có kết quả so sánh hiệu quả làn sóng xanh. Kiểm thử xe mẫu không thay cho thực nghiệm đánh giá phối hợp đèn.
