"""Nhu cầu có seed, các cấu hình dùng chung route; không sửa mô hình GĐ2–3."""
import copy
from decimal import Decimal, ROUND_FLOOR
import hashlib
import json
import math
from pathlib import Path
import random
import xml.etree.ElementTree as ET

from greenwave.controllers.fixed_plans import require
from greenwave.simulation.model import write_xml
from greenwave.simulation.plan_validation import validate_plans

LEVELS = ('low', 'medium', 'high')
PLANS = ('baseline', 'greenwave')
CONFIG = 'config/stage4-experiments.json'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def settings(root):
    c = json.loads((Path(root)/CONFIG).read_text(encoding='utf-8'))
    require(c['schema_version'] == 1 and c['generator'] == 'stratified_uniform_v1', 'Không hỗ trợ phiên bản phát xe')
    require(c['levels_vph'] == dict(zip(LEVELS, (300,600,900))), 'Giữ ba mức nhu cầu đã công bố')
    require(c['plans'] == list(PLANS), 'Cần cả hai phương án')
    require(c['seeds'] and len(set(c['seeds'])) == len(c['seeds']) and all(type(s) is int and s>=0 for s in c['seeds']), 'Seed phải nguyên không âm, không trùng')
    for key in ('warmup_s','measurement_s','drain_s','reverse_vph','each_cross_direction_vph'):
        require(type(c[key]) is int and c[key]>0, key+' phải nguyên dương')
    require(c['warmup_s'] == 300 and c['measurement_s'] == 3600, 'Cửa sổ đã công bố là 300 + 3600 s')
    require(c['max_depart_delay_s'] == -1 and c['time_to_teleport_s'] == -1, 'Không được tự bỏ xe hoặc teleport')
    require(c['departure_position']=='base' and c['departure_speed']=='max' and c['precision_s']==0.001, 'Sai quy ước xuất phát')
    return c


def streams(c, level):
    return [('east','main_east',c['levels_vph'][level],True),
            ('west','main_west',c['reverse_vph'],False)] + [
        (j+suffix,j+'_'+direction,c['each_cross_direction_vph'],False)
        for j in 'ABCD' for suffix,direction in [('S','south'),('N','north')]]


def schedule(c, level, seed):
    """Mỗi cửa sổ có n=floor(q*T/3600) xe, một xe ngẫu nhiên/mỗi ô thời gian bằng nhau."""
    require(level in LEVELS and type(seed) is int and seed>=0, 'Sai level hoặc seed')
    rows=[]
    for stream, route, rate, priority in streams(c,level):
        for cohort,begin,duration in [('warmup',0,c['warmup_s']),('measurement',c['warmup_s'],c['measurement_s'])]:
            n=int((Decimal(rate)*Decimal(duration)/Decimal(3600)).to_integral_value(rounding=ROUND_FLOOR))
            if not n:continue
            # Hash theo luồng/cửa sổ: luồng nền giống nhau cả khi đổi mức nhu cầu chính.
            key=f'stratified_uniform_v1|{seed}|{stream}|{cohort}'
            rng=random.Random(int(hashlib.sha256(key.encode()).hexdigest(),16))
            width=duration/n
            for i in range(n):
                depart=round(begin+(i+rng.random())*width,3)
                depart=min(depart,begin+duration-0.001)
                rows.append({'id':f'{stream}.{cohort}.{i:05d}', 'stream':stream,
                             'route':route,'priority':priority,'cohort':cohort,
                             'planned_depart_s':depart})
    return sorted(rows,key=lambda row:(row['planned_depart_s'],row['id']))


def route_path(level, seed):
    return f'simulation/routes/generated/stage4/{level}_seed{seed}.rou.xml'


def scenario_path(level, plan, seed):
    return f'simulation/scenarios/experiments/{level}_{plan}_seed{seed}.sumocfg'


def route_tree(root, rows):
    sample=ET.parse(Path(root)/'simulation/routes/source/sample.rou.xml').getroot()
    result=ET.Element('routes')
    for node in sample:
        if node.tag in ('vType','route'):result.append(copy.deepcopy(node))
    for row in rows:
        vehicle=ET.SubElement(result,'vehicle',id=row['id'],type='car',route=row['route'],
                             depart=f"{row['planned_depart_s']:.3f}",departLane='0',departPos='base',departSpeed='max',
                             color='1,0.7,0' if row['priority'] else '0.2,0.6,0.9')
    return result


def config_tree(c, level, plan, seed):
    root=ET.Element('configuration');inp=ET.SubElement(root,'input')
    for key,value in [('net-file','../../network/generated/corridor.net.xml'),
                      ('route-files',f'../../routes/generated/stage4/{level}_seed{seed}.rou.xml'),
                      ('additional-files',f'../../signals/{plan}.add.xml')]:
        ET.SubElement(inp,key,value=value)
    time=ET.SubElement(root,'time')
    for key,value in [('begin',0),('end',c['warmup_s']+c['measurement_s']+c['drain_s']),('step-length',1)]:
        ET.SubElement(time,key,value=str(value))
    process=ET.SubElement(root,'processing')
    for key in ('time-to-teleport','max-depart-delay'):ET.SubElement(process,key,value='-1')
    random_node=ET.SubElement(root,'random_number');ET.SubElement(random_node,'seed',value=str(seed))
    return root


def xml_bytes(element):
    """Chuẩn hóa độc lập XML trình bày để kiểm tra file sinh, không ghi đè nguồn."""
    attrs=sorted((k,v) for k,v in element.attrib.items() if 'SchemaLocation' not in k)
    return (element.tag,attrs,[xml_bytes(n) for n in element])


def build(root, levels=LEVELS, seeds=None):
    root=Path(root).resolve();validate_plans(root);c=settings(root)
    seeds=c['seeds'] if seeds is None else seeds
    require(levels and set(levels)<=set(LEVELS), 'Sai danh sách level')
    require(seeds and all(type(s) is int and s>=0 for s in seeds), 'Sai danh sách seed')
    # Tạo toàn bộ vào thư mục tạm; kiểm tra xung đột trước khi ghi bất kỳ đích nào.
    import tempfile
    targets=[]
    with tempfile.TemporaryDirectory() as temp:
        for level in levels:
            for seed in seeds:
                items=[(route_path(level,seed),route_tree(root,schedule(c,level,seed)))] + [
                    (scenario_path(level,plan,seed),config_tree(c,level,plan,seed)) for plan in PLANS]
                for name,tree in items:
                    staged=Path(temp)/name;write_xml(staged,tree)
                    dest=root/name
                    require(not dest.exists() or dest.read_bytes()==staged.read_bytes(),
                            'Đích đã có nội dung khác; không ghi đè: '+name)
                    targets.append((staged,dest))
        for staged,dest in targets:
            if not dest.exists():
                dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(staged.read_bytes())
    return [str(dest.relative_to(root)) for _,dest in targets]


def verify_files(root, levels=LEVELS, seeds=None):
    root=Path(root).resolve();validate_plans(root);c=settings(root)
    seeds=c['seeds'] if seeds is None else seeds
    net=ET.parse(root/'simulation/network/generated/corridor.net.xml').getroot()
    edges={e.get('id') for e in net.findall('edge')}
    connections={(x.get('from'),x.get('to')) for x in net.findall('connection')}
    reports=[]
    for level in levels:
        for seed in seeds:
            rows=schedule(c,level,seed);p=root/route_path(level,seed)
            actual=ET.parse(p).getroot()
            require(xml_bytes(actual)==xml_bytes(route_tree(root,rows)), 'Nhu cầu khác thuật toán/seed: '+str(p))
            vehicles=actual.findall('vehicle');ids=[v.get('id') for v in vehicles]
            require(len(ids)==len(set(ids)), 'ID xe trùng')
            route_map={r.get('id'):r.get('edges').split() for r in actual.findall('route')}
            for path in route_map.values():
                require(all(e in edges for e in path) and all(x in connections for x in zip(path,path[1:])), 'Route không nối liên tục')
            cfgs=[]
            for plan in PLANS:
                name=scenario_path(level,plan,seed);cfg=ET.parse(root/name).getroot()
                require(xml_bytes(cfg)==xml_bytes(config_tree(c,level,plan,seed)), 'Cấu hình khác thiết kế: '+name)
                for key in ('net-file','route-files','additional-files'):
                    require((root/name).parent.joinpath(cfg.find('input/'+key).get('value')).is_file(), 'Thiếu tệp tham chiếu')
                cfg.find('input/additional-files').set('value','same-signals-except-offset')
                cfgs.append(xml_bytes(cfg))
            require(cfgs[0]==cfgs[1], 'Cặp phương án khác tham số chung')
            counts={s:sum(r['stream']==s for r in rows) for s,_,_,_ in streams(c,level)}
            reports.append({'level':level,'seed':seed,'demand_sha256':sha(p),'requested_total':len(rows),
                            'requested_priority':counts['east'],'counts_per_stream':counts,
                            'priority_measurement':sum(r['priority'] and r['cohort']=='measurement' for r in rows),
                            'pair_uses_same_route':True})
    return reports
