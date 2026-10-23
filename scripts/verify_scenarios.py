"""Kiểm tra tĩnh nhu cầu và tính công bằng; chạy SUMO bằng run_experiments.py."""
import argparse,json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'src'))
from greenwave.simulation.scenarios import verify_files,LEVELS
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--level',choices=LEVELS,nargs='+',default=list(LEVELS))
    p.add_argument('--seed',type=int,nargs='+')
    p.add_argument('--results',help='Thư mục batch cần kiểm tra hash')
    p.add_argument('--compare',help='Batch lặp cùng seed cần đối chiếu')
    a=p.parse_args()
    try:
        if a.results:
            from greenwave.simulation.scenario_audit import audit_batch
            report=audit_batch(root/a.results,root/a.compare if a.compare else None)
        else:
            if a.compare:p.error('--compare cần --results')
            report=verify_files(root,a.level,a.seed)
        print(json.dumps(report,ensure_ascii=False,indent=2))
    except (ValueError,FileNotFoundError) as e:raise SystemExit(str(e))
