"""Vẽ sáu biểu đồ, cần matplotlib; không ghi đè thư mục hình cũ."""
import argparse,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'src'))
from greenwave.visualization.experiment_plots import plot
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tables',required=True);p.add_argument('--output',required=True);a=p.parse_args()
 try:print(plot(root/a.tables,root/a.output))
 except (ValueError,FileNotFoundError) as e:raise SystemExit(str(e))
