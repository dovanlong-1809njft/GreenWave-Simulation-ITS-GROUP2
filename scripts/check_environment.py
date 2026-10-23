"""Kiểm tra Python và SUMO đã có trong môi trường hay chưa."""
import shutil
import sys
from pathlib import Path

print("Python:", sys.version.split()[0])
print("Thư mục dự án:", Path(__file__).resolve().parents[1])
for cmd in ("sumo", "sumo-gui", "netconvert", "netedit"):
    print(f"{cmd}: {shutil.which(cmd) or 'CHƯA tìm thấy trên PATH'}")
try:
    import traci  # noqa: F401
    print("TraCI Python: OK")
except ImportError:
    print("TraCI Python: chưa cài (pip install -r requirements.txt)")
