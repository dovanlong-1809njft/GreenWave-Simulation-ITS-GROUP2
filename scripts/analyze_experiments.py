"""Phân tích một batch GĐ4 đã niêm phong, không trộn các batch."""
import argparse,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'src'))
from greenwave.analysis.experimental import analyze
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batch',required=True);p.add_argument('--output',required=True);a=p.parse_args()
 try:print(analyze(root/a.batch,root/a.output))
 except (ValueError,FileNotFoundError) as e:raise SystemExit(str(e))
