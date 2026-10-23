# Giai đoạn 2: chạy mô hình SUMO mẫu trên Windows

## 1. Kết quả bàn giao

Mô hình giả lập W–A–B–C–D–E, bốn nút A/B/C/D có đèn; W và E là biên mạng. Các tâm nút cách nhau 300 m, đoạn biên dài 200 m. Mỗi nút có nhánh bắc/nam dài 150 m. Đây là kích thước thiết kế, không phải khảo sát hiện trường.

Mỗi chiều có một làn, chạy bên phải; vận tốc tối đa 36 km/h. Có hai chiều trên trục chính và hai chiều qua đường ngang. Chỉ đi thẳng, không rẽ, không quay đầu, không có người đi bộ. Chọn mô hình này để kiểm tra tính thông suốt và tín hiệu trước khi đánh giá phối hợp.

Khoảng cách 300 m là giữa tâm nút. Chiều dài làn bên ngoài nút trong `.net.xml` có thể ngắn hơn do hình học giao lộ; không được tự dùng nó làm cùng một đại lượng khi tính offset ở giai đoạn sau.

Xe mẫu: 30 xe W→E qua đủ A/B/C/D (vàng cam), 15 xe E→W (xanh dương), 5 xe mỗi hướng ngang tại mỗi nút (xanh lá), tổng 85 xe. Xe được phát trong 0–360 s, mô phỏng kết thúc ở 1800 s. Đây là bài kiểm tra mô hình, chưa phải ma trận thí nghiệm lưu lượng.

Đèn đồng thời, offset 0 và chu kỳ 120 s:

| Khoảng trong chu kỳ (s) | Đường chính | Đường ngang |
| --- | --- | --- |
| [0,45) | Xanh | Đỏ |
| [45,48) | Vàng | Đỏ |
| [48,50) | Đỏ | Đỏ |
| [50,115) | Đỏ | Xanh |
| [115,118) | Đỏ | Vàng |
| [118,120) | Đỏ | Đỏ |

Các thời gian trên lấy từ `config/signals.json`, là giả định project. Chưa áp dụng làn sóng xanh. Cơ sở học thuật: `docs/theory-summary.md`, L04 tr. 5–15, 19–31. Không dùng thời gian vàng như một cửa sổ xanh cho mọi xe.

## 2. Giải nén và mở trực tiếp

1. Giải nén ZIP **vào thư mục gốc project hiện tại**, nơi có README.md và config/. Chấp nhận thay thế các file đã sửa.
2. Cài SUMO bản desktop cho Windows, có SUMO-GUI và NETCONVERT. Bản đã kiểm thử ở đây là SUMO 1.28.0 trên Linux. Chưa chứng nhận các bản SUMO cũ hơn.
3. Mở SUMO-GUI, chọn **File → Open Simulation**, mở `simulation/scenarios/sample.sumocfg`.
4. Nhấn nút chạy hình tam giác hoặc Ctrl+A. Đặt Delay khoảng 100 ms nếu chạy quá nhanh. Phóng to các nút để nhìn đèn và phương tiện.
5. Trục chính có bốn nút có đèn, lần lượt A–B–C–D từ trái sang phải. Di chuột/nhấp phải vào nút để xem ID; có thể bật hiển thị tên nút trong thiết lập hiển thị của GUI.

Đã có sẵn `.net.xml`; mở trực tiếp không cần cài thư viện Python, không cần chạy netconvert trước. Giữ nguyên cây thư mục vì `.sumocfg` dùng đường dẫn tương đối.

## 3. Chạy bằng PowerShell

Tại thư mục gốc project:

```powershell
# Nếu chưa nhận lệnh SUMO, chỉnh đường dẫn theo nơi đã cài trên máy bạn
$env:SUMO_HOME = "C:\Program Files (x86)\Eclipse\Sumo"
$env:Path = "$env:SUMO_HOME\bin;$env:Path"
sumo --version
netconvert --version

# Python chuẩn là đủ cho các script giai đoạn 2
py scripts/build_network.py
py scripts/validate_sample.py
py scripts/validate_sample.py --run
py -m unittest discover -s tests -v
py scripts/run_sample.py
```

`SUMO_HOME` chỉ là đường dẫn ví dụ; không thay đổi nếu môi trường hiện tại đã đúng. Script tìm chương trình trên PATH trước, rồi SUMO_HOME/bin. Không cần cài lại Python hoặc tạo lại môi trường ảo đã có.

`py scripts/run_sample.py --cli` chạy mẫu không giao diện. `run_sample.py` mở GUI ở trạng thái chờ để bạn nhấn chạy. Có thể chạy script từ thư mục khác vì đường dẫn được tính từ vị trí script.

## 4. Vai trò các file

| Đường dẫn | Ý nghĩa |
| --- | --- |
| `simulation/network/source/corridor.nod.xml` | Nodes: tọa độ nút và kiểu nút |
| `simulation/network/source/corridor.edg.xml` | Edges: đường có hướng, làn và tốc độ |
| `simulation/network/source/corridor.con.xml` | Connections: kết nối làn, chỉ cho đi thẳng |
| `simulation/network/generated/corridor.net.xml` | Mạng hoàn chỉnh do NETCONVERT sinh; không sửa thủ công |
| `simulation/signals/fixed.add.xml` | Chương trình đèn cố định, dùng ánh xạ linkIndex thực từ mạng |
| `simulation/routes/source/sample.rou.xml` | Tuyến và các luồng xe mẫu |
| `simulation/scenarios/sample.sumocfg` | Cấu hình tổng để mở bằng SUMO/SUMO-GUI |
| `src/greenwave/simulation/model.py` | Sinh các nguồn XML và gọi NETCONVERT |
| `src/greenwave/simulation/validation.py` | Kiểm tra cấu trúc và mô phỏng tích hợp |
| `scripts/build_network.py` | Lệnh tạo lại toàn bộ mô hình mẫu |
| `scripts/run_sample.py` | Mở GUI hoặc chạy dòng lệnh |
| `scripts/validate_sample.py` | Kiểm tra cấu trúc, thêm --run để chạy thử SUMO |
| `tests/test_sumo_model.py` | Kiểm thử kết nối, xung đột tín hiệu và tích hợp |

`.xml` lưu dữ liệu có cấu trúc; các hậu tố nod/edg/con/net/rou phân biệt vai trò. `.sumocfg` cũng là XML, dùng để gom cấu hình. `.py` là mã Python, `.md` là tài liệu Markdown.

## 5. Tái tạo và giới hạn

`build_network.py` đọc config/network.json và config/signals.json, tạo nguồn, gọi NETCONVERT rồi đọc linkIndex thực để sinh chương trình đèn. Không giả định thứ tự kết nối. Mạng có chương trình mặc định của NETCONVERT; sample.sumocfg nạp chương trình `fixed` riêng. Không mở riêng .net.xml nếu muốn chạy đúng xe mẫu và chu kỳ bàn giao.

Khi đổi thông số: chạy lại build, validate --run và tests; không chỉnh riêng .net.xml rồi kỳ vọng nguồn vẫn khớp. File sinh có thể bị ghi đè. Bộ kiểm tra giai đoạn này cố ý khóa các kỳ vọng của mẫu 120 s/85 xe; khi mở rộng phải cập nhật thiết kế kiểm thử cùng mô hình.

Chưa có mô hình giao thông thực, rẽ, người đi bộ, điều khiển thích nghi, thuật toán làn sóng xanh nâng cao, biểu đồ hoặc các mức lưu lượng thực nghiệm. Không thay kiến trúc Frontend/Backend/Database.

## 6. Nguồn kỹ thuật bổ sung

Đối chiếu ngày 23/10/2026, tài liệu chính thức SUMO:

- PlainXML: https://sumo.dlr.de/docs/Networks/PlainXML.html — tách nguồn nút/đường/kết nối, dùng NETCONVERT tạo mạng.
- Traffic Lights: https://sumo.dlr.de/docs/Simulation/Traffic_Lights.html — chương trình cố định, các pha, ánh xạ kết nối/tín hiệu.
- SUMO: https://sumo.dlr.de/docs/sumo.html — nạp cấu hình và dữ liệu đầu vào.

Các khai báo XML, cách gọi chương trình và cơ chế kiểm thử là giải pháp kỹ thuật bổ sung; công thức và nguyên tắc ITS vẫn theo tài liệu tổng hợp đã dẫn trang bài giảng.
