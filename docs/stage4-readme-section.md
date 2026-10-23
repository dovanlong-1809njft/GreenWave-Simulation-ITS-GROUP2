<!-- STAGE4:BEGIN -->
## Giai đoạn 4 — kịch bản nhu cầu và dữ liệu thô

Đã có bộ tạo 300/600/900 xe/giờ theo hướng W_A→A→D, nhu cầu dùng chung giữa hai phương án, script chạy/kiểm tra và log có snapshot đầu vào. **Mức 900 xe/giờ có giới hạn năng lực; chưa nghiệm thu toàn bộ như một trạng thái phục vụ ổn định.** Chưa kết luận Green Wave hiệu quả hơn.

Xem [STAGE4.md](STAGE4.md), [thiết kế](docs/stage4-scenario-design.md), [kiểm thử](docs/stage4-validation.md), [Windows](docs/stage4-windows.md).

```powershell
py scripts/build_scenarios.py
py scripts/verify_scenarios.py
py scripts/run_experiments.py --seed 11
```
<!-- STAGE4:END -->
