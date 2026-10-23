# Báo cáo kiểm thử Giai đoạn 2

Ngày: 23/10/2026. Môi trường đã chạy: Linux, Python 3.12, Eclipse SUMO/NETCONVERT 1.28.0.

## Đã kiểm thử

| Hạng mục | Bằng chứng / kết quả |
| --- | --- |
| Sinh mạng bằng NETCONVERT | Thành công từ nod/edg/con, không dùng ignore-errors |
| Nạp cấu hình và XML | SUMO chạy với --xml-validation always; không báo lỗi/cảnh báo |
| Nút, đường, kết nối | Đúng 4 nút đèn A/B/C/D, 26 đường có hướng, 1 làn/đường, 16 kết nối có đèn |
| Tuyến xe | Tất cả tuyến liên tục, có kết nối hợp lệ giữa các cạnh |
| Quyền đi qua nút | Kiểm tra mọi pha với bảng foes của mạng: không cấp xanh/vàng đồng thời cho hai kết nối xung đột |
| Mốc tín hiệu thực tế | Đối chiếu 7200 bản ghi trạng thái: 1800 bước × 4 nút, chương trình fixed, 6 pha, chu kỳ 120 s |
| Hành trình mẫu | 85 xe được phát và 85 xe hoàn tất; 30 xe hướng W→E đi đúng W_A, A_B, B_C, C_D, D_E |
| An toàn chạy mẫu | 0 va chạm, 0 teleport (dịch chuyển cưỡng bức), không còn xe chạy/chờ phát ở bước cuối |
| Script chạy CLI | run_sample.py --cli kết thúc thành công |
| Bộ kiểm thử | 10/10 test đạt, gồm 7 test trước đó và 3 test mô hình/tích hợp mới |

Các kiểm tra xung đột dựa trên logic mạng và bài chạy mẫu, không phải chứng nhận an toàn giao thông thực tế. Kết quả trên chỉ là kiểm thử tính hoạt động, chưa chứng minh hiệu quả làn sóng xanh.

## Chưa kiểm thử

- Chưa mở cửa sổ SUMO-GUI trên Windows; chưa xác minh trực quan bằng ảnh chụp GUI. Môi trường chạy không có màn hình đồ họa.
- Chưa kiểm thử cài đặt SUMO, PATH/SUMO_HOME và PowerShell trên máy người dùng.
- Chưa kiểm thử các phiên bản SUMO khác 1.28.0.
- Chưa có so sánh baseline/greenwave, nhiều mức lưu lượng, thống kê/biểu đồ hoặc hiệu chỉnh theo số liệu thực địa.

## Chạy lại

```powershell
py scripts/build_network.py
py scripts/validate_sample.py --run
py -m unittest discover -s tests -v
py scripts/run_sample.py
```

Nếu không tìm thấy SUMO, test tích hợp sẽ báo skipped (bỏ qua); không coi đó là bằng chứng tích hợp đã đạt. Các kiểm tra cấu trúc vẫn chạy từ mạng bàn giao sẵn. Không chạy Python với -O vì các kiểm tra mô hình dùng assert.

Bài kiểm tra tích hợp xuất tripinfo, summary, vehroute và trạng thái đèn vào thư mục tạm, kiểm tra rồi dọn dẹp; không tạo dữ liệu thực nghiệm giả trong results/.
