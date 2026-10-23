"""Mở xe mẫu: python scripts/run_sample.py; thêm --cli để chạy không giao diện."""
import argparse
import subprocess
import sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/"src"))
from greenwave.simulation.model import binary
if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cli",action="store_true",help="Chạy SUMO dòng lệnh")
    args=parser.parse_args()
    if not (root/"simulation/network/generated/corridor.net.xml").is_file():
        raise SystemExit("Chưa có mạng. Chạy python scripts/build_network.py")
    try:
        cmd=[binary("sumo" if args.cli else "sumo-gui"),"-c",str(root/"simulation/scenarios/sample.sumocfg")]
        if not args.cli:
            cmd += ["--delay","100"]
        subprocess.run(cmd,check=True)
    except FileNotFoundError as error:
        raise SystemExit(str(error))
