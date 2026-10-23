# Thiết lập và chạy trên Windows

Mô hình giai đoạn 2 đã có sẵn. Xem [hướng dẫn từng bước](stage2-windows.md).

Mở trực tiếp `simulation/scenarios/sample.sumocfg` trong SUMO-GUI rồi nhấn chạy.

```powershell
py scripts/build_network.py
py scripts/validate_sample.py --run
py -m unittest discover -s tests -v
py scripts/run_sample.py
```

Các script giai đoạn 2 chỉ dùng thư viện chuẩn Python. `requirements.txt` vẫn phục vụ các giai đoạn phân tích/TraCI sau; SUMO desktop phải cài riêng. Chưa có các file kịch bản low/medium/high.
