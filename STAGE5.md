# Giai đoạn 5 — Phân tích thực nghiệm

Phạm vi: ảnh hưởng offset đến thời gian hành trình của nhóm xe hướng A→D. Đọc dữ liệu SUMO đã niêm phong, so sánh ghép cặp theo seed, xuất bảng và sáu hình PNG/SVG. Không thay mạng, pha, nhu cầu hoặc mã Stage4.

- [Phương pháp](docs/stage5-methodology.md)
- [Định nghĩa chỉ số](docs/stage5-metrics.md)
- [Kết quả](docs/stage5-results.md)
- [Kiểm thử](docs/stage5-validation.md)
- [Giới hạn](docs/stage5-limitations.md)
- [Windows](docs/stage5-windows.md)

```powershell
py scripts/analyze_experiments.py --batch results/raw/stage5-source/sealed_primary --output results/tables/stage5/my_analysis
py scripts/plot_experiments.py --tables results/tables/stage5/my_analysis --output results/figures/stage5/my_analysis
```

Dữ liệu phân tích kèm gói là dữ liệu Linux được tạo thật ở GĐ4; không giả định đó là batch Windows của người dùng. High là bài thử quá tải, không khẳng định cải thiện toàn hệ thống hoặc ý nghĩa thống kê.
