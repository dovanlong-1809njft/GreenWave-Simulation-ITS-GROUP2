# Đối chiếu gốc một mẫu nhỏ

Nguồn: low/seed11, hai ID measurement; các số depart/arrival/waiting/timeLoss chép từ tripinfo.xml trong gói niêm phong. CộtT tự lấy arrival−depart, không gọi hàm metrics.

| Plan | ID | Depart(s) | Arrival(s) | T(s) | Waiting(s) | TimeLoss(s) |
|---|---|---:|---:|---:|---:|---:|
| baseline | east.measurement.00000 | 304.00 | 622.00 | 318.0 | 170.00 | 187.77 |
| baseline | east.measurement.00001 | 324.00 | 625.00 | 301.0 | 148.00 | 162.84 |
| greenwave | east.measurement.00000 | 304.00 | 510.00 | 206.0 | 40.00 | 76.31 |
| greenwave | east.measurement.00001 | 324.00 | 512.00 | 188.0 | 21.00 | 50.32 |
