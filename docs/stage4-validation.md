# Kiểm chứng Giai đoạn 4 và giới hạn nghiệm thu

**Không đánh dấu hoàn thành toàn bộ tiêu chí năng lực:** mức 900 xe/h gây tăng hàng chờ ngoài mạng trong cửa sổ đo. Đã hoàn thành phần tạo/chạy/kiểm tra kịch bản và chuẩn bị dữ liệu; High phải được xem là thử quá tải, cần quyết định phạm vi trước khi coi mọi mức đều phục vụ ổn định.

## Nền và môi trường thực tế

Ngày 24/10/2026; nhánh feature/stage3-greenwave, commit8089d6f282b3a99647b7aeb2ca099eb8c150b58f. Linux/Python 3.12/Eclipse SUMO 1.28.0. Không đọc lại PDF; dùng theory-summary và tài liệu SUMO chính thức đã dẫn.

Chạy18 tổ hợp =3 mức ×2 phương án ×3 seed11/22/33. Lặp sáu tổ hợp seed11 để kiểm tra tái lập. Không coi sáu lượt lặp là mẫu độc lập và chưa suy luận độ tin cậy thống kê.

## Kết quả kiểm tra chức năng

- Đủ9 nhu cầu dùng chung và18 sumocfg; XML được SUMO nạp với --xml-validation always.
- 9/9 cặp có cùng route/hash, cùng tham số chung, chỉ khác chương trình offset.
- 18/18 lượt chính chạy kết thúc hợp lệ; 6/6 lượt lặp seed11 khớp hash dấu vết hành vi với lượt gốc.
- Sau khoảng xả tới 7500 s, mọi xe yêu cầu đều được chèn và đến đích; không còn xe pending/running. Điều này không chứng minh năng lực trong cửa sổ đo.
- Không có va chạm, teleport hoặc cảnh báo SUMO trong bộ kết quả chính đã niêm phong.
- Bộ kiểm thử tự động35/35 đạt:20 test GĐ 2–3 giữ nguyên và15 test mới về nhu cầu, cửa sổ, tính công bằng, chống ghi đè, xe chưa hoàn tất và toàn vẹn log. tests.txt là đầu ra thực.
- Kiểm thử cố ý rút thời gian xả xuống1 s vẫn giữ xe chưa xuất phát/chưa đến đích; không biến chúng thành chuyến hoàn tất hoặc0giây.

## Số liệu kiểm tra seed11

Tất cả số liệu dưới đây được lấy từ gói kết quả đã audit, không dùng để kết luận phương án nào hiệu quả hơn. Pending/running chỉ tính hướng ưu tiên; requested/arrived cuối là mọi hướng.

| Mức | Phương án | Requested mọi hướng | Pending ưu tiên tại 3900 | Running ưu tiên tại 3900 | Qua A_B pos10m trong 3600 s (xe/h) | Arrived mọi hướng tại 7500 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| low | baseline | 1297 | 0 | 19 | 300 | 1297 |
| low | greenwave | 1297 | 0 | 13 | 300 | 1297 |
| medium | baseline | 1622 | 0 | 49 | 600 | 1622 |
| medium | greenwave | 1622 | 0 | 31 | 600 | 1622 |
| high | baseline | 1947 | 230 | 82 | 673 | 1947 |
| high | greenwave | 1947 | 206 | 68 | 696 | 1947 |

Cả 6 lượt High ở 3 seed đều có pending ưu tiên tăng giữa 300 và 3900 s; pending tại 3900 trong khoảng 194–230 xe. Khoảng xả giúp giải tỏa nhưng không sửa được mất cân bằng nhu cầu/phục vụ trong cửa sổ đo. Lưu lượng qua detector là kết quả phục vụ quan sát của bài thử, **không tự gọi là năng lực cực đại** và không đánh đồng nó với 900 xe/h yêu cầu.

Không thay đổi 900, số làn, tốc độ, pha xanh hoặc offset. Đề xuất giữ High như stress test và phân tích tồn đọng/censoring trong GĐ 5; mọi thay đổi phạm vi khác phải được thống nhất, không tự tối ưu để làm đẹp số liệu.

## Toàn vẹn và những lần thử bị loại

Kiểm tra lưu trữ đã phát hiện một số log rời chưa hoàn chỉnh/không khớp ở các lần thử trước. Không sử dụng các lần đó làm bằng chứng và không sửa số liệu để khớp. Chưa xác định chắc chắn nguyên nhân môi trường, nên không tuyên bố chúng đã hợp lệ.

Bản cuối niêm phong từng lượt thành sealed-run.zip sau khi tiến trình SUMO kết thúc và kiểm tra số xe. Trong mỗi gói: XML gốc, CSV, snapshot, manifest trạng thái hoàn tất và hash đầu ra. check_seal xác minh CRC, hash snapshot, hash nội dung XML và dữ liệu CSV/JSON; audit kiểm tra gói niêm phong và ghép cặp. Chỉ 24 lượt qua kiểm tra này được đưa vào raw-runs.zip. Các tệp rời có thể kiểm tra để chẩn đoán, nhưng gói niêm phong là bằng chứng chuẩn.

Hash XML loại comment ngày tạo và thời gian tính toán; vẫn giữ duration hành trình và mọi dữ liệu giao thông. Có test xác nhận đổi số liệu làm hash đổi, còn đổi comment thì không. Một gói có metadata started hoặc CSV bị sửa sẽ bị từ chối.

## Dữ liệu kèm theo

- validation-table.csv: đủ18 lượt chính, số xe tại các mốc và thông tin quá tải.
- audit.json:9 cặp công bằng và6 lượt lặp khớp.
- summary.json: trạng thái nghiệm thu có giới hạn và hash raw-runs.zip.
- raw-runs.zip: hai batch sealed_primary và sealed_repeat; mỗi thư mục case có sealed-run.zip chứa toàn bộ dữ liệu thô cùng inputs/.
- tests.txt: đầu ra35 test.

Không tính trung bình travel_time/waiting_time hoặc xếp hạngBaseline/GreenWave ởGĐ 4. Dữ liệu mọi xe và trạng thái censored đã sẵn để xử lý đúng tạiGĐ 5.

## Chưa xác minh

- GĐ 4 chưa được chạy trực tiếp trên Windows/Python 3.13.12; thao tác GUI mới chưa được quan sát. Người dùng xác nhận GĐ 3 chạyWindows không thay thế phần này.
- Chưa hiệu chỉnh theo thực địa, chưa thử nhiều kiểu người lái/sigma, chưa chứng minh warmup300 s đạt cân bằng.
- Chưa khẳng định các mức Low/Medium là năng lực tối đa hoặcHigh là ổn định; chỉ báo cáo đúng bài chạy.
- Chưa phân tích thống kê, biểu đồ hiệu quả hay kết luận Green Wave tốt hơn.

Xem stage4-windows.md để tự chạy và audit trên máy người dùng. Không push/merge lênGitHub.


## Kiểm tra tích hợp cuối

Đã thử trên thư mục mới có dấu cách: xung đột bị chặn trước khi ghi; cài hai lần không nhân bản; giữ ghi chú riêng trong README và giữ nguyên83 tệp nền khác. Sau tích hợp,35 test đạt và audit lại gói 24 lượt được giao đạt9 cặp công bằng/6 lượt lặp giống nhau. Đây là kiểm tra trên Linux với đường dẫn có dấu cách, chưa thay cho chạy Windows thực tế.
