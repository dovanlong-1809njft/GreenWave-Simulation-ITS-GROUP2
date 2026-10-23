"""Vẽ sơ đồ thời gian–không gian từ CSV trạng thái đã đo, cần matplotlib."""
import argparse
import csv
import json
from pathlib import Path
import xml.etree.ElementTree as ET


def draw(root, evidence):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    report=json.loads((evidence/'verification.json').read_text(encoding='utf-8'))
    params=report['parameters']
    nodes={n.get('id'):n for n in ET.parse(root/'simulation/network/generated/corridor.net.xml').getroot().findall('junction')}
    positions={j:float(nodes[j].get('x'))-float(nodes['A'].get('x')) for j in 'ABCD'}
    colors={0:'#168454',1:'#e5a800'}
    fig,axes=plt.subplots(2,1,figsize=(11,7.2),sharex=True,sharey=True,layout='constrained')
    for ax,plan in zip(axes,('baseline','greenwave')):
        with (evidence/f'{plan}-tls.csv').open(encoding='utf-8') as f:rows=list(csv.DictReader(f))
        for j in 'ABCD':
            data=[r for r in rows if r['junction']==j and float(r['time_s'])<360]
            # Ghép các mẫu cùng trạng thái thành một đoạn liên tục.
            start = None
            previous = None
            for row in data + [None]:
                phase = int(row['phase']) if row else None
                if phase != previous:
                    if start is not None:
                        stop = float(row['time_s']) if row else 360
                        ax.plot([start,stop],[positions[j]]*2,color=colors.get(previous,'#dc6969'),linewidth=9,solid_capstyle='butt')
                    start = float(row['time_s']) if row else None
                    previous = phase
        # Đường lý tưởng chỉ để giải thích nguyên lý; không vẽ thành quỹ đạo xe đã đo.
        for depart in [20,140,260]:
            ax.plot([depart,depart+900/(params['speed_kmh']/3.6)],[0,900],
                    color='#263953',linestyle='--',linewidth=1.3)
        offsets=params['offsets_s'][plan]
        ax.set_title(f'{plan.upper()} | offset A/B/C/D = '+ '/'.join(f'{v:g}' for v in offsets)+' s',loc='left',fontsize=11,fontweight='bold')
        ax.set_yticks([positions[j] for j in 'ABCD'], [f'{j} · {positions[j]:g}' for j in 'ABCD']);ax.set_ylabel('Nút · khoảng cách từ A (m)')
        ax.set_ylim(-65,965);ax.set_xlim(0,360);ax.grid(alpha=.15)
    axes[-1].set_xlabel('Thời gian mô phỏng (s)')
    axes[0].legend(handles=[Patch(color='#168454',label='Xanh chính (đo từ SUMO)'),
                            Patch(color='#e5a800',label='Vàng chính'),Patch(color='#dc6969',label='Đỏ chính'),
                            Line2D([0],[0],color='#263953',linestyle='--',label='Quỹ đạo lý tưởng 36 km/h, KHÔNG phải log xe')],
                   loc='upper left',bbox_to_anchor=(0,1.3),ncol=2,fontsize=8,frameon=False)
    fig.suptitle('LỊCH TÍN HIỆU THỰC TẾ — CHƯA ĐÁNH GIÁ HIỆU QUẢ GIAO THÔNG',fontsize=12,fontweight='bold')
    fig.savefig(evidence/'time-space.png',dpi=150)
    fig.savefig(evidence/'time-space.svg')
    plt.close(fig)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence',default='docs/stage3-evidence')
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    draw(root,(root/args.evidence).resolve())
