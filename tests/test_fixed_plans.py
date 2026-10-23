"""Công thức, lịch kỳ vọng và lỗi tích hợp có thể xảy ra khi đổi tham số."""
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from greenwave.algorithms.offset import corridor_offsets
from greenwave.controllers.fixed_plans import build_plans, parameters, phase_at
from greenwave.simulation.model import binary
from greenwave.simulation.plan_validation import validate_plans, verify

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    'config/network.json', 'config/signals.json',
    'simulation/network/generated/corridor.net.xml',
    'simulation/routes/source/sample.rou.xml',
    'simulation/signals/fixed.add.xml', 'simulation/scenarios/sample.sumocfg',
    'simulation/signals/baseline.add.xml', 'simulation/signals/greenwave.add.xml',
    'simulation/scenarios/baseline.sumocfg', 'simulation/scenarios/greenwave.sumocfg',
]


def copy_fixture(path):
    for name in FILES:
        target = path/name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT/name, target)


class PlanTests(unittest.TestCase):
    def test_offsets_hand_calculation_and_units(self):
        self.assertEqual(corridor_offsets([300,300,300], 36, 120), [0,30,60,90])
        self.assertEqual(corridor_offsets([100,200,400], 36, 120), [0,10,30,70])
        self.assertEqual(corridor_offsets([1500,300,300],36,120), [0,30,60,90])

    def test_phase_boundaries_independent_table(self):
        durations = [45,3,2,65,3,2]
        expected = {0:0,44:0,45:1,47:1,48:2,49:2,50:3,114:3,115:4,117:4,118:5,119:5,120:0}
        for t, phase in expected.items():
            self.assertEqual(phase_at(t,0,durations), phase)
        d_expected = {0:0,14:0,15:1,18:2,20:3,85:4,88:5,90:0,135:1,210:0}
        for t, phase in d_expected.items():
            self.assertEqual(phase_at(t,90,durations),phase)

    def test_static_xml_and_four_offsets(self):
        params=validate_plans(ROOT)
        self.assertEqual(params['offsets_s']['baseline'], [0]*4)
        self.assertEqual(params['offsets_s']['greenwave'], [0,30,60,90])

    def test_invalid_inputs_and_non_grid_offset_rejected(self):
        for key, value in [('speed_target_kmh',0),('speed_target_kmh',float('nan')),
                           ('speed_target_kmh',float('inf')),('speed_target_kmh',True),
                           ('speed_target_kmh',37),('intersections_spacing_m',[0,300,300])]:
            with self.subTest(key=key,value=value), tempfile.TemporaryDirectory() as d:
                root=Path(d);copy_fixture(root)
                p=root/'config/network.json';config=json.loads(p.read_text(encoding='utf-8'))
                config[key]=value;p.write_text(json.dumps(config),encoding='utf-8')
                with self.assertRaises(ValueError):parameters(root)

    def test_build_preserves_stage2_and_is_deterministic(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);copy_fixture(root)
            protected=FILES[:6]
            before={p:(root/p).read_bytes() for p in protected}
            build_plans(root)
            generated={p:(root/p).read_bytes() for p in FILES[6:]}
            build_plans(root)
            self.assertEqual(before,{p:(root/p).read_bytes() for p in protected})
            self.assertEqual(generated,{p:(root/p).read_bytes() for p in FILES[6:]})

    def test_stale_network_geometry_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);copy_fixture(root)
            p=root/'config/network.json';config=json.loads(p.read_text(encoding='utf-8'))
            config['intersections_spacing_m']=[310,300,300]
            p.write_text(json.dumps(config),encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'Khoảng cách'):validate_plans(root)

    def test_incorrect_offset_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);copy_fixture(root)
            p=root/'simulation/signals/greenwave.add.xml';tree=ET.parse(p)
            tree.getroot().findall('tlLogic')[1].set('offset','90')
            tree.write(p)
            with self.assertRaises(ValueError):validate_plans(root)

    def test_conflicting_green_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);copy_fixture(root)
            p=root/'simulation/signals/baseline.add.xml';tree=ET.parse(p)
            tree.getroot().find('tlLogic/phase').set('state','GGGG')
            tree.write(p)
            with self.assertRaises(ValueError):validate_plans(root)

    def test_unequal_inputs_are_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);copy_fixture(root)
            p=root/'simulation/scenarios/greenwave.sumocfg';tree=ET.parse(p)
            tree.getroot().find('random_number/seed').set('value','12');tree.write(p)
            with self.assertRaises(ValueError):validate_plans(root)

    def test_two_plans_in_sumo_and_reproducibility(self):
        try:binary('sumo')
        except FileNotFoundError:self.skipTest('SUMO chưa có: chưa kiểm chứng tích hợp')
        report=verify(ROOT)
        self.assertEqual(report['runs_completed'],4)
        self.assertTrue(report['different_signal_schedules'])
        for plan in ('baseline','greenwave'):
            self.assertEqual(report['plans'][plan]['arrived'],85)
            self.assertTrue(report['plans'][plan]['repeat_identical'])
        starts=report['plans']['greenwave']['green_starts_s']
        self.assertEqual([starts[j][0] for j in 'ABCD'],[0,30,60,90])
        self.assertEqual(starts['D'][1],210)

if __name__ == '__main__':unittest.main()
