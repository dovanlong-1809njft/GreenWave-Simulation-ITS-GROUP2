# Yêu cầu hệ thống / System Requirements

## Phạm vi
Mô phỏng một tuyến 4 giao lộ A–B–C–D; ưu tiên xe đi thẳng một chiều A→D. Không điều khiển thiết bị thật, không phát triển thương mại, không yêu cầu AI, Web App hay cơ sở dữ liệu.

## Functional Requirements – yêu cầu chức năng
| Mã | Nội dung | Tiêu chí nghiệm thu |
|---|---|---|
| FR-01 | Cấu hình mạng đường 4 giao lộ | SUMO-GUI hiển thị đúng 4 nút và phương tiện có thể đi qua |
| FR-02 | Phương án baseline | Chạy được cấu hình chu kỳ cố định với các offset đối chứng |
| FR-03 | Phương án greenwave | Offset tính theo khoảng cách/tốc độ, áp vào SUMO và kiểm tra pha |
| FR-04 | 3 mức lưu lượng | Có low/medium/high, cùng seed cho hai phương án |
| FR-05 | Thu thập số liệu | Lưu trip time, waiting time, stops và số xe hoàn thành |
| FR-06 | Phân tích, biểu đồ | Bảng so sánh và đồ thị với nhãn đơn vị đầy đủ |

## Non-functional Requirements – yêu cầu phi chức năng
- **NFR-01: Tái lập** – lưu cấu hình, seed và phiên bản SUMO/Python cho mỗi đợt chạy.
- **NFR-02: Kiểm chứng** – có unit test cho offset, có ít nhất một test chức năng so số liệu với kỳ vọng.
- **NFR-03: Minh bạch** – phân biệt rõ dữ liệu giả lập và dữ liệu khảo sát, tránh khẳng định hiệu quả ngoài phạm vi mô phỏng.
- **NFR-04: Dễ chạy lại** – có README và các lệnh chạy trên Windows PowerShell.
- **NFR-05: Quản lý mã nguồn** – dùng Git, branch, PR, `.gitignore`.

## Ngoài phạm vi
Tối ưu hai chiều đồng thời, học tăng cường, nhận diện camera, điều khiển đèn thực tế, quản lý người dùng.
