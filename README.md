## Thành viên

| STT | Họ và tên             |    MSSV      | 
| --- | --------------------- | ------------ | 
| 1   | Văn Hoàng             |              |  
| 2   | Đỗ Văn Long           | 054205002454 | 
| 3   | Lê Minh Như           |              |
| 4   | Hoàng Minh Tâm        |              | 
| 5   | Huỳnh Nguyễn Bảo Long |              | 

# ITS GreenWave Simulation – Đề tài 9 

**Tên đề tài:** Mô phỏng và đánh giá phối hợp đèn tín hiệu theo nguyên tắc làn sóng xanh trên tuyến đường 4 giao lộ.

> **Trạng thái:** Giai đoạn 2 có mạng SUMO và xe mẫu chạy được; chưa triển khai thực nghiệm làn sóng xanh.
> **Trạng thái:** đã triển khai cấu trúc dự án .

## Mục tiêu
- 4 giao lộ A–B–C–D, ưu tiên một hướng A → D; có dòng xe ngang để mô phỏng giao lộ hợp lý.
- Hai phương án cùng chu kỳ và thời gian pha: **baseline** (độ lệch đồng thời, chưa tối ưu cho tiến trình) và **greenwave** (offset theo thời gian đi giữa nút).
- 3 mức lưu lượng giả lập: 300 / 600 / 900 xe/giờ trên hướng nghiên cứu (có thể hiệu chỉnh).
- Kết quả: thời gian hành trình, thời gian chờ, số lần dừng và tỷ lệ xe hoàn tất hành trình; so sánh hai phương án với cùng đầu vào và random seed.
- Kiểm thử code, lưu bảng và biểu đồ, viết báo cáo và trình diễn bằng SUMO-GUI.
- Đã có mạng 4 nút, xe mẫu và đèn cố định; chưa có ma trận 18 lượt so sánh baseline/greenwave.
- chương trình mô phỏng SUMO đã hoàn thiện ,giai đoạn tiếp theo cần triển khai các file mạng đường/tuyến xe/kịch bản SUMO .

## Quy ước quản lý
- `config/`: giả định mô hình và thiết kế thực nghiệm.
- `simulation/`: mô hình mạng đường, xe, các chương trình đèn SUMO.
- `src/greenwave/`: thuật toán, bộ chạy, phân tích và đồ họa bằng Python.
- `scripts/`: lệnh tiện ích từ thư mục gốc của repository.
- `tests/`: kiểm thử tự động không cần khởi động SUMO.
- `data/`: dữ liệu bổ sung; `results/`: đầu ra và biểu đồ (mặc định bị bỏ qua bởi Git).
- `docs/`: yêu cầu, giải thuật, kế hoạch mô phỏng, hướng dẫn và báo cáo.

## Nguồn học thuật và kỹ thuật
- [Tổng hợp lý thuyết, nguồn theo trang và quy tắc kiểm chứng](docs/theory-summary.md)
- Lecture 04, học phần ITS – phần điều khiển đèn liên hoàn, offset, bandwidth, mô phỏng giao thông.
- [Tài liệu SUMO](https://sumo.dlr.de/docs/)
- [Traffic lights SUMO](https://sumo.dlr.de/docs/Simulation/Traffic_Lights.html)

## Windows PowerShell
```powershell
# Clone từ GitHub sau khi tạo repository và push bộ khung này
cd ITS-GreenWave-Simulation
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts/check_environment.py
python scripts/preview_offsets.py
python -m unittest discover -s tests -v
```
Để chạy mẫu giai đoạn 2, xem `docs/stage2-windows.md`. Kế hoạch so sánh hai phương án trong `docs/experiment-plan.md` thuộc giai đoạn sau.

## Chạy mô hình giai đoạn 2

Mở `simulation/scenarios/sample.sumocfg` trong SUMO-GUI rồi nhấn chạy.

```powershell
py scripts/run_sample.py
py scripts/validate_sample.py --run
```

[Hướng dẫn Windows và vai trò từng file](docs/stage2-windows.md) · [Kết quả kiểm thử](docs/stage2-validation.md).
Để chạy **mô phỏng giao thông**, cần cài SUMO/NETEDIT và thực hiện các TODO trong `simulation/`; xem `docs/setup.md` và `docs/experiment-plan.md`.

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
