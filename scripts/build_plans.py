"""Tạo Baseline/Green Wave mà không sửa mạng hoặc xe mẫu."""
import json
from pathlib import Path
import sys
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'src'))
from greenwave.controllers.fixed_plans import build_plans
if __name__ == '__main__':
    try:
        print(json.dumps(build_plans(root), ensure_ascii=False, indent=2))
    except (ValueError, FileNotFoundError) as error:
        raise SystemExit(str(error))
