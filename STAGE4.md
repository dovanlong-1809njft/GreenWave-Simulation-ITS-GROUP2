# Giai đoạn 4 — Nhu cầu và kịch bản lưu lượng

**Trạng thái:** đã triển khai và chạy kiểm tra bộ kịch bản; mức High bộc lộ quá tải, vì vậy chưa đánh dấu nghiệm thu toàn bộ khả năng phục vụ của ba mức. Chưa làm phân tích thống kê hoặc kết luận hiệu quả Giai đoạn 5.

- [Thiết kế kịch bản và định nghĩa lưu lượng](docs/stage4-scenario-design.md)
- [Thuật toán phát sinh nhu cầu](docs/stage4-demand-generation.md)
- [Kết quả kiểm tra và giới hạn](docs/stage4-validation.md)
- [Hướng dẫn Windows](docs/stage4-windows.md)
- [Danh sách file](docs/stage4-file-manifest.json)

```powershell
py scripts/build_scenarios.py
py scripts/verify_scenarios.py
py scripts/run_experiments.py --seed 11
py scripts/run_scenario.py --level high --plan baseline --seed 11
py -m unittest discover -s tests -v
```

Mỗi lệnh chạy thí nghiệm tạo batch mới dưới results/raw/stage4/. File mẫu, mạng, lịch đèn và 20 test trước đó được giữ nguyên. experiments.json cũ không bị sửa; config/stage4-experiments.json công bố rõ phần mở rộng còn thiếu trong cấu hình cũ.
