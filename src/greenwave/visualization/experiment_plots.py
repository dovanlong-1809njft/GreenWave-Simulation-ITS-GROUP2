"""Sáu hình khoa học từ bảng đã tính; không vẽ đường xu hướng hoặc suy luận kiểm định."""
import csv
from pathlib import Path

def plot(tables,output):
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 tables,output=Path(tables),Path(output)
 if output.exists():raise ValueError('Thư mục hình đã tồn tại, chọn đường dẫn mới')
 def read(name):
  with (tables/name).open(encoding='utf-8') as f:return list(csv.DictReader(f))
 summary=read('scenario_summary.csv');pairs=read('paired_comparison.csv');agg=read('seed_aggregation.csv');diag=read('overload_diagnostics.csv')
 if any(s['complete_cohort']!='True' for s in summary):raise ValueError('Cohort chưa hoàn tất: không vẽ biểu đồ chính như đủ dữ liệu')
 seeds=sorted({int(p['seed']) for p in pairs})
 levels=['low','medium','high'];labels=['Low · 300','Medium · 600','High · 900\nQuá tải']
 output.mkdir(parents=True)
 def finish(fig,ax,name,title,ylabel):
  ax.set_title(title,fontsize=12);ax.set_ylabel(ylabel);ax.set_xlabel('Nhu cầu dự kiến hướng ưu tiên (xe/giờ)')
  ax.set_xticks(range(3),labels);ax.grid(axis='y',alpha=.2);ax.legend(fontsize=8)
  fig.tight_layout();fig.savefig(output/(name+'.png'),dpi=180);fig.savefig(output/(name+'.svg'));plt.close(fig)
 for metric,name,title,unit in [('travel_time_s','01-travel-time','Thời gian hành trình trong mạng · cohort A→D','Thời gian trung bình (s/xe)'),('waiting_time_s','03-waiting','Thời gian chờ · cohort A→D','Thời gian chờ trung bình (s/xe)'),('stops','04-stops','Số đợt chờ ở tốc độ ≤0,1 m/s · cohort A→D','Số đợt chờ trung bình (lần/xe)')]:
  fig,ax=plt.subplots(figsize=(8,4.5))
  for plan,color,dx in [('baseline','#35688b',-.18),('greenwave','#c48237',.18)]:
   data=[next(a for a in agg if a['metric']==metric and a['level']==l) for l in levels]
   ax.bar([i+dx for i in range(3)],[float(a[plan+'_mean']) for a in data],width=.34,color=color,label=plan,
          yerr=[float(a[plan+'_sd']) for a in data] if all(a[plan+'_sd'] for a in data) else None,capsize=4)
  ax.set_ylim(bottom=0);finish(fig,ax,name,title+'\nTrung bình giữa seed; thanh sai số = SD khi n≥2, không phải CI',unit)
 fig,ax=plt.subplots(figsize=(8,4.5))
 for i,seed in enumerate(seeds):
  marker=['o','s','^','D'][i%4]
  vals=[next(p for p in pairs if p['level']==l and int(p['seed'])==seed) for l in levels]
  ax.scatter(range(3),[float(p['travel_time_s_reduction_pct']) for p in vals],marker=marker,s=55,label=f'seed {seed}')
 ax.axhline(0,color='black',linewidth=.8);finish(fig,ax,'02-reduction','Tỷ lệ giảm thời gian hành trình theo từng cặp seed\nDương: giảm; âm: tăng; High không ổn định','(Baseline − Green Wave) / Baseline (%)')
 fig,ax=plt.subplots(figsize=(8,4.5))
 for plan,marker in [('baseline','o'),('greenwave','x')]:
  for i,seed in enumerate(seeds):
   dx=(i-(len(seeds)-1)/2)*.08
   vals=[next(s for s in summary if s['level']==l and s['plan']==plan and int(s['seed'])==seed) for l in levels]
   ax.scatter([i+dx for i in range(3)],[float(s['travel_time_s_mean']) for s in vals],marker=marker,label=f'{plan} · {seed}')
 ax.set_ylim(bottom=0);finish(fig,ax,'05-seeds','Biến động giữa các seed · cohort A→D','Thời gian hành trình trung bình (s/xe)')
 fig,ax=plt.subplots(figsize=(8,4.5))
 for plan,dx in [('baseline',-.15),('greenwave',.15)]:
  vals=[next(d for d in diag if d['level']=='high' and d['plan']==plan and int(d['seed'])==s) for s in seeds]
  ax.bar([i+dx for i in range(len(seeds))],[int(d['pending_priority_3900']) for d in vals],width=.28,label=plan)
 ax.set_title('High · Xe ưu tiên chưa được chèn tại t=3900 s\nKhông đồng nhất xả hết xe với phục vụ ổn định',fontsize=12)
 ax.set_xticks(range(len(seeds)),[f'seed {s}' for s in seeds]);ax.set_ylabel('Số xe chờ ngoài mạng (xe)');ax.set_xlabel('Seed');ax.set_ylim(bottom=0);ax.legend();ax.grid(axis='y',alpha=.2)
 fig.tight_layout();fig.savefig(output/'06-overload.png',dpi=180);fig.savefig(output/'06-overload.svg');plt.close(fig)
 return output
