# Thuật toán phối hợp đèn / Green-wave Offset

Theo phần điều khiển đèn liên hoàn trong Lecture 04:

- Thời gian đi giữa hai nút: `t_i = L_i / V` (L: m, V: m/s).
- Vận tốc nhập từ km/h được đổi thành m/s bằng cách chia 3.6.
- Offset của giao lộ `i` so với giao lộ đầu: `O_i = (sum(t_1 ... t_i)) mod C`, trong đó C là chu kỳ chung.

Ví dụ mẫu: `L=[300,300,300]m`, `V=36km/h`, `C=120s` → offset `[0,30,60,90]s`.

Công thức trên là **độ lệch lý tưởng ban đầu cho một hướng**, không bảo đảm băng thông xanh tối đa khi có hàng chờ, giao cắt hai chiều hoặc vận tốc biến đổi.

Các pha tín hiệu cần được kiểm chứng theo sơ đồ xung đột giao lộ; tuyệt đối không suy diễn việc cùng xanh cho các dòng xe giao cắt.

**Bandwidth:** khoảng xanh hữu ích để một đoàn xe đi liên tiếp qua các nút. Có thể đo/tính thêm trong báo cáo (Lecture 04, slide 28–29), nhưng không dùng chỉ số này thay cho thời gian chờ/số lần dừng.
