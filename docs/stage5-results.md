# Kết quả quan sát từ dữ liệu mô phỏng thực

Nguồn:18 lượt Linux của batch sealed_primary, ba seed11/22/33; không phải dữ liệu Windows do người dùng tự chạy. Toàn bộ cohort ưu tiên measurement đều hoàn tất sau xả. Mỗi phương án dùng cùng tập300/600/900 xe mỗi seed, không gộp ba seed thành một thử nghiệm lớn.

| Mức | Baseline (s/xe) | Green Wave (s/xe) | Trung bình tỷ lệ giảm theo cặp (%) |
| --- | ---: | ---: | ---: |
| low | 260.99 | 177.67 | 31.93 |
| medium | 342.29 | 218.01 | 36.31 |
| high | 427.43 | 315.96 | 26.08 |

Low/Medium: trong ba seed được khảo sát, Green Wave có thời gian hành trình trong mạng thấp hơn ở từng cặp. Đây là kết quả của mô hình giả lập và hai bộ offset đã chọn, không khẳng định một thuật toán tối ưu hoặc quy luật chung của giao thông thực.

High: thời gian trong mạng cũng thấp hơn trong các lượt này, nhưng không thể từ đó kết luận phục vụ ổn định. Hướng ưu tiên tồn đọng ngoài mạng và chịu chậm xuất phát lớn; phải đọc cùng total_requested_to_arrival_s và overload_diagnostics. Tập xe hoàn tất đã được theo dõi tới sau xả nên không bỏ riêng các xe khó phục vụ; tuy vậy quá trình nhu cầu vượt phục vụ vẫn làm High khác điều kiện ổn định.

Không phải chỉ số nào cũng giảm: số đợt chờ của High có biến động và trung bình tỷ lệ thay đổi âm ở bộ dữ liệu này. Không chọn riêng kết quả thuận lợi để khẳng định Green Wave tốt hơn về mọi mặt.

Các bảng nằm tại results/tables/stage5/final/: scenario_summary, paired_comparison, seed_aggregation, overload_diagnostics và vehicle_metrics. Dấu vết nguồn từng xe là source_case + source_seal_sha256. analysis_manifest mô tả batch/hash, snapshot và mã phân tích.

Sáu hình PNG/SVG tại results/figures/stage5/final/:01-travel-time,02-reduction,03-waiting,04-stops,05-seeds,06-overload. Hình dùng trục0 cho độ lớn, đường0 cho tỷ lệ có dấu; High gắn nhãn quá tải. Thanh sai số là SD giữa seed, không phải khoảng tin cậy.
