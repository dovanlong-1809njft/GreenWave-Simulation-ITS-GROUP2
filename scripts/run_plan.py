"""Chạy riêng baseline hoặc greenwave bằng SUMO-GUI/dòng lệnh."""
import argparse
from pathlib import Path
import subprocess
import sys
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'src'))
from greenwave.controllers.fixed_plans import PLANS
from greenwave.simulation.model import binary
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', choices=PLANS, required=True)
    parser.add_argument('--cli', action='store_true', help='Chạy không giao diện')
    parser.add_argument('--delay', type=float, default=100, help='Độ trễ GUI (ms)')
    args = parser.parse_args()
    if args.delay < 0:
        parser.error('--delay phải không âm')
    config = root / f'simulation/scenarios/{args.plan}.sumocfg'
    if not config.is_file():
        raise SystemExit('Chưa có cấu hình. Chạy py scripts/build_plans.py')
    try:
        cmd = [binary('sumo' if args.cli else 'sumo-gui'), '-c', str(config)]
        if not args.cli:
            cmd += ['--delay', str(args.delay)]
        subprocess.run(cmd, check=True)
    except FileNotFoundError as error:
        raise SystemExit(str(error))
