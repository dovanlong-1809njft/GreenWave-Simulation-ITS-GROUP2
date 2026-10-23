"""Kiểm tra mô hình; thêm --run để chạy thử SUMO và xác minh tín hiệu."""
import argparse
import json
import sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/"src"))
from greenwave.simulation.validation import validate, smoke_test
if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run",action="store_true")
    args=parser.parse_args()
    try:
        print(json.dumps(smoke_test(root) if args.run else validate(root),ensure_ascii=False,indent=2))
    except FileNotFoundError as error:
        raise SystemExit(str(error))
