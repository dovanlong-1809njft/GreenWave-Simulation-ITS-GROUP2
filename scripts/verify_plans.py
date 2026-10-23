"""Đối chiếu lịch đèn và lặp lại 2 lần/phương án; không đo hiệu quả làn sóng xanh."""
import argparse
import json
from pathlib import Path
import sys
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root/'src'))
from greenwave.simulation.plan_validation import validate_plans, verify
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--static-only',action='store_true',help='Chỉ kiểm tra file, chưa chạy SUMO')
    parser.add_argument('--output',default='results/raw/stage3',help='Thư mục log, tương đối từ gốc project')
    args = parser.parse_args()
    try:
        report = validate_plans(root) if args.static_only else verify(root, root/args.output)
        print(json.dumps(report,ensure_ascii=False,indent=2))
    except (ValueError, FileNotFoundError) as error:
        raise SystemExit(str(error))
