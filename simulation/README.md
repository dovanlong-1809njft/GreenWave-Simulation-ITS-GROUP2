# Mô hình giao thông SUMO — Giai đoạn 2

Đã có mạng 4 nút A–B–C–D với đường ngang hai chiều và xe mẫu. Mở `scenarios/sample.sumocfg` bằng SUMO-GUI. Chi tiết: [hướng dẫn Windows](../docs/stage2-windows.md).

- network/source/: nguồn nút, đường, kết nối.
- network/generated/corridor.net.xml: mạng do NETCONVERT tạo, bàn giao sẵn.
- signals/fixed.add.xml: đèn cố định đồng thời, chu kỳ 120 s.
- routes/source/sample.rou.xml: tổng 85 xe mẫu.
- scenarios/sample.sumocfg: cấu hình nạp mạng, tuyến và chương trình đèn.
- Các thư mục generated khác tiếp tục dành cho giai đoạn thực nghiệm sau.

Tạo lại: `py scripts/build_network.py`; kiểm chứng: `py scripts/validate_sample.py --run` từ thư mục gốc. Không chỉnh `.net.xml` thủ công.
