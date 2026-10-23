"""Chạy GĐ4 với batch riêng, không ghi đè dữ liệu thí nghiệm cũ."""
import argparse,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'src'))
from greenwave.simulation.experiments import run_batch
from greenwave.simulation.scenarios import LEVELS,PLANS
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--level',choices=LEVELS,nargs='+',default=list(LEVELS))
    p.add_argument('--plan',choices=PLANS,nargs='+',default=list(PLANS))
    p.add_argument('--seed',type=int,nargs='+',default=[11])
    p.add_argument('--batch-id')
    a=p.parse_args()
    try:print(run_batch(root,a.level,a.plan,a.seed,a.batch_id))
    except (ValueError,RuntimeError,FileNotFoundError,FileExistsError) as e:raise SystemExit(str(e))
