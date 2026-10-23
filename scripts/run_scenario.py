"""Mở một kịch bản GĐ4 bằng SUMO-GUI; script run_experiments.py dùng cho CLI có log."""
import argparse,sys,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'src'))
from greenwave.simulation.model import binary
from greenwave.simulation.scenarios import LEVELS,PLANS,scenario_path,verify_files
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--level',choices=LEVELS,required=True);p.add_argument('--plan',choices=PLANS,required=True)
    p.add_argument('--seed',type=int,default=11);p.add_argument('--delay',type=float,default=50)
    a=p.parse_args()
    try:
        verify_files(root,[a.level],[a.seed])
        if a.delay<0:raise ValueError('Delay không âm')
        subprocess.run([binary('sumo-gui'),'-c',str(root/scenario_path(a.level,a.plan,a.seed)),'--delay',str(a.delay)],check=True)
    except (ValueError,FileNotFoundError) as e:raise SystemExit(str(e))
