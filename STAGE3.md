# Giai đoạn 3 — Baseline và Green Wave

Bản bổ sung này chỉ thêm file mới, không sửa config/network.json, config/signals.json, mạng, xe mẫu, sample.sumocfg hoặc tùy chỉnh GUI cũ. Không push GitHub.

- [Cách cài và chạy Windows](docs/stage3-windows.md)
- [Thuật toán và cơ sở lý thuyết](docs/stage3-algorithm.md)
- [Kết quả kiểm chứng và giới hạn](docs/stage3-validation.md)
- [Danh sách thay đổi](docs/stage3-changes.md)
- [Sơ đồ thời gian–không gian](docs/stage3-evidence/time-space.png)

```powershell
py scripts/build_plans.py
py scripts/verify_plans.py
py -m unittest discover -s tests -v
py scripts/run_plan.py --plan baseline
py scripts/run_plan.py --plan greenwave
```

Hai cửa sổ GUI mở riêng hoặc lần lượt; nhấn nút tam giác để chạy. Chỉ kiểm chứng cơ chế, chưa so sánh hiệu quả lưu lượng.
