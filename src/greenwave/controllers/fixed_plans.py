"""Hai kế hoạch định thời; tái sử dụng mạng và xe mẫu Giai đoạn 2."""
import copy
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET

from greenwave.algorithms.offset import corridor_offsets, travel_time_seconds
from greenwave.simulation.model import write_xml

PHASE_KEYS = (
    'main_green_s', 'main_yellow_s', 'all_red_after_main_s',
    'cross_green_s', 'cross_yellow_s', 'all_red_after_cross_s',
)
PLANS = ('baseline', 'greenwave')
MAIN = ('G', 'y', 'r', 'r', 'r', 'r')
CROSS = ('r', 'r', 'r', 'G', 'y', 'r')


def require(condition, message):
    """Kiểm tra vẫn hoạt động nếu Python chạy với -O."""
    if not condition:
        raise ValueError(message)


def finite_number(value, label, positive=True):
    require(isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value), f'{label} phải là số hữu hạn')
    require(value > 0 if positive else value >= 0, f'{label} ngoài miền hợp lệ')
    return float(value)


def parameters(root):
    network = json.loads((root / 'config/network.json').read_text(encoding='utf-8'))
    signal = json.loads((root / 'config/signals.json').read_text(encoding='utf-8'))
    require(network['junctions'] == list('ABCD'), 'Giai đoạn 3 chỉ hỗ trợ A–B–C–D')
    require(network['priority_direction'] == 'A_to_D', 'Hướng ưu tiên phải là A_to_D')
    spacing = network['intersections_spacing_m']
    require(len(spacing) == 3, 'Cần ba khoảng cách giữa bốn nút')
    spacing = [finite_number(v, 'Khoảng cách (m)') for v in spacing]
    speed = finite_number(network['speed_target_kmh'], 'Tốc độ (km/h)')
    cycle = finite_number(signal['cycle_s'], 'Chu kỳ (s)')
    durations = [finite_number(signal[k], k) for k in PHASE_KEYS]
    require(math.isclose(sum(durations), cycle, abs_tol=1e-9), 'Tổng pha khác chu kỳ')
    step = finite_number(network['simulation_step_s'], 'Bước mô phỏng (s)')
    # Kiểm chứng từng giây và mốc chuyển pha chính xác trong phạm vi bản mẫu.
    require(step == 1, 'Giai đoạn 3 xác minh lịch trên bước 1 giây')
    offsets = corridor_offsets(spacing, speed, cycle)
    for value in durations + offsets + [cycle]:
        require(math.isclose(value, round(value), abs_tol=1e-8),
                'Mốc pha/offset phải nằm trên lưới 1 giây; không âm thầm làm tròn')
    baseline = signal['baseline_offsets_s']
    require(baseline == [0, 0, 0, 0], 'Đối chứng giai đoạn 3 dùng bốn offset bằng 0')
    return {
        'junctions': list('ABCD'), 'spacing_m': spacing, 'speed_kmh': speed,
        'segment_travel_s': [travel_time_seconds(v, speed) for v in spacing],
        'cycle_s': cycle, 'durations_s': durations, 'step_s': step,
        'offsets_s': {'baseline': [0.0] * 4, 'greenwave': offsets},
    }


def topology(root, params):
    """Đối chiếu cấu hình với mạng thật và ánh xạ linkIndex từng nút."""
    net = ET.parse(root / 'simulation/network/generated/corridor.net.xml').getroot()
    nodes = {n.get('id'): n for n in net.findall('junction')}
    require({n.get('id') for n in net.findall('junction')
             if n.get('type') == 'traffic_light'} == set('ABCD'), 'Mạng phải có đúng 4 nút đèn')
    require(all(math.isclose(float(nodes[j].get('y')), float(nodes['A'].get('y')),
                            abs_tol=1e-6) for j in 'ABCD'), 'Trục chính phải thẳng')
    for left, right, distance in zip('ABC', 'BCD', params['spacing_m']):
        require(math.isclose(float(nodes[right].get('x')) - float(nodes[left].get('x')),
                             distance, abs_tol=0.02), 'Khoảng cách cấu hình không khớp mạng')
    links = {}
    corridor = ['W', 'A', 'B', 'C', 'D', 'E']
    for i, j in enumerate('ABCD'):
        controlled = [c for c in net.findall('connection') if c.get('tl') == j]
        require(sorted(int(c.get('linkIndex')) for c in controlled) == [0, 1, 2, 3],
                'Cần bốn linkIndex độc lập mỗi nút')
        pairs = {(c.get('from'), c.get('to')) for c in controlled}
        expected = {(f'{corridor[i]}_{j}', f'{j}_{corridor[i+2]}'),
                    (f'{corridor[i+2]}_{j}', f'{j}_{corridor[i]}'),
                    (f'{j}N_{j}', f'{j}_{j}S'), (f'{j}S_{j}', f'{j}_{j}N')}
        require(pairs == expected, 'Các kết nối phải đúng đường trục/nhánh, chỉ đi thẳng')
        links[j] = controlled
    return net, links


def signal_tree(params, links, plan):
    additional = ET.Element('additional')
    for j, offset in zip(params['junctions'], params['offsets_s'][plan]):
        logic = ET.SubElement(additional, 'tlLogic', id=j, type='static',
                              programID=plan, offset=f'{offset:g}')
        for phase, duration in enumerate(params['durations_s']):
            state = ['r'] * 4
            for link in links[j]:
                incoming = link.get('from').split('_')[0]
                colors = CROSS if incoming in [j+'N', j+'S'] else MAIN
                state[int(link.get('linkIndex'))] = colors[phase]
            ET.SubElement(logic, 'phase', duration=f'{duration:g}', state=''.join(state))
    return additional


def build_plans(root):
    """Chỉ tạo file mới của giai đoạn 3; không tái sinh mạng/xe/GUI GĐ2."""
    root = Path(root).resolve()
    params = parameters(root)
    _, links = topology(root, params)
    template = ET.parse(root / 'simulation/scenarios/sample.sumocfg').getroot()
    for plan in PLANS:
        write_xml(root / f'simulation/signals/{plan}.add.xml', signal_tree(params, links, plan))
        config = copy.deepcopy(template)
        # write_xml giai đoạn 2 tự gắn schema: bỏ thuộc tính QName đã parse.
        config.attrib.pop('{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation', None)
        config.find('input/additional-files').set('value', f'../signals/{plan}.add.xml')
        write_xml(root / f'simulation/scenarios/{plan}.sumocfg', config)
    return params


def phase_at(time_s, offset_s, durations):
    """Lịch lý thuyết: tuổi chương trình (t-O) mod C, không phải (t+O)."""
    age = (time_s - offset_s) % sum(durations)
    boundary = 0
    for index, duration in enumerate(durations):
        boundary += duration
        if age < boundary:
            return index
    raise ValueError('Không xác định được pha')
