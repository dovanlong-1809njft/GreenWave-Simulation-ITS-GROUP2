# Danh sách thay đổi Giai đoạn 3

## Tệp đã sửa

**Không sửa tệp cũ nào của Giai đoạn 2.** Kiểm tra SHA-256 toàn bộ tệp nền trước/sau xác nhận không thay đổi. Do đó không cần ghi đè README.md, docs/theory-summary.md, configs, mạng, tuyến xe, fixed.add.xml, sample.sumocfg hoặc hồ sơ GUI đang chạy của người dùng.

## Thành phần tái sử dụng

| Thành phần | Cách dùng |
| --- | --- |
| config/network.json, config/signals.json | Đọc tham số, không ghi lại |
| corridor.net.xml và các nguồn nod/edg/con | Giữ nguyên mạng, đọc hình học và linkIndex |
| sample.rou.xml | Cùng luồng xe mẫu cho hai phương án |
| sample.sumocfg | Mẫu tham số chung để tạo cấu hình mới |
| algorithms/offset.py | Giữ hàm L/V và offset tích lũy/modulo |
| simulation/model.py | Dùng tìm SUMO và ghi XML |
| simulation/validation.py | Tái dùng kiểm tra mô hình mẫu GĐ2 |
| docs/theory-summary.md | Nguồn lý thuyết được dẫn tới từ tài liệu mới |
| tests cũ | Giữ nguyên và vẫn chạy cùng bộ test mới |

## Tệp bổ sung

| Đường dẫn | Loại thay đổi | Chức năng |
| --- | --- | --- |
| `STAGE3.md` | Mới | Điểm bắt đầu, liên kết hướng dẫn và lệnh chạy |
| `docs/stage3-algorithm.md` | Mới | Nguồn bài giảng, giả định, công thức và dấu offset SUMO |
| `docs/stage3-changes.md` | Mới | Bảng thay đổi và phần tái sử dụng |
| `docs/stage3-evidence/baseline-green-starts.csv` | Mới | Các mốc bật xanh chính thực đo |
| `docs/stage3-evidence/baseline-tls.csv` | Mới | Log tín hiệu từng giây của lần chạy đầu |
| `docs/stage3-evidence/greenwave-green-starts.csv` | Mới | Các mốc bật xanh chính thực đo |
| `docs/stage3-evidence/greenwave-tls.csv` | Mới | Log tín hiệu từng giây của lần chạy đầu |
| `docs/stage3-evidence/tests.txt` | Mới | Đầu ra thực của 20 kiểm thử Python |
| `docs/stage3-evidence/time-space.png` | Mới | Sơ đồ thời gian–không gian để xem nhanh |
| `docs/stage3-evidence/time-space.svg` | Mới | Sơ đồ vector để chèn báo cáo/phóng to |
| `docs/stage3-evidence/verification.json` | Mới | Kết quả kiểm chứng, tham số, phiên bản và hash |
| `docs/stage3-file-manifest.json` | Mới | Danh mục máy đọc để trình tích hợp kiểm tra toàn bộ trước khi ghi |
| `docs/stage3-validation.md` | Mới | Các phép kiểm đã chạy, kết quả và giới hạn |
| `docs/stage3-windows.md` | Mới | Cài an toàn, lệnh PowerShell, mở GUI và đối chiếu log |
| `scripts/build_plans.py` | Mới | Tạo lại hai file đèn và hai cấu hình mới |
| `scripts/install_stage3.py` | Mới | Kiểm tra xung đột trước khi tích hợp; không ghi đè file khác nội dung |
| `scripts/plot_signal_schedule.py` | Mới | Vẽ PNG/SVG từ CSV tín hiệu đo được |
| `scripts/run_plan.py` | Mới | Mở GUI/chạy CLI theo lựa chọn phương án |
| `scripts/verify_plans.py` | Mới | Chạy bốn lượt kiểm chứng và lưu log |
| `simulation/scenarios/baseline.sumocfg` | Mới | Cấu hình Baseline chạy độc lập |
| `simulation/scenarios/greenwave.sumocfg` | Mới | Cấu hình Green Wave chạy độc lập |
| `simulation/signals/baseline.add.xml` | Mới | Tín hiệu cố định đồng thời: offset 0/0/0/0 |
| `simulation/signals/greenwave.add.xml` | Mới | Cùng pha và chu kỳ: offset 0/30/60/90 |
| `src/greenwave/controllers/fixed_plans.py` | Mới | Đọc cấu hình, kiểm tra hình học, tái dùng L/V, tạo hai kế hoạch |
| `src/greenwave/simulation/plan_validation.py` | Mới | Đối chiếu XML, xung đột, log thực, tính tái lập |
| `tests/test_fixed_plans.py` | Mới | 10 test mới: tính tay, biên pha, cấu hình sai và SUMO tích hợp |

Tổng: 26 tệp mới; 0 tệp cũ bị thay thế. GitHub không được push.
