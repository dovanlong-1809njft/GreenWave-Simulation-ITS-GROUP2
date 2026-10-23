# Kiến trúc / Architecture

```text
config JSON (giả định và kịch bản)
  -> scripts + Python src (tính offset, sinh routes/sumocfg)
  -> SUMO / sumo-gui (mạng đường, tín hiệu, phương tiện)
  -> results/raw (tripinfo, trajectory, log nếu bật)
  -> Python analysis (chuẩn hóa, thống kê)
  -> results/tables + results/figures
  -> docs/report + slide (nhóm tự hoàn thiện)
```

## Modules
- `src/greenwave/algorithms/offset.py`: hàm tính thời gian và offset một chiều – **đã có và đã có unit test**.
- `src/greenwave/controllers/`: chương trình chuyển offset thành điều khiển SUMO – **TODO**.
- `src/greenwave/simulation/`: sinh kịch bản và chạy SUMO CLI / GUI – **TODO**.
- `src/greenwave/analysis/`: thu thập chỉ số, so sánh nghiệm – hiện mới có phép tính thống kê cơ bản.
- `src/greenwave/visualization/`: biểu đồ Matplotlib – **TODO**.

## Quy tắc so sánh
Cả hai phương án cần có cùng chu kỳ, pha, tốc độ thiết kế, số làn, dòng xe, seed, thời gian warm-up và đo lường. Chỉ thay đổi phối hợp offset, trừ khi mục tiêu thực nghiệm ghi rõ khác.

## Ràng buộc
File SUMO `.net.xml` chứa mạng đường, `.rou.xml` chứa tuyến/xe, `.add.xml` thường chứa các cấu hình bổ sung như chương trình đèn, `.sumocfg` gom nguồn cho một lượt chạy. IDs và trạng thái đèn phải nhất quán, không giả định `.add.xml` có thể hoạt động chỉ với offset mà chưa có mạng phù hợp.
