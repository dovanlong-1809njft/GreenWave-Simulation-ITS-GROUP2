# Cài đặt môi trường / Setup Guide (Windows)

1. Cài Python 3.11+ và Git.
2. Tải và cài SUMO từ https://sumo.dlr.de/docs/Downloads.php (có SUMO-GUI, NETEDIT, NETCONVERT).
3. Kiểm tra `sumo --version`, `netconvert --version` trên PowerShell; nếu không nhận, thêm thư mục `bin` SUMO vào PATH.
4. Tại repository:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python scripts/check_environment.py
python scripts/preview_offsets.py
python -m unittest discover -s tests -v
```

5. Sau khi nhóm hoàn thành mạng đường, routes, `sumocfg`, mở mô hình bằng:

```powershell
# CHỈ sử dụng sau khi đã tạo file sumocfg tương ứng
sumo-gui -c simulation/scenarios/generated/low_greenwave_seed11.sumocfg
```

Tên `low_greenwave_seed11.sumocfg` là **quy ước dự kiến**, chưa có sẵn trong bộ khung.
