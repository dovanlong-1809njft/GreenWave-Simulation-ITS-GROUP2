<<<<<<< HEAD
# ITS GreenWave Simulation – Đề tài 9 (mức 2)

**Tên đề tài:** Mô phỏng và đánh giá phối hợp đèn tín hiệu theo nguyên tắc làn sóng xanh trên tuyến đường 4 giao lộ.

> **Trạng thái:** Bộ khung dự án để khởi tạo GitHub. **Chưa phải chương trình mô phỏng SUMO đã hoàn thiện.** Hai tiện ích Python kiểm tra môi trường và tính offset đã có thể chạy độc lập; các file mạng đường/tuyến xe/kịch bản SUMO sẽ được phát triển ở giai đoạn tiếp theo.

## Mục tiêu
- 4 giao lộ A–B–C–D, ưu tiên một hướng A → D; có dòng xe ngang để mô phỏng giao lộ hợp lý.
- Hai phương án cùng chu kỳ và thời gian pha: **baseline** (độ lệch đồng thời, chưa tối ưu cho tiến trình) và **greenwave** (offset theo thời gian đi giữa nút).
- 3 mức lưu lượng giả lập: 300 / 600 / 900 xe/giờ trên hướng nghiên cứu (có thể hiệu chỉnh).
- Kết quả: thời gian hành trình, thời gian chờ, số lần dừng và tỷ lệ xe hoàn tất hành trình; so sánh hai phương án với cùng đầu vào và random seed.
- Kiểm thử code, lưu bảng và biểu đồ, viết báo cáo và trình diễn bằng SUMO-GUI.

## Bắt đầu nhanh (Windows PowerShell)
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

Để chạy **mô phỏng giao thông**, cần cài SUMO/NETEDIT và thực hiện các TODO trong `simulation/`; xem `docs/setup.md` và `docs/experiment-plan.md`.

## Quy ước quản lý
- `config/`: giả định mô hình và thiết kế thực nghiệm.
- `simulation/`: mô hình mạng đường, xe, các chương trình đèn SUMO.
- `src/greenwave/`: thuật toán, bộ chạy, phân tích và đồ họa bằng Python.
- `scripts/`: lệnh tiện ích từ thư mục gốc của repository.
- `tests/`: kiểm thử tự động không cần khởi động SUMO.
- `data/`: dữ liệu bổ sung; `results/`: đầu ra và biểu đồ (mặc định bị bỏ qua bởi Git).
- `docs/`: yêu cầu, giải thuật, kế hoạch mô phỏng, hướng dẫn và báo cáo.

## Nguồn học thuật và kỹ thuật
- Lecture 04, học phần ITS – phần điều khiển đèn liên hoàn, offset, bandwidth, mô phỏng giao thông.
- [Tài liệu SUMO](https://sumo.dlr.de/docs/)
- [Traffic lights SUMO](https://sumo.dlr.de/docs/Simulation/Traffic_Lights.html)

**Lưu ý:** Dữ liệu ví dụ trong `config/` là **giả định**, không được trình bày như dữ liệu đo đạc thực tế.
=======
# GreenWave-Simulation-ITS-GROUP2
Xây dựng mô phỏng phối hợp đèn tín hiệu theo nguyên tắc làn sóng xanh trên một tuyến đường
>>>>>>> 3f56e683dd6aebc34c81fd8f52a232377e80a385
