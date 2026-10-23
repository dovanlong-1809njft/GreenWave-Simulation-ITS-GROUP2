# Chương trình tín hiệu (TODO)

Hai chế độ phải sử dụng **cùng chu kỳ 120s và cùng pha xanh/vàng/đỏ**; chỉ thay đổi offset để so sánh hợp lý.

- Baseline: offset [0, 0, 0, 0] giây (đèn cùng mốc pha; chưa tối ưu theo thời gian đi lại).
- Greenwave: offset [0, 30, 60, 90] giây theo giả định d=300m, v=36km/h.

Các con số là giá trị ví dụ; phải chuyển thành chương trình `tlLogic` áp đúng ID và trạng thái `linkIndex` của mạng SUMO sau khi xây mạng. Cấu hình trong `config/signals.json` không tự động khiến SUMO đổi đèn.
