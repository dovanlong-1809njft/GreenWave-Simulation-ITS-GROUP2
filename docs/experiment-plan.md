# Kế hoạch thực nghiệm / Experimental Plan

## Biến độc lập
- Phương án: baseline (offset đồng thời) / greenwave (offset dựa trên L/V).
- Nhu cầu hướng ưu tiên: 300, 600, 900 xe/giờ (giả định khởi tạo).

## Giữ cố định
Mạng đường, pha xanh/vàng/đỏ, chu kỳ 120s, số làn, luật di chuyển, speed target 36km/h, lưu lượng hướng ngang (dự kiến 100 xe/h), thời gian warm-up 300s và đo 3600s, mỗi bộ random seed 11/22/33.

## Ma trận chạy
`2 phương án × 3 mức lưu lượng × 3 seed = 18 lượt chạy`.

## Chỉ số tối thiểu
1. Thời gian hành trình trung bình (s/xe hoàn thành).
2. Thời gian chờ trung bình (s/xe hoàn thành).
3. Số lần dừng trung bình (lần/xe hoàn thành; định nghĩa ngưỡng dừng rõ ràng).
4. Số xe hoàn tất / còn trong hệ thống tại thời điểm kết thúc.

Đảm bảo không so sánh chỉ các xe hoàn thành nếu tỷ lệ xe chưa hoàn thành khác nhau quá lớn giữa các phương án. Có thể kéo dài thời gian kết thúc để xe đi hết mạng hoặc mô tả trường hợp censoring.

## Đầu ra dự kiến
- `results/raw/`: dữ liệu gốc từ SUMO.
- `results/tables/`: CSV tổng hợp, mean + độ biến thiên theo seeds.
- `results/figures/`: biểu đồ so sánh và, nếu phù hợp, time–space diagram.

**Lưu ý:** Kịch bản giao thông giả lập không đại diện một tuyến đường thực tế nếu chưa hiệu chỉnh bằng dữ liệu thực.
