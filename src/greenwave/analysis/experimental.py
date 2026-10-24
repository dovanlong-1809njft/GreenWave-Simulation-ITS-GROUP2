"""Phân tích cohort dự kiến, kiểm chứng nguồn trước khi đọc số liệu; không đổi mô phỏng."""
import csv,hashlib,json,math,statistics,zipfile
from pathlib import Path
import xml.etree.ElementTree as ET
from greenwave.analysis.metrics import mean,reduction_percent
from greenwave.controllers.fixed_plans import require
from greenwave.simulation.experiments import check_seal
from greenwave.simulation.scenario_audit import audit_batch

PRIORITY=['W_A','A_B','B_C','C_D','D_E']
METRICS=('travel_time_s','waiting_time_s','time_loss_s','stops','depart_delay_s','total_requested_to_arrival_s')

def average(values):return mean(values) if values else None

def reduction(a,b):return reduction_percent(a,b) if a is not None and b is not None and a>0 else None

def group_route(edges):
    if edges==PRIORITY:return 'priority'
    if edges==['E_D','D_C','C_B','B_A','A_W']:return 'reverse'
    return 'cross'

def parse_vehicles(demand,trips,begin=300,end=3900):
    routes={r.get('id'):r.get('edges').split() for r in demand.findall('route')}
    vehicles=demand.findall('vehicle');ids=[v.get('id') for v in vehicles]
    require(len(set(ids))==len(ids),'Trùng ID nhu cầu')
    elements=trips.findall('tripinfo');tids=[t.get('id') for t in elements]
    require(len(set(tids))==len(tids) and set(tids)<=set(ids),'ID trip trùng/ngoài nhu cầu')
    lookup={t.get('id'):t for t in elements};result=[]
    def num(t,k):
        if t is None or t.get(k) is None:return None
        value=float(t.get(k));require(math.isfinite(value),'Trường số không hữu hạn')
        return value if value>=0 else None
    for v in vehicles:
        route=v.get('route');edges=routes.get(route)
        require(edges is not None,'Route thiếu trong snapshot')
        planned=float(v.get('depart'));require(math.isfinite(planned),'Sai thời điểm dự kiến')
        t=lookup.get(v.get('id'));dep,arr=num(t,'depart'),num(t,'arrival')
        complete=dep is not None and arr is not None
        if complete:
            require(arr>=dep,'Arrival trước departure')
            duration=num(t,'duration')
            require(duration is not None and abs(duration-(arr-dep))<=0.021,'SUMO duration khác arrival-depart')
        record={'vehicle_id':v.get('id'),'route_id':route,'route_edges':' '.join(edges),'group':group_route(edges),
                'cohort':'measurement' if begin<=planned<end else 'warmup',
                'planned_depart_s':planned,'actual_depart_s':dep,'arrival_s':arr,
                'status':'arrived' if complete else ('running' if dep is not None else 'not_departed'),
                'travel_time_s':arr-dep if complete else None,
                'waiting_time_s':num(t,'waitingTime') if complete else None,
                'time_loss_s':num(t,'timeLoss') if complete else None,
                'stops':num(t,'waitingCount') if complete else None,
                'depart_delay_s':dep-planned if dep is not None else None,
                'sumo_depart_delay_s':num(t,'departDelay'),
                'total_requested_to_arrival_s':arr-planned if complete else None}
        result.append(record)
    return result

def summarize(rows):
    selected=[r for r in rows if r['group']=='priority' and r['cohort']=='measurement']
    arrived=[r for r in selected if r['status']=='arrived']
    return {'n_requested':len(selected),'n_departed':sum(r['actual_depart_s'] is not None for r in selected),
            'n_arrived':len(arrived),'n_pending':sum(r['status']=='not_departed' for r in selected),
            'n_running':sum(r['status']=='running' for r in selected),
            'complete_cohort':bool(selected) and len(arrived)==len(selected),
            **{m+'_mean':average([r[m] for r in arrived if r[m] is not None]) for m in METRICS},
            **{m+'_n':sum(r[m] is not None for r in arrived) for m in METRICS}}

def paired(a,b):
    require(a and b,'Cặp cohort rỗng')
    ia={r['vehicle_id']:r for r in a};ib={r['vehicle_id']:r for r in b}
    require(set(ia)==set(ib),'Cặp khác tập xe dự kiến')
    require(all((ia[k]['planned_depart_s'],ia[k]['route_edges'])==(ib[k]['planned_depart_s'],ib[k]['route_edges']) for k in ia),'Cặp khác nhu cầu')
    common=[k for k in ia if ia[k]['status']=='arrived' and ib[k]['status']=='arrived']
    complete=len(common)==len(ia)
    row={'n_requested':len(ia),'n_common_arrived':len(common),'complete_pair':complete}
    for metric in METRICS:
        valid=[k for k in common if ia[k][metric] is not None and ib[k][metric] is not None]
        row[metric+'_n']=len(valid)
        av=average([ia[k][metric] for k in valid]);bv=average([ib[k][metric] for k in valid])
        row[metric+'_baseline']=av;row[metric+'_greenwave']=bv
        row[metric+'_difference_s' if metric!='stops' else 'stops_difference']=None if av is None or bv is None else av-bv
        row[metric+'_reduction_pct']=reduction(av,bv) if complete and len(valid)==len(ia) else None
    row['interpretation']='full_expected_cohort' if complete else 'conditional_common_arrivals_only_no_primary_conclusion'
    return row

def csv_write(path,rows):
    require(bool(rows),'Không xuất bảng rỗng')
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def analyze(batch,output):
    batch=Path(batch).resolve();output=Path(output).resolve()
    audit=audit_batch(batch)
    cases=json.loads((batch/'batch.json').read_text(encoding='utf-8'))['cases']
    require(len(cases)==len({x['case'] for x in cases}),'Batch có case trùng')
    allrows=[];summary=[];diagnostics=[];samples={};provenance={};common_inputs={}
    for case in cases:
        path=batch/case['case']/'sealed-run.zip';run,validation=check_seal(path)
        key=(run['level'],run['plan'],run['seed']);require(key not in samples,'Case level/plan/seed trùng')
        with zipfile.ZipFile(path) as z:
            c=json.loads(z.read('inputs/config/stage4-experiments.json'))
            # Không giả định tên route/ID: đọc lộ trình của từng vehicle từ snapshot thực.
            demand_name=next(n for n in run['input_sha256'] if n.endswith('.rou.xml'))
            rows=parse_vehicles(ET.fromstring(z.read('inputs/'+demand_name)),ET.fromstring(z.read('tripinfo.xml')),c['warmup_s'],c['warmup_s']+c['measurement_s'])
        require(len(rows)==validation['snapshots']['all'][str(7500)]['requested'],'Số xe không khớp GĐ4')
        require(sum(r['status']=='arrived' for r in rows)==validation['arrived_end'],'Arrived không khớp GĐ4')
        require(validation['collisions']==0 and validation['teleports']==0,'Không dùng run có sự cố an toàn')
        level,plan,seed=key;meta={'level':level,'plan':plan,'seed':seed}
        flagged=validation['overload_screen'] or validation['incomplete_end']
        samples[key]=[r for r in rows if r['group']=='priority' and r['cohort']=='measurement']
        summary.append({**meta,**summarize(rows),'overload_screen':flagged})
        allrows.extend({**meta,**r,'source_case':case['case'],'source_seal_sha256':hashlib.sha256(path.read_bytes()).hexdigest()} for r in rows)
        snap=validation['snapshots']['priority'];stop=c['warmup_s']+c['measurement_s'];finish=stop+c['drain_s']
        diagnostics.append({**meta,'overload_screen':flagged,'requested_priority_all':snap[str(finish)]['requested'],
                            'pending_priority_300':snap[str(c['warmup_s'])]['pending'],
                            'pending_priority_3900':snap[str(stop)]['pending'],'running_priority_3900':snap[str(stop)]['running'],
                            'pending_end':snap[str(finish)]['pending'],'running_end':snap[str(finish)]['running'],
                            'flow_after_A_vph':validation['detector_A_B_10m_flow_vph'],
                            'max_priority_insertion_delay_s':validation['max_priority_planned_to_actual_delay_s'],
                            'collisions':validation['collisions'],'teleports':validation['teleports']})
        provenance[case['case']]={'seal_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'run_source_platform':run['platform'],'input_sha256':run['input_sha256']}
        common_inputs[key]=run['input_sha256']
    pairs=[]
    for level,plan,seed in sorted(samples):
        if plan!='baseline':continue
        other=(level,'greenwave',seed);require(other in samples,'Thiếu phương án ghép cặp')
        left,right=common_inputs[(level,plan,seed)],common_inputs[other]
        require(all(left[n]==right[n] for n in left.keys() & right.keys()),'Cặp khác snapshot đầu vào chung')
        pairs.append({'level':level,'seed':seed,**paired(samples[(level,plan,seed)],samples[other])})
    require(len(pairs)*2==len(samples),'Có phương án không ghép được')
    aggregation=[]
    for level in sorted({p['level'] for p in pairs}):
        group=[p for p in pairs if p['level']==level]
        for metric in METRICS:
            record={'level':level,'metric':metric,'n_seeds':len(group),'overload_screen':any(s['overload_screen'] for s in summary if s['level']==level)}
            for name,suffix in [('baseline',metric+'_baseline'),('greenwave',metric+'_greenwave'),('paired_reduction_pct',metric+'_reduction_pct')]:
                vals=[p[suffix] for p in group if p[suffix] is not None]
                record[name+'_n_seeds']=len(vals);record[name+'_mean']=average(vals)
                record[name+'_sd']=statistics.stdev(vals) if len(vals)>1 else None
            aggregation.append(record)
    require(not output.exists(),'Thư mục phân tích đã tồn tại; chọn tên mới, không ghi đè')
    output.mkdir(parents=True)
    for name,data in [('vehicle_metrics',allrows),('scenario_summary',summary),('paired_comparison',pairs),('seed_aggregation',aggregation),('overload_diagnostics',diagnostics)]:csv_write(output/(name+'.csv'),data)
    manifest={'version':1,'source_batch':str(batch),'source_batch_sha256':hashlib.sha256((batch/'batch.json').read_bytes()).hexdigest(),
              'source_cases':provenance,'audit':audit,'primary_cohort':'priority route W_A A_B B_C C_D D_E, planned depart [300,3900)',
              'primary_measurement':'actual arrival minus actual departure; entire W-to-E route, not pure A-stopline to D-stopline',
              'seed_statistics':'equal seed weights, paired per seed, sample SD; no p-value or confidence interval',
              'incomplete_policy':'conditional common-arrivals means labelled; no primary reduction when cohort incomplete',
              'analysis_source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (output/'analysis_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return output
