"""Tạo lại mô hình từ cấu hình: python scripts/build_network.py."""
import sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/"src"))
from greenwave.simulation.model import build
if __name__ == "__main__":
    try:
        print(build(root))
    except (FileNotFoundError, ValueError) as error:
        raise SystemExit(str(error))
