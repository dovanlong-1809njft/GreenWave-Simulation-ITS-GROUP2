"""Kiểm chứng hai lịch tín hiệu bằng log SUMO, không xếp hạng hiệu quả."""
import csv
import hashlib
import json
import math
import platform
from pathlib import Path
import subprocess
import tempfile
import xml.etree.ElementTree as ET

from greenwave.controllers.fixed_plans import (
    PLANS, parameters, phase_at, require, signal_tree, topology,
)
from greenwave.simulation.model import binary, write_xml
from greenwave.simulation.validation import validate as validate_sample


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(element):
    """Bỏ khác biệt trình bày/schema; giữ toàn bộ thuộc tính có nghĩa."""
    return (element.tag, sorted((k, v) for k, v in element.attrib.items()
                               if 'SchemaLocation' not in k),
            [canonical(c) for c in element])


def validate_plans(root):
    root = Path(root).resolve()
    validate_sample(root)  # Giữ kiểm tra mô hình/xe mẫu đang chạy của GĐ2.
    params = parameters(root)
    net, links = topology(root, params)
    expected_routes = ['W_A', 'A_B', 'B_C', 'C_D', 'D_E']
    routes = ET.parse(root / 'simulation/routes/source/sample.rou.xml').getroot()
    route = next(r for r in routes.findall('route') if r.get('id') == 'main_east')
    require(route.get('edges').split() == expected_routes, 'Hướng xe ưu tiên không khớp tuyến')
    speed = params['speed_kmh'] / 3.6
    edges = {e.get('id'): e for e in net.findall('edge')}
    for edge in expected_routes:
        require(all(math.isclose(float(l.get('speed')), speed, abs_tol=0.01)
                    for l in edges[edge].findall('lane')), 'Tốc độ mạng khác cấu hình')
    template = ET.parse(root / 'simulation/scenarios/sample.sumocfg').getroot()
    normalized_configs = []
    for plan in PLANS:
        actual = ET.parse(root / f'simulation/signals/{plan}.add.xml').getroot()
        require(canonical(actual) == canonical(signal_tree(params, links, plan)),
                f'{plan}: pha/offset/ánh xạ tín hiệu khác cấu hình đầu vào')
        # Kiểm tra xung đột độc lập bằng ma trận foes do NETCONVERT sinh.
        for logic in actual.findall('tlLogic'):
            jid = logic.get('id')
            junction = next(j for j in net.findall('junction') if j.get('id') == jid)
            internal = junction.get('intLanes').split()
            requests = {int(q.get('index')): q.get('foes')[::-1]
                        for q in junction.findall('request')}
            for phase in logic.findall('phase'):
                state = phase.get('state')
                active = [c for c in links[jid] if state[int(c.get('linkIndex'))] in 'Gy']
                for a in active:
                    for b in active:
                        require(requests[internal.index(a.get('via'))][internal.index(b.get('via'))] == '0',
                                'Các dòng xung đột cùng được cấp quyền đi')
        config = ET.parse(root / f'simulation/scenarios/{plan}.sumocfg').getroot()
        field = config.find('input/additional-files')
        require(field.get('value') == f'../signals/{plan}.add.xml', 'Sai file tín hiệu')
        for key in ('net-file', 'route-files', 'additional-files'):
            for ref in config.find('input/' + key).get('value').split(','):
                require((root / 'simulation/scenarios' / ref).is_file(), 'Thiếu file cấu hình: '+ref)
        field.set('value', template.find('input/additional-files').get('value'))
        require(canonical(config) == canonical(template),
                'Hai phương án chỉ được khác tham chiếu chương trình đèn')
        normalized_configs.append(canonical(config))
    require(normalized_configs[0] == normalized_configs[1], 'Các tham số chung khác nhau')
    require(params['offsets_s']['baseline'] != params['offsets_s']['greenwave'],
            'Hai lịch trùng nhau: không thể chứng minh cơ chế khác biệt')
    return params


def configuration_time(root, plan):
    config = ET.parse(root / f'simulation/scenarios/{plan}.sumocfg').getroot()
    begin = float(config.find('time/begin').get('value'))
    end = float(config.find('time/end').get('value'))
    step = float(config.find('time/step-length').get('value'))
    require(begin == 0 and step == 1 and end >= 360 and end == int(end),
            'Bài kiểm chứng yêu cầu bắt đầu 0, bước 1 s và ít nhất 3 chu kỳ mẫu')
    return begin, end, step


def run_capture(root, plan, params, directory):
    """Đọc trạng thái thực ở mọi bước và xác minh độc lập với thứ tự XML."""
    directory.mkdir(parents=True, exist_ok=True)
    events = ET.Element('additional')
    for j in 'ABCD':
        ET.SubElement(events, 'timedEvent', type='SaveTLSStates', source=j,
                      dest=str(directory / f'{j}.xml'))
    write_xml(directory / 'events.add.xml', events)
    result = subprocess.run([
        binary('sumo'), '-c', str(root / f'simulation/scenarios/{plan}.sumocfg'),
        '--additional-files', str(root / f'simulation/signals/{plan}.add.xml') + ',' + str(directory / 'events.add.xml'),
        '--tripinfo-output', str(directory / 'trips.xml'),
        '--summary-output', str(directory / 'summary.xml'),
        '--vehroute-output', str(directory / 'routes.xml'),
        '--no-step-log', 'true', '--xml-validation', 'always',
    ], capture_output=True, text=True)
    require(result.returncode == 0, 'SUMO thất bại: ' + result.stderr)
    require('Error:' not in result.stderr and 'Warning:' not in result.stderr,
            'SUMO báo lỗi/cảnh báo: ' + result.stderr)
    begin, end, step = configuration_time(root, plan)
    signals = ET.parse(root / f'simulation/signals/{plan}.add.xml').getroot()
    tls = {t.get('id'): t for t in signals.findall('tlLogic')}
    trace, starts = [], []
    for j, offset in zip('ABCD', params['offsets_s'][plan]):
        rows = ET.parse(directory / f'{j}.xml').getroot().findall('tlsState')
        require(len(rows) == int((end-begin)/step), f'{j}: thiếu bản ghi trạng thái')
        phases = tls[j].findall('phase')
        previous_phase = None
        observed_starts = []
        for n, rec in enumerate(rows):
            t = float(rec.get('time'))
            require(t == begin+n*step, 'Thiếu hoặc trùng mốc log')
            expected = phase_at(t, offset, params['durations_s'])
            require(rec.get('programID') == plan and int(rec.get('phase')) == expected
                    and rec.get('state') == phases[expected].get('state'),
                    f'{plan}/{j}: sai trạng thái tại t={t}')
            trace.append({'plan':plan, 'junction':j, 'time_s':t,
                          'phase':int(rec.get('phase')), 'state':rec.get('state'),
                          'program':rec.get('programID')})
            # Không nhầm cửa sổ xanh đã bắt đầu từ chu kỳ âm với sự kiện bật xanh t=0.
            if expected == 0 and (previous_phase not in (None, 0)
                                  or (n == 0 and (t-offset) % params['cycle_s'] == 0)):
                observed_starts.append(t)
                starts.append({'plan':plan, 'junction':j, 'time_s':t,
                               'offset_s':offset, 'kind':'boundary_at_begin' if n==0 else 'red_to_green'})
            previous_phase = expected
        expected_starts = [float(t) for t in range(int(begin), int(end))
                           if (t-offset) % params['cycle_s'] == 0]
        require(observed_starts == expected_starts, 'Thời điểm bật xanh không khớp offset')
        require(all(b-a == params['cycle_s'] for a,b in zip(observed_starts,observed_starts[1:])),
                'Chu kỳ thực đo không đúng')
    trips = ET.parse(directory/'trips.xml').getroot().findall('tripinfo')
    require(len(trips) == 85, 'Chưa có đủ 85 xe hoàn tất')
    steps = ET.parse(directory/'summary.xml').getroot().findall('step')
    require(steps[-1].get('running') == '0' and steps[-1].get('waiting') == '0', 'Còn xe chưa hoàn tất')
    require(all(int(s.get('collisions','0')) == 0 and int(s.get('teleports','0')) == 0 for s in steps),
            'Có va chạm hoặc teleport')
    vehicles = ET.parse(directory/'routes.xml').getroot().findall('vehicle')
    east = [v for v in vehicles if v.get('id').startswith('east.')]
    require(len(east) == 30 and all(v.find('route').get('edges') == 'W_A A_B B_C C_D D_E' for v in east),
            'Xe hướng ưu tiên không qua đúng tuyến')
    trip_signature = sorted((t.get('id'), t.get('depart'), t.get('arrival'), t.get('duration')) for t in trips)
    return {'trace':trace, 'starts':starts,
            'trace_sha256':digest(trace), 'trips_sha256':digest(trip_signature),
            'arrived':len(trips), 'collisions':0, 'teleports':0,
            'end_s':end, 'seed':ET.parse(root/f'simulation/scenarios/{plan}.sumocfg').getroot().find('random_number/seed').get('value')}


def write_csv(path, rows):
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def verify(root, output=None):
    """Chạy mỗi phương án hai lần; so hash log và hành trình, giữ minh chứng lần đầu."""
    root = Path(root).resolve()
    params = validate_plans(root)
    public = {'parameters':params, 'scope':'Signal mechanism only; no efficiency comparison',
              'python_version':platform.python_version(), 'platform':platform.system(),
              'sumo_version':subprocess.check_output([binary('sumo'),'--version'],text=True).splitlines()[0],
              'plans':{}}
    captures = {}
    with tempfile.TemporaryDirectory(prefix='greenwave-stage3-') as temp:
        for plan in PLANS:
            first = run_capture(root, plan, params, Path(temp)/plan/'first')
            second = run_capture(root, plan, params, Path(temp)/plan/'repeat')
            require(first['trace_sha256'] == second['trace_sha256'] and first['trips_sha256'] == second['trips_sha256'],
                    'Không tái lập cùng seed và cấu hình')
            public['plans'][plan] = {k:v for k,v in first.items() if k not in ('trace','starts')}
            public['plans'][plan]['repeat_identical'] = True
            public['plans'][plan]['tls_records_per_run'] = len(first['trace'])
            public['plans'][plan]['green_starts_s'] = {
                j:[r['time_s'] for r in first['starts'] if r['junction']==j] for j in 'ABCD'}
            captures[plan] = first
    a,b = captures['baseline']['trace'],captures['greenwave']['trace']
    require(any(x['phase'] != y['phase'] or x['state'] != y['state'] for x,y in zip(a,b)),
            'Hai phương án không khác lịch thực')
    inputs = ['config/network.json','config/signals.json', 'simulation/network/generated/corridor.net.xml',
              'simulation/routes/source/sample.rou.xml', 'simulation/scenarios/sample.sumocfg',
              'src/greenwave/algorithms/offset.py', 'src/greenwave/controllers/fixed_plans.py',
              'src/greenwave/simulation/plan_validation.py'] + [f'simulation/{folder}/{plan}.{ext}'
                for plan in PLANS for folder,ext in [('signals','add.xml'),('scenarios','sumocfg')]]
    public['input_sha256'] = {p:file_hash(root/p) for p in inputs}
    public['different_signal_schedules'] = True
    public['runs_completed'] = 4
    if output is not None:
        output = Path(output).resolve()
        output.mkdir(parents=True, exist_ok=True)
        for plan, data in captures.items():
            write_csv(output/f'{plan}-tls.csv', data['trace'])
            write_csv(output/f'{plan}-green-starts.csv', data['starts'])
        (output/'verification.json').write_text(json.dumps(public,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return public
