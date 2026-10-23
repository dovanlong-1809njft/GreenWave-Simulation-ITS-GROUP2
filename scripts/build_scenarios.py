"""Sinh nhu cầu/kịch bản GĐ4, giữ file cũ; không cần TraCI."""
import argparse,json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'src'))
from greenwave.simulation.scenarios import build,LEVELS
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--level',choices=LEVELS,nargs='+',default=list(LEVELS))
    p.add_argument('--seed',type=int,nargs='+')
    a=p.parse_args()
    try:print(json.dumps(build(root,a.level,a.seed),ensure_ascii=False,indent=2))
    except (ValueError,FileNotFoundError) as e:raise SystemExit(str(e))
