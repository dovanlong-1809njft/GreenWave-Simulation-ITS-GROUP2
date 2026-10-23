# SUMO – mô hình giao thông

Cần triển khai bộ file mạng đường / chương trình tín hiệu phù hợp mô hình 4 giao lộ.

- `network/source/`: lưu nguồn `.nod.xml`, `.edg.xml`, `.con.xml` nếu tạo mạng bằng `netconvert` để có thể tái tạo.
- `network/generated/`: đầu ra tự sinh `.net.xml` (mặc định không commit; nếu nhóm quyết định lưu mô hình chuẩn, chuyển file đã kiểm chứng sang khu vực nguồn và điều chỉnh `.gitignore`).
- `signals/`: chương trình tín hiệu `.add.xml` hoặc cấu hình điều khiển đèn; **không đặt mẫu `tlLogic` chưa đúng link-index vào đây**.
- `routes/source/`: định nghĩa tuyến và luồng xe gốc do nhóm xây dựng.
- `routes/generated/`: file `.rou.xml` sinh từ scenario và seed.
- `scenarios/generated/`: cấu hình `.sumocfg` theo từng phương án / lưu lượng / seed.

`netedit` hoặc `netconvert` có thể tạo mạng, `sumo-gui` để trình diễn, SUMO CLI để chạy lặp nghiệm. File tên `.net.xml` và `.rou.xml` phải khớp ID đường/nút thực tế. Không đặt file XML minh họa chưa hợp lệ làm mô hình chạy.

**TODO:** Thiết kế 4 nút và các hướng cắt ngang, khai báo chương trình đèn an toàn, xuất mạng, tạo tuyến và 18 cấu hình (2 phương án × 3 mức lưu lượng × 3 seeds).
