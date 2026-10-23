"""Chạy kịch bản với thư mục riêng; giữ số xe pending/unfinished để tránh thiên lệch."""
import csv
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import xml.etree.ElementTree as ET
import zipfile

from greenwave.controllers.fixed_plans import require
from greenwave.simulation.model import binary, write_xml
from greenwave.simulation.scenarios import (
    CONFIG, LEVELS, PLANS, route_path, scenario_path, schedule, settings, sha, verify_files,
)


def dump(path, data):
    temporary=path.with_name(path.name+'.tmp')
    with temporary.open('w',encoding='utf-8') as stream:
        stream.write(json.dumps(data,ensure_ascii=False,indent=2)+'\n');stream.flush();os.fsync(stream.fileno())
    os.replace(temporary,path)



def digest_bytes(name,data):
    """Hash XML có nghĩa, hoặc byte chính xác cho CSV/JSON."""
    if Path(name).suffix!='.xml':return hashlib.sha256(data).hexdigest()
    def clean(node):
        if node.tag=='performance':return None
        attrs={k:v for k,v in node.attrib.items() if not (node.tag=='step' and k=='duration')}
        return [node.tag,sorted(attrs.items()),[clean(n) for n in node if n.tag!='performance']]
    return hashlib.sha256(json.dumps(clean(ET.fromstring(data)),sort_keys=True,separators=(',',':')).encode()).hexdigest()


def evidence_digest(path):
    return digest_bytes(str(path),Path(path).read_bytes())


def check_seal(path):
    """Kiểm tra đúng bytes trong gói niêm phong, không dựa vào tệp rời có thể đổi sau chạy."""
    with zipfile.ZipFile(path) as z:
        require(z.testzip() is None,'Gói lượt chạy lỗi CRC')
        metadata=json.loads(z.read('run.json'))
        require(metadata.get('status') in ('completed','completed_with_limits','unsafe'), 'Metadata lượt chạy chưa hoàn tất')
        for name,digest in metadata['input_sha256'].items():
            require(hashlib.sha256(z.read('inputs/'+name)).hexdigest()==digest,'Snapshot trong gói đã đổi')
        for name,digest in metadata['output_structural_sha256'].items():
            require(digest_bytes(name,z.read(name))==digest,'Đầu ra trong gói đã đổi: '+name)
        return metadata,json.loads(z.read('validation.json'))


def rows_csv(path, rows):
    with path.open('w',encoding='utf-8',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)


def state_counts(rows, cutoff):
    """Trạng thái cohort theo thời gian dự kiến; cutoff là biên phải loại trừ."""
    selected=[r for r in rows if r['planned_depart_s']<cutoff]
    inserted=[r for r in selected if r['actual_depart_s'] is not None and r['actual_depart_s']<cutoff]
    arrived=[r for r in inserted if r['arrival_s'] is not None and r['arrival_s']<cutoff]
    return {'requested':len(selected),'departed':len(inserted),'arrived':len(arrived),
            'pending':len(selected)-len(inserted),'running':len(inserted)-len(arrived)}


def read_results(root, directory, level, seed):
    c=settings(root);demand=schedule(c,level,seed)
    trips={t.get('id'):t.attrib for t in ET.parse(directory/'tripinfo.xml').getroot().findall('tripinfo')}
    require(set(trips)<=set(r['id'] for r in demand), 'SUMO trả ID không có trong nhu cầu')
    records=[]
    for vehicle in demand:
        raw=trips.get(vehicle['id'],{})
        def number(key):
            v=raw.get(key)
            return float(v) if v is not None and float(v)>=0 else None
        depart,arrival=number('depart'),number('arrival')
        record={**vehicle,'actual_depart_s':depart,'arrival_s':arrival,
                'status':'arrived' if arrival is not None else ('running' if depart is not None else 'not_departed'),
                'depart_delay_sumo_s':number('departDelay'),
                'planned_to_actual_delay_s':None if depart is None else round(depart-vehicle['planned_depart_s'],3),
                'travel_time_s':number('duration'),'waiting_time_s':number('waitingTime'),
                'time_loss_s':number('timeLoss'),'stops_waiting_episodes':number('waitingCount')}
        records.append(record)
    warm=c['warmup_s'];stop=warm+c['measurement_s'];end=stop+c['drain_s']
    by_group={}
    for name,selected in [('all',records),('priority',[r for r in records if r['priority']]),
                           ('priority_measurement',[r for r in records if r['priority'] and r['cohort']=='measurement'])]:
        by_group[name]={str(t):state_counts(selected,t) for t in (warm,stop,end)}
    summary=ET.parse(directory/'summary.xml').getroot().findall('step')
    require(summary, 'Không có summary')
    final=by_group['all'][str(end)]
    require(int(summary[-1].get('inserted'))==final['departed'] and int(summary[-1].get('arrived'))==final['arrived'], 'Đếm xe khác summary SUMO')
    require(int(summary[-1].get('running'))==final['running'] and int(summary[-1].get('waiting'))==final['pending'], 'Trạng thái cuối khác summary')
    require(final['requested']==final['pending']+final['running']+final['arrived'], 'Không bảo toàn số xe')
    require(all(int(s.get('discarded','0'))==0 for s in summary), 'Có xe bị SUMO loại bỏ')
    collisions=len(ET.parse(directory/'collisions.xml').getroot().findall('collision'))
    stats=ET.parse(directory/'statistics.xml').getroot()
    tele=stats.find('teleports');teleports=int(tele.get('total','0')) if tele is not None else None
    require(teleports is not None, 'Thiếu thống kê teleport')
    detector=ET.parse(directory/'A_detector.xml').getroot().findall('interval')
    measured=[x for x in detector if float(x.get('begin'))>=warm and float(x.get('end'))<=stop]
    # nVehContrib: xe đã hoàn tất qua vòng từ, không dùng nVehEntered đếm lặp xe chờ.
    crossing=sum(int(x.get('nVehContrib')) for x in measured)
    require(sum(float(x.get('end'))-float(x.get('begin')) for x in measured)==c['measurement_s'], 'Detector không phủ đủ cửa sổ đo')
    warnings=(directory/'sumo.stderr.txt').read_text(encoding='utf-8').splitlines()
    report={'level':level,'seed':seed,'snapshots':by_group,'collisions':collisions,'teleports':teleports,
            'pending_end':final['pending'],'running_end':final['running'],'arrived_end':final['arrived'],
            'detector_A_B_10m_count_measurement':crossing,
            'detector_A_B_10m_flow_vph':crossing*3600/c['measurement_s'],
            'max_waiting_insertion_all':max(int(s.get('waiting')) for s in summary),
            'max_halting_all':max(int(s.get('halting')) for s in summary),
            'max_priority_planned_to_actual_delay_s':max((r['planned_to_actual_delay_s'] or 0) for r in records if r['priority']),
            'warning_lines':warnings,
            'overload_screen':by_group['priority'][str(stop)]['pending']>by_group['priority'][str(warm)]['pending'],
            'incomplete_end':final['pending']>0 or final['running']>0,
            'metrics_note':'stops = native SUMO waitingCount episodes at speed <= 0.1m/s; partial metrics marked by status'}
    rows_csv(directory/'vehicles.csv',records)
    # Dữ liệu tái lập loại thời gian tính toán/chú thích timestamp XML, giữ hành vi mô phỏng.
    normalized={'vehicles':records,'summary':[{k:v for k,v in x.attrib.items() if k!='duration'} for x in summary],
                'detector':[x.attrib for x in detector]}
    report['behavior_sha256']=hashlib.sha256(json.dumps(normalized,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return report


def run_case(root, level, plan, seed, directory):
    root=Path(root).resolve();directory=Path(directory).resolve()
    require(level in LEVELS and plan in PLANS,'Sai tổ hợp')
    verify_files(root,[level],[seed])
    directory.mkdir(parents=True,exist_ok=False)  # Không ghi đè lượt chạy cũ.
    c=settings(root)
    input_names=[CONFIG,'config/network.json','config/signals.json',
                 'simulation/network/generated/corridor.net.xml',route_path(level,seed),
                 f'simulation/signals/{plan}.add.xml',scenario_path(level,plan,seed)]
    hashes={}
    for name in input_names:
        dest=directory/'inputs'/name;dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes((root/name).read_bytes());hashes[name]=sha(dest)
    # Chạy trên snapshot vừa lưu, không đọc tệp mutable trong project khi SUMO đang chạy.
    snapshot=directory/'inputs'
    events=ET.Element('additional')
    ET.SubElement(events,'inductionLoop',id='priority_after_A',lane='A_B_0',pos='10',
                  period='60',file=str(directory/'A_detector.xml'))
    write_xml(directory/'detector.add.xml',events)
    command=[binary('sumo'),'-c',str(snapshot/scenario_path(level,plan,seed)),
             '--additional-files',str(snapshot/f'simulation/signals/{plan}.add.xml')+','+str(directory/'detector.add.xml'),
             '--tripinfo-output',str(directory/'tripinfo.xml'),
             '--tripinfo-output.write-unfinished','true','--tripinfo-output.write-undeparted','true',
             '--summary-output',str(directory/'summary.xml'),
             '--statistic-output',str(directory/'statistics.xml'),
             '--collision-output',str(directory/'collisions.xml'),
             '--xml-validation','always','--no-step-log','true']
    manifest={'level':level,'plan':plan,'seed':seed,'input_sha256':hashes,
              'sumo_version':subprocess.check_output([binary('sumo'),'--version'],text=True).splitlines()[0],
              'python_version':platform.python_version(),'platform':platform.system(),
              'hash_method':'XML structure excluding generated comments/performance, CSV/JSON exact bytes',
              'implementation_sha256':{n:sha(p) for n,p in {
                  'greenwave.simulation.scenarios':Path(__file__).with_name('scenarios.py'),
                  'greenwave.simulation.experiments':Path(__file__),
                  'greenwave.controllers.fixed_plans':Path(__file__).parents[1]/'controllers/fixed_plans.py'}.items()},
              'command':command,'created_utc':datetime.now(timezone.utc).isoformat(),'status':'started'}
    dump(directory/'run.json',manifest)
    result=subprocess.run(command,capture_output=True,text=True)
    (directory/'sumo.stdout.txt').write_text(result.stdout,encoding='utf-8')
    (directory/'sumo.stderr.txt').write_text(result.stderr,encoding='utf-8')
    manifest['exit_code']=result.returncode
    if result.returncode:
        manifest['status']='sumo_error';dump(directory/'run.json',manifest)
        raise RuntimeError('SUMO lỗi, xem '+str(directory/'sumo.stderr.txt'))
    try:report=read_results(snapshot,directory,level,seed)
    except Exception:
        manifest['status']='validation_error';dump(directory/'run.json',manifest);raise
    report['plan']=plan;report['route_sha256']=hashes[route_path(level,seed)]
    manifest['status']='completed_with_limits' if report['overload_screen'] or report['incomplete_end'] or report['warning_lines'] else 'completed'
    if report['collisions'] or report['teleports']:
        manifest['status']='unsafe'
    dump(directory/'validation.json',report)
    manifest['output_structural_sha256']={name:evidence_digest(directory/name) for name in ['tripinfo.xml','summary.xml','statistics.xml','collisions.xml','A_detector.xml','vehicles.csv','validation.json','sumo.stdout.txt','sumo.stderr.txt']}
    dump(directory/'run.json',manifest)
    sealed=directory/'sealed-run.zip'
    with zipfile.ZipFile(sealed,'w',zipfile.ZIP_DEFLATED) as archive:
        for p in sorted(directory.rglob('*')):
            if p.is_file() and p!=sealed and p.suffix!='.tmp':archive.write(p,p.relative_to(directory).as_posix())
    check_seal(sealed)
    report['sealed_run_sha256']=sha(sealed)
    return report


def run_batch(root, levels=LEVELS, plans=PLANS, seeds=(11,), batch_id=None):
    root=Path(root).resolve()
    require(levels and plans and seeds and set(levels)<=set(LEVELS) and set(plans)<=set(PLANS),'Sai lựa chọn batch')
    batch_id=batch_id or datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    require(batch_id and all(x.isalnum() or x in '-_' for x in batch_id), 'batch-id chỉ dùng chữ, số, - hoặc _')
    require(len(set(levels))==len(levels) and len(set(plans))==len(plans) and len(set(seeds))==len(seeds),'Không lặp lại case trong cùng batch')
    verify_files(root,levels,seeds)
    output=root/'results/raw/stage4'/batch_id
    output.mkdir(parents=True,exist_ok=False)
    records=[]
    dump(output/'batch.json',{'batch_id':batch_id,'status':'started','cases':[]})
    for level in levels:
        for seed in seeds:
            for plan in plans:
                name=f'{level}_{plan}_seed{seed}'
                try:
                    report=run_case(root,level,plan,seed,output/name)
                    records.append({'case':name,'status':'failed_safety' if report['collisions'] or report['teleports'] else 'ok','report':report})
                    print(f"{name}: arrived={report['arrived_end']}, pending_end={report['pending_end']}, overload_screen={report['overload_screen']}",flush=True)
                except Exception as error:
                    records.append({'case':name,'status':'failed','error':str(error)})
                    print(f'{name}: FAILED {error}',flush=True)
                dump(output/'batch.json',{'batch_id':batch_id,'status':'running','cases':records})
    limited=any(r.get('report',{}).get('overload_screen') or r.get('report',{}).get('incomplete_end') for r in records)
    dump(output/'batch.json',{'batch_id':batch_id,'status':'finished_with_capacity_limits' if limited else 'finished','cases':records})
    if limited: print('LIMIT: có tăng tồn đọng hoặc chưa xả hết xe; không nghiệm thu khả năng phục vụ ổn định.',flush=True)
    require(all(r['status']=='ok' for r in records),'Có lượt chạy lỗi; xem '+str(output/'batch.json'))
    # Không tự coi overload_screen là đạt năng lực; dữ liệu được giữ để báo cáo giới hạn.
    return output
