# Git workflow – quy trình Git cho nhóm

- Nhánh chính `main`: lưu phiên bản tích hợp đã kiểm thử.
- Nhánh chức năng ví dụ: `feature/sumo-network`, `feature/green-wave`, `feature/experiments`, `feature/results-analysis`, `docs/report`.
- Một người mở Pull Request (PR), người khác review trước khi merge.
- Không commit `.venv`, dữ liệu sinh ra lớn, logs, tệp bí mật.

Ví dụ:
```powershell
git switch -c feature/green-wave
# Sửa src/greenwave/algorithms/offset.py
git add src/greenwave/algorithms/offset.py tests/test_offset.py
git commit -m "Implement offset calculation"
git push -u origin feature/green-wave
```
