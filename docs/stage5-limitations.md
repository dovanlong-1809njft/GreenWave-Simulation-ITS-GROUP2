# Giới hạn diễn giải

- Mạng giả lập bốn nút, đường chỉ đi thẳng, không có người đi bộ hoặc dữ liệu thực địa hiệu chỉnh.
- Offset lấy từ300m/10m/s theo tâm nút; tốc độ mục tiêu khác tốc độ thực, có hàng chờ và tăng/giảm tốc.
- Chỉ hai bộ offset và chu kỳ120s cố định; không chứng minh tối ưu hoặc ưu thế với mọi tuyến.
- Chỉ ba seed, biến thiên chỉ ở thời điểm yêu cầu, vType sigma=0 của Stage4. Không tuyên bố ý nghĩa thống kê, p-value hoặc độ tin cậy cao.
-300s làm nóng chưa được chứng minh đạt cân bằng. Cohort measurement phát trong3600s rồi theo dõi xả tới7500s, không chỉ lấy xe đến đích trước3900.
- High900xe/h có tăng pending trong cửa sổ đo. Chậm chèn không nằm trong travel_time trong mạng, phải đọc thêm delay và thời gian từ yêu cầu tới đích.
- Phép đo toànW→E chưa tách được thời gian giữa hai vạch dừngA/D.
- Kết quả kèm gói là dữ liệuLinux; chưa đối chiếu với batch Windows của người dùng, chưa thử Stage5 trực tiếp Python3.13.12 trên Windows.
