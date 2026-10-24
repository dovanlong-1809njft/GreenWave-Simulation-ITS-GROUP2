# Hướng dẫn Windows

1. Giải nén góiStage5 vào thư mục riêng; chạy trình cài để giữ sửa đổi cũ:

```powershell
py scripts/install_stage5.py --project "C:\Users\User\Downloads\ITS-GreenWave-Simulation"
cd "C:\Users\User\Downloads\ITS-GreenWave-Simulation"
py -m pip install matplotlib
```

Phần phân tích chỉ dùng thư viện chuẩn; matplotlib chỉ dùng khi vẽ. Không yêu cầu dashboard hoặc thư viện nặng.

2. Nếu dùng batch Windows đã chạy:

```powershell
py scripts/analyze_experiments.py --batch results/raw/stage4/20261024T024249811236Z --output results/tables/stage5/windows_seed11
py scripts/plot_experiments.py --tables results/tables/stage5/windows_seed11 --output results/figures/stage5/windows_seed11
```

Một seed vẫn được phân tích nhưng không có SD mẫu. Nếu muốn đủ ba seed cùngbatch:

```powershell
$env:SUMO_HOME = "C:\Program Files (x86)\SUMO"
$env:Path = "$env:SUMO_HOME\bin;$env:Path"
py scripts/build_scenarios.py
py scripts/run_experiments.py --seed 11 22 33
# Dùng tênbatch mới được in sau lệnh, không trộn các batch cũ
py scripts/analyze_experiments.py --batch results/raw/stage4/TEN_BATCH_MOI --output results/tables/stage5/three_seeds
py scripts/plot_experiments.py --tables results/tables/stage5/three_seeds --output results/figures/stage5/three_seeds
```

3. Tái tạo chính kết quả được bàn giao: giải nén docs/stage5-evidence/source-runs.zip vào thư mục mới results/raw/stage5-source. Có sealed_primary và sealed_repeat; chỉ phân tích sealed_primary:

```powershell
py scripts/analyze_experiments.py --batch results/raw/stage5-source/sealed_primary --output results/tables/stage5/reproduced
py scripts/plot_experiments.py --tables results/tables/stage5/reproduced --output results/figures/stage5/reproduced
py scripts/build_scenarios.py
py -m unittest discover -s tests -v
```

Các thư mụcđầu ra phải mới; script không âm thầm ghi đè. Batch thiếu cặp, file thiếu/hash sai hoặc tập xe khác nhau sẽ bị từ chối. Không cầnSUMO để đọc kết quả đã niêm phong; các test mô phỏng cũ tự bỏ qua nếu thiếuSUMO và phải đọc rõ dòngskipped.

4. Đọc paired_comparison theo level/seed trước, sau đó seed_aggregation (mỗi seed trọng số bằng nhau). Đọc n_requested/n_arrived vàcomplete_cohort trước khi diễn giải số trung bình. High phải đọc thêm overload_diagnostics và delay. SD không phảiCI. Dữ liệu cuối doWork kiểm chứng trênLinux/Python3.12; cần bạn chạyStage5 trênWindows/Python3.13.12 để xác nhận tương thích thực tế.

CI hiện có đã chạy build_scenarios.py trước unittest; không thay workflow đã sửa. TestStage5 dùng fixture tính tay và dữ liệu niêm phong, không chạy18 thí nghiệm mới. Test vẽ báoskipped nếuCI không cómatplotlib; các testSUMO cũ báoskipped nếu không càiSUMO. Chưa chạyGitHub Actions từ đây.
