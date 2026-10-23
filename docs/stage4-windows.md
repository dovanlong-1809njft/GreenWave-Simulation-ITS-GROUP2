# Hướng dẫn Giai đoạn 4 trên Windows

## Tích hợp có kiểm tra xung đột

Giải nén ZIP vào thư mục riêng, mở PowerShell tại đó:

```powershell
py scripts/install_stage4.py --project "C:\Users\User\Downloads\ITS-GreenWave-Simulation"
```

Trình cài kiểm tra mọi tệp trước khi ghi; dừng nếu tệp mới trùng tên nhưng khác nội dung. Riêng README được ghép thêm một mục GĐ 4, giữ toàn bộ phần trước. Không xóa file, không push, không thay mạng/lịch đèn hay test GĐ 2–3. Không khuyến nghị giải nén đè trực tiếp README nếu bạn đã chỉnh nó.

## Môi trường đúng theo máy người dùng

```powershell
cd "C:\Users\User\Downloads\ITS-GreenWave-Simulation"
$env:SUMO_HOME = "C:\Program Files (x86)\SUMO"
$env:Path = "$env:SUMO_HOME\bin;$env:Path"
py --version
sumo --version
```

Mục tiêu tương thích Python 3.13.12 / SUMO 1.28.0. GĐ 4 chỉ dùng thư viện chuẩn Python; không cần TraCI/pandas hoặc công cụ nặng. Đã kiểm thử thực tế Linux/Python 3.12/SUMO 1.28.0, chưa chạy GĐ 4 trên Windows. Người dùng đã xác nhận20 test GĐ 3 chạy đạt trên Windows; điều đó không thay cho kiểm thử Windows của GĐ 4.

## Tạo và kiểm tra cấu hình

```powershell
py scripts/build_scenarios.py
py scripts/verify_scenarios.py
py -m unittest discover -s tests -v
```

Mặc định tạo9 tệp nhu cầu và18 cấu hình cho seeds11/22/33. Muốn chọn:

```powershell
py scripts/build_scenarios.py --level high --seed 11
py scripts/verify_scenarios.py --level high --seed 11
```

Sinh lại cùng cấu hình là idempotent (không đổi nội dung). Nếu đích đã có dữ liệu khác, lệnh dừng trước khi ghi; không dùng --force. Khi chủ động đổi thiết kế, hãy lưu các tệp sinh cũ ở thư mục riêng trước khi tái tạo và ghi nhận thay đổi thí nghiệm.

## Chạy thí nghiệm có dữ liệu đầu ra

```powershell
# Sáu tổ hợp, seed11
py scripts/run_experiments.py --seed 11
# Mở rộng18 tổ hợp
py scripts/run_experiments.py --seed 11 22 33
# Một tổ hợp cụ thể
py scripts/run_experiments.py --level high --plan baseline --seed 11
```

Mỗi lệnh tạo batch có timestamp duy nhất dưới results/raw/stage4/. Có thể chọn --batch-id ten_moi; nếu đã tồn tại thì dừng, không ghi đè. Kết quả completed_with_limits/finished_with_capacity_limits biểu thị giới hạn tồn đọng, không phải lỗi XML; không coi đó là nghiệm thu năng lực900 xe/h.

Lưu lại đường dẫn batch được in ở cuối. Ví dụ kiểm tra sau chạy:

```powershell
py scripts/verify_scenarios.py --results results/raw/stage4/TEN_BATCH
# Tạo một batch lặp rồi so với batch đầu, cùng các tổ hợp vàseed
py scripts/verify_scenarios.py --results results/raw/stage4/BATCH_DAU --compare results/raw/stage4/BATCH_LAP
```

Không xóa requested/unfinished để tăng tỷ lệ hoàn tất. Lượt chạy có lỗi giữ stdout/stderr và manifest lỗi; chưa được coi là có dữ liệu hợp lệ.

## Mở từng tổ hợp trong GUI

```powershell
py scripts/run_scenario.py --level low --plan baseline --seed 11
py scripts/run_scenario.py --level low --plan greenwave --seed 11
py scripts/run_scenario.py --level medium --plan baseline --seed 11
py scripts/run_scenario.py --level medium --plan greenwave --seed 11
py scripts/run_scenario.py --level high --plan baseline --seed 11
py scripts/run_scenario.py --level high --plan greenwave --seed 11
```

Hoặc File → Open Simulation rồi chọn simulation/scenarios/experiments/{level}_{plan}_seed11.sumocfg. Nhấn nút tam giác; thời gian mô phỏng tới 7500 s bao gồm xả, xe mới được yêu cầu chỉ trước 3900 s. Script GUI phục vụ quan sát; dùng run_experiments.py để có snapshot và dữ liệu đầy đủ. Không thay profile simple shapes của bạn.

## Bằng chứng đã kèm

docs/stage4-evidence/raw-runs.zip chứa các lượt đã kiểm tra. Nếu muốn kiểm tra lại, giải nén vào thư mục **mới** ví dụ results/raw/stage4-delivered (không dùng Force đè dữ liệu cũ), rồi chạy audit với đường dẫn hai batch bên trong. Mỗi case được giao bằng sealed-run.zip; mở gói này để xem tripinfo.xml/vehicles.csv hoặc giải nén vào thư mục riêng. Audit đọc trực tiếp các gói, không đòi giải nén từng case. Các CSV tổng kiểm tra và JSON ở docs/stage4-evidence/ để xem nhanh mà không cần giải nén dữ liệu thô.

Các tệp generated và kết quả có thể bị .gitignore hiện tại bỏ qua. Mã nguồn/config mới được theo dõi bình thường; sinh lại nhu cầu bằng script, hoặc chủ động chọn cách quản lý bản snapshot trong nhóm. Không tự thay .gitignore hay push dữ liệu thay bạn.

Ví dụ sau khi giải nén raw-runs.zip vào thư mục mới results/raw/stage4-delivered:

```powershell
py scripts/verify_scenarios.py --results results/raw/stage4-delivered/sealed_primary --compare results/raw/stage4-delivered/sealed_repeat
```
