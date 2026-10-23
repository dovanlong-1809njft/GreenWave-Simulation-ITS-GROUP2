"""Kiểm tra bằng chứng tệp và hash, không so sánh hiệu quả giữa phương án."""
import json
from pathlib import Path
from greenwave.controllers.fixed_plans import require
from greenwave.simulation.scenarios import sha
from greenwave.simulation.experiments import evidence_digest


def audit_batch(path, repeat=None):
    path=Path(path).resolve();batch=json.loads((path/'batch.json').read_text(encoding='utf-8'))
    cases={x['case']:x for x in batch['cases']}
    manifests={}
    for name,case in cases.items():
        require(case['status']=='ok','Có case lỗi: '+name)
        sealed=path/name/'sealed-run.zip'
        require(sha(sealed)==case['report']['sealed_run_sha256'],'Gói lượt chạy thay đổi: '+name)
        from greenwave.simulation.experiments import check_seal
        run,result=check_seal(sealed)
        require(result['behavior_sha256']==case['report']['behavior_sha256'],'Kết quả batch khác gói lượt chạy')
        manifests[name]=run
    pairs=[]
    for name,case in cases.items():
        r=case['report']
        if r['plan']!='baseline':continue
        other=f"{r['level']}_greenwave_seed{r['seed']}"
        if other in cases:
            b=cases[other]['report']
            require(r['route_sha256']==b['route_sha256'],'Nhu cầu cặp khác nhau')
            ar=manifests[name]['input_sha256']
            br=manifests[other]['input_sha256']
            require(all(ar[k]==br[k] for k in ar.keys() & br.keys()),'Đầu vào chung khác nhau')
            pairs.append([name,other])
    matched=[]
    if repeat:
        second=audit_batch(repeat)
        repeat_batch=json.loads((Path(repeat)/'batch.json').read_text(encoding='utf-8'))
        for case in repeat_batch['cases']:
            name=case['case'];require(name in cases,'Không có case gốc để so sánh')
            a,b=cases[name]['report'],case['report']
            require(a['route_sha256']==b['route_sha256'] and a['behavior_sha256']==b['behavior_sha256'], 'Không tái lập: '+name)
            matched.append(name)
    return {'cases_verified':len(cases),'fair_pairs':pairs,'repeat_cases_identical':matched,
            'capacity_limits_present':batch['status']=='finished_with_capacity_limits'}
