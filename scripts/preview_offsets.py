"""Tính offset từ file config và in ra để kiểm tra logic trước khi dùng SUMO."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from greenwave.algorithms.offset import corridor_offsets  # noqa: E402

config = json.loads((ROOT / "config/network.json").read_text(encoding="utf-8"))
signal = json.loads((ROOT / "config/signals.json").read_text(encoding="utf-8"))
offsets = corridor_offsets(config["intersections_spacing_m"], config["speed_target_kmh"], signal["cycle_s"])
print("Các offset một chiều theo giả định khởi tạo:")
for junction, offset in zip(config["junctions"], offsets):
    print(f"  Giao lộ {junction}: {offset:.1f}s")
print("Lưu ý: chưa ghi/chạy cấu hình SUMO.")
