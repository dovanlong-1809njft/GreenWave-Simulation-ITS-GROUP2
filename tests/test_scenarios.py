"""Bảo toàn nhu cầu, tính công bằng, chống ghi đè và kiểm tra xe chưa hoàn tất."""
import copy
import json
import hashlib
import zipfile
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from greenwave.simulation.scenarios import settings,schedule,build,verify_files,route_path,scenario_path,route_tree,xml_bytes
from greenwave.simulation.experiments import state_counts,run_case,check_seal,digest_bytes
from greenwave.simulation.model import binary
from greenwave.simulation.scenario_audit import audit_batch
ROOT=Path(__file__).resolve().parents[1]
FIXTURES=['config/network.json','config/signals.json','config/stage4-experiments.json',
          'simulation/network/generated/corridor.net.xml','simulation/routes/source/sample.rou.xml',
          'simulation/signals/fixed.add.xml','simulation/signals/baseline.add.xml','simulation/signals/greenwave.add.xml',
          'simulation/scenarios/sample.sumocfg','simulation/scenarios/baseline.sumocfg','simulation/scenarios/greenwave.sumocfg']


def fixture(root):
    for n in FIXTURES:
        p=root/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/n,p)
    build(root,seeds=[11])


class ScenarioTests(unittest.TestCase):
    def test_three_levels_and_both_plans(self):
        report=verify_files(ROOT,seeds=[11])
        self.assertEqual([r['level'] for r in report],['low','medium','high'])
        self.assertEqual([r['priority_measurement'] for r in report],[300,600,900])
        self.assertEqual([r['requested_total'] for r in report],[1297,1622,1947])
        self.assertTrue(all(r['pair_uses_same_route'] for r in report))

    def test_seed_reproducible_and_different(self):
        c=settings(ROOT)
        self.assertEqual(schedule(c,'high',11),schedule(c,'high',11))
        self.assertNotEqual(schedule(c,'high',11),schedule(c,'high',22))

    def test_background_same_across_levels(self):
        c=settings(ROOT)
        self.assertEqual([x for x in schedule(c,'low',11) if not x['priority']],
                         [x for x in schedule(c,'high',11) if not x['priority']])

    def test_unique_ids_order_time_windows(self):
        c=settings(ROOT)
        for level in ['low','medium','high']:
            r=schedule(c,level,11)
            self.assertEqual(len(r),len(set(x['id'] for x in r)))
            self.assertEqual(r,sorted(r,key=lambda x:(x['planned_depart_s'],x['id'])))
            self.assertTrue(all(0<=x['planned_depart_s']<3900 for x in r))
            self.assertTrue(all((x['planned_depart_s']<300)==(x['cohort']=='warmup') for x in r))

    def test_no_source_files_modified_and_idempotent_build(self):
        with tempfile.TemporaryDirectory() as d:
            r=Path(d);fixture(r)
            before={n:(r/n).read_bytes() for n in FIXTURES}
            first=build(r,seeds=[11]);hashes={n:(r/n).read_bytes() for n in first}
            build(r,seeds=[11])
            self.assertEqual(before,{n:(r/n).read_bytes() for n in FIXTURES})
            self.assertEqual(hashes,{n:(r/n).read_bytes() for n in first})

    def test_conflict_refuses_all_writes(self):
        with tempfile.TemporaryDirectory() as d:
            r=Path(d);fixture(r)
            missing=r/scenario_path('low','baseline',11);missing.unlink()
            conflict=r/route_path('high',11);conflict.write_text('user content')
            with self.assertRaises(ValueError):build(r,seeds=[11])
            self.assertFalse(missing.exists());self.assertEqual(conflict.read_text(),'user content')

    def test_duplicate_vehicle_or_bad_route_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            r=Path(d);fixture(r)
            p=r/route_path('low',11);tree=ET.parse(p)
            tree.getroot().append(copy.deepcopy(tree.getroot().find('vehicle')));tree.write(p)
            with self.assertRaises(ValueError):verify_files(r,['low'],[11])

    def test_config_fairness_and_seed_mismatch(self):
        with tempfile.TemporaryDirectory() as d:
            r=Path(d);fixture(r)
            p=r/scenario_path('low','greenwave',11);tree=ET.parse(p)
            tree.getroot().find('random_number/seed').set('value','22');tree.write(p)
            with self.assertRaises(ValueError):verify_files(r,['low'],[11])

    def test_pending_and_cohort_boundaries(self):
        rows=[{'planned_depart_s':299,'actual_depart_s':300,'arrival_s':400},
              {'planned_depart_s':300,'actual_depart_s':None,'arrival_s':None},
              {'planned_depart_s':0,'actual_depart_s':0,'arrival_s':299}]
        self.assertEqual(state_counts(rows,300),{'requested':2,'departed':1,'arrived':1,'pending':1,'running':0})
        self.assertEqual(state_counts(rows,3900),{'requested':3,'departed':2,'arrived':2,'pending':1,'running':0})

    def test_invalid_seed_and_rate_rejected(self):
        c=settings(ROOT)
        with self.assertRaises(ValueError):schedule(c,'low',True)
        with self.assertRaises(ValueError):schedule(c,'invalid',11)

    def test_output_directory_never_overwritten(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'existing';out.mkdir();sentinel=out/'user.txt';sentinel.write_text('keep')
            with self.assertRaises(FileExistsError):run_case(ROOT,'low','baseline',11,out)
            self.assertEqual(sentinel.read_text(),'keep')

    def test_sealed_output_tampering_is_detected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'sealed.zip'
            csv=b'id,value\na,1\n'
            meta={'status':'completed','input_sha256':{},'output_structural_sha256':{'vehicles.csv':hashlib.sha256(csv).hexdigest()}}
            def write(data):
                with zipfile.ZipFile(p,'w') as z:
                    z.writestr('run.json',json.dumps(meta));z.writestr('validation.json','{}');z.writestr('vehicles.csv',data)
            write(csv);check_seal(p)
            write(b'id,value\na,2\n')
            with self.assertRaises(ValueError):check_seal(p)

    def test_incomplete_metadata_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'sealed.zip'
            with zipfile.ZipFile(p,'w') as z:z.writestr('run.json','{"status":"started"}')
            with self.assertRaises(ValueError):check_seal(p)

    def test_xml_hash_excludes_comment_not_traffic_duration(self):
        a=b'<tripinfos><!-- run 1 --><tripinfo id="x" duration="2"/></tripinfos>'
        b=b'<tripinfos><!-- run 2 --><tripinfo duration="2" id="x"/></tripinfos>'
        c=b'<tripinfos><tripinfo id="x" duration="3"/></tripinfos>'
        self.assertEqual(digest_bytes('trips.xml',a),digest_bytes('trips.xml',b))
        self.assertNotEqual(digest_bytes('trips.xml',a),digest_bytes('trips.xml',c))

    def test_real_sumo_low_and_short_drain_high(self):
        try:binary('sumo')
        except FileNotFoundError:self.skipTest('SUMO chưa có, chưa kiểm thử tích hợp GĐ4')
        with tempfile.TemporaryDirectory(prefix='stage4 test ') as d:
            r=Path(d)/'project';fixture(r)
            low=run_case(r,'low','baseline',11,Path(d)/'low output')
            self.assertEqual(low['arrived_end'],1297);self.assertEqual(low['collisions'],0)
            p=r/'config/stage4-experiments.json';c=json.loads(p.read_text());c['drain_s']=1;p.write_text(json.dumps(c))
            # Dùng bộ file sinh riêng cho drain ngắn; không ghi đè cấu hình mẫu cũ.
            for level in ['low','medium','high']:
                for plan in ['baseline','greenwave']:(r/scenario_path(level,plan,11)).unlink()
            build(r,seeds=[11])
            high=run_case(r,'high','baseline',11,Path(d)/'high output')
            self.assertTrue(high['incomplete_end']);self.assertGreater(high['pending_end']+high['running_end'],0)
            self.assertEqual(high['snapshots']['all']['3901']['requested'],1947)
            self.assertEqual(sum(high['snapshots']['all']['3901'][k] for k in ['arrived','pending','running']),1947)
            with (Path(d)/'high output/vehicles.csv').open() as f:
                self.assertIn('not_departed',f.read())

if __name__=='__main__':unittest.main()
