# Cài và chạy hai phương án trên Windows

## 1. Nền dùng để tích hợp

Cần project đã có Giai đoạn 2 chạy được: sample.sumocfg, corridor.net.xml, xe mẫu và các module model.py/validation.py.

Kiểm tra GitHub ngày 23/10/2026 ở commit `5fdcd65a2b53c892c2e3d7f154b4ff6e536e7822` thấy bản online chưa có GĐ2. Bản GĐ3 được xây trên gói GĐ2 đã bàn giao trong phiên này; không giả định clone GitHub hiện tại đã chứa tất cả file cần thiết. Không thay dữ liệu remote.

## 2. Tích hợp an toàn

ZIP chỉ có các file mới của GĐ3, không chứa thay thế README.md, config cũ, mạng, xe mẫu, sample.sumocfg hoặc thiết lập simple shapes của bạn.

Để tránh ghi đè nếu bạn đã có tệp cùng tên:

1. Giải nén ZIP vào **thư mục riêng** (ví dụ `GreenWave-Stage3` trong Downloads).
2. Mở PowerShell tại thư mục vừa giải nén.
3. Chạy, sửa đường dẫn đích nếu project của bạn ở nơi khác:

```powershell
py scripts/install_stage3.py --project "C:\Users\User\Downloads\ITS-GreenWave-Simulation"
```

Trình cài kiểm tra trước toàn bộ file: nếu đích đã có file khác nội dung thì dừng, chưa sao chép gì. File giống hệt được giữ. Không có thao tác xóa file hoặc push GitHub.

Nếu chắc chắn các tên file GĐ3 chưa tồn tại, có thể giải nén thẳng vào thư mục gốc project. Tuy nhiên cách dùng trình cài ở trên có kiểm tra xung đột trước.

## 3. Tạo và kiểm tra

Mở PowerShell tại project đã tích hợp:

```powershell
cd "C:\Users\User\Downloads\ITS-GreenWave-Simulation"
sumo --version
py scripts/build_plans.py
py scripts/verify_plans.py --static-only
py scripts/verify_plans.py
py -m unittest discover -s tests -v
```

`build_plans.py` chỉ tạo lại 4 file XML/cấu hình mới, giữ nguyên mẫu GĐ2. Chạy bước này sau tích hợp giúp sao các tùy chọn chung từ sample.sumocfg tại máy bạn. Nếu cấu hình/mạng đã khác mô hình được kiểm chứng, chương trình có thể báo lỗi thay vì âm thầm dùng tham số không khớp.

`verify_plans.py` chạy **4 lần**: Baseline hai lần và Green Wave hai lần. Mỗi lần kết thúc ở 1800 giây mô phỏng, không phải 1800 giây thực. Kiểm chứng xuất log ở `results/raw/stage3/`.

Nếu lệnh sumo không được nhận, dùng PATH/SUMO_HOME như hướng dẫn GĐ2. Script tìm PATH trước, sau đó SUMO_HOME/bin. Python chuẩn và SUMO là đủ để sinh/chạy/kiểm chứng; matplotlib chỉ cần khi vẽ lại sơ đồ.

## 4. Mở GUI

```powershell
py scripts/run_plan.py --plan baseline
py scripts/run_plan.py --plan greenwave
```

Hoặc chọn File → Open Simulation trong SUMO-GUI và mở lần lượt:

- `simulation/scenarios/baseline.sumocfg`
- `simulation/scenarios/greenwave.sumocfg`

Nhấn nút tam giác để chạy. Script không tự chạy ngay khi mở, để bạn quan sát. Dùng `--delay 100` để chỉnh tốc độ hiển thị. Không cần mở lại sample.sumocfg cho phần so sánh này.

Chạy không giao diện:

```powershell
py scripts/run_plan.py --plan baseline --cli
py scripts/run_plan.py --plan greenwave --cli
```

Cả hai dùng cùng mạng, xe mẫu, seed, bước thời gian và độ dài mô phỏng. Chỉ khác chương trình tín hiệu và offset; hình xe 2D vẫn dùng thiết lập GUI của bạn. Không tự thay đổi hồ sơ hiển thị.

## 5. Tự đối chiếu lịch đèn

Mở `results/raw/stage3/baseline-green-starts.csv` và `greenwave-green-starts.csv` trong trình soạn thảo hoặc Excel. Thời gian có đơn vị giây; các mốc đầu mong đợi:

| Nút | Baseline | Green Wave |
| --- | --- | --- |
| A | 0,120,240 | 0,120,240 |
| B | 0,120,240 | 30,150,270 |
| C | 0,120,240 | 60,180,300 |
| D | 0,120,240 | 90,210,330 |

D đã xanh ở t=0 không phải lỗi: đó là phần cuối xanh của chu kỳ trước. Log không ghi nó thành lần bật xanh mới ở 0.

Các file *-tls.csv có trạng thái ở mọi bước; verification.json chứa tham số, hash đầu vào, kết quả kiểm chứng và tính tái lập. Bản minh chứng đã chạy được lưu sẵn trong `docs/stage3-evidence/`.

## 6. Vẽ lại sơ đồ nếu cần

```powershell
# requirements.txt hiện có đã liệt kê matplotlib
py -m pip install matplotlib
py scripts/plot_signal_schedule.py --evidence results/raw/stage3
```

Nếu chỉ muốn xem thì mở PNG/SVG đã kèm theo, không cần cài thư viện vẽ. Sơ đồ dùng cửa sổ xanh/vàng/đỏ đo từ log. Đường nét đứt là quỹ đạo lý tưởng giải thích cơ chế, không phải quỹ đạo xe đo được, không phải kết luận lợi ích.

## 7. Giới hạn kiểm thử Windows

Người dùng đã xác nhận GĐ2 chạy trên Windows với SUMO 1.28.0. GĐ3 được chạy và kiểm thử tự động trên Linux/SUMO 1.28.0; chưa mở hai cửa sổ GĐ3 trên Windows. Cần bạn xác nhận thao tác GUI/PowerShell thực tế. Nếu SUMO chưa có, test tích hợp báo skipped, không được xem là đã kiểm thử thành công.
