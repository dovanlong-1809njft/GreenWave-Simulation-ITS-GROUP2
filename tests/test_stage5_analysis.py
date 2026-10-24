"""Fixture tính tay và tích hợp dữ liệu đã niêm phong, không cần phát lại 18 mô phỏng."""
import csv,importlib.util,json,os,sys,tempfile,unittest,zipfile
from pathlib import Path
import xml.etree.ElementTree as ET
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from greenwave.analysis.experimental import average,reduction,parse_vehicles,summarize,paired,analyze
R=Path(__file__).resolve().parents[1]

def fixture():
 demand=ET.fromstring('''<routes><route id="r" edges="W_A A_B B_C C_D D_E"/><route id="x" edges="AN_A A_AS"/><vehicle id="v1" route="r" depart="300"/><vehicle id="v2" route="r" depart="310"/><vehicle id="east.fake" route="x" depart="300"/></routes>''')
 trips=ET.fromstring('''<tripinfos><tripinfo id="v1" depart="301" arrival="321" duration="20" waitingTime="3" timeLoss="7" waitingCount="1"/><tripinfo id="v2" depart="313" arrival="353" duration="40" waitingTime="9" timeLoss="13" waitingCount="3"/></tripinfos>''')
 return demand,trips

class MetricsTests(unittest.TestCase):
 def test_hand_calculated_metrics_and_filter(self):
  d,t=fixture();rows=parse_vehicles(d,t);s=summarize(rows)
  self.assertEqual(s['n_requested'],2);self.assertEqual(s['travel_time_s_mean'],30)
  self.assertEqual(s['waiting_time_s_mean'],6);self.assertEqual(s['time_loss_s_mean'],10)
  self.assertEqual(s['stops_mean'],2);self.assertEqual(s['depart_delay_s_mean'],2)
  self.assertEqual(rows[2]['group'],'cross')
 def test_reduction_zero_negative_and_empty(self):
  self.assertEqual(reduction(100,80),20);self.assertEqual(reduction(100,120),-20)
  self.assertIsNone(reduction(0,0));self.assertIsNone(average([]))
 def test_missing_unfinished_not_zero(self):
  d,t=fixture();t.remove(t[1]);rows=parse_vehicles(d,t);s=summarize(rows)
  self.assertEqual(s['n_pending'],1);self.assertFalse(s['complete_cohort'])
  self.assertIsNone(rows[1]['travel_time_s'])
 def test_duration_mismatch_rejected(self):
  d,t=fixture();t[0].set('duration','21')
  with self.assertRaises(ValueError):parse_vehicles(d,t)
 def test_duplicate_trip_rejected(self):
  d,t=fixture();t.append(ET.fromstring(ET.tostring(t[0])))
  with self.assertRaises(ValueError):parse_vehicles(d,t)
 def test_paired_hand_50_percent(self):
  d,t=fixture();a=[r for r in parse_vehicles(d,t) if r['group']=='priority']
  b=[dict(r,travel_time_s=r['travel_time_s']/2) for r in a]
  self.assertEqual(paired(a,b)['travel_time_s_reduction_pct'],50)
 def test_incomplete_pair_has_no_primary_reduction(self):
  d,t=fixture();a=[r for r in parse_vehicles(d,t) if r['group']=='priority'];b=[dict(r) for r in a];b[0]['status']='running'
  p=paired(a,b);self.assertFalse(p['complete_pair']);self.assertEqual(p['n_common_arrived'],1)
  self.assertIsNone(p['travel_time_s_reduction_pct'])
 def test_different_requested_set_rejected(self):
  d,t=fixture();a=[r for r in parse_vehicles(d,t) if r['group']=='priority']
  with self.assertRaises(ValueError):paired(a,a[:1])
 def test_missing_batch_clear_failure(self):
  with tempfile.TemporaryDirectory() as tmp:
   with self.assertRaises(FileNotFoundError):analyze(Path(tmp)/'missing',Path(tmp)/'out')
 def test_real_sealed_data_csv_and_no_overwrite(self):
  with tempfile.TemporaryDirectory(prefix='stage5 analysis ') as tmp:
   tmp=Path(tmp)
   with zipfile.ZipFile(R/'docs/stage4-evidence/raw-runs.zip') as z:z.extractall(tmp/'source')
   result=analyze(tmp/'source/sealed_primary',tmp/'out')
   with (result/'scenario_summary.csv').open() as f:rows=list(csv.DictReader(f))
   self.assertEqual(len(rows),18);self.assertTrue(all(r['n_arrived']==r['n_requested'] for r in rows))
   with (result/'paired_comparison.csv').open() as f:self.assertEqual(len(list(csv.DictReader(f))),9)
   with self.assertRaises(ValueError):analyze(tmp/'source/sealed_primary',tmp/'out')
 def test_plot_real_output(self):
  if importlib.util.find_spec('matplotlib') is None:self.skipTest('Matplotlib chưa cài: chưa kiểm thử vẽ hình')
  from greenwave.visualization.experiment_plots import plot
  with tempfile.TemporaryDirectory() as tmp:
   tmp=Path(tmp)
   with zipfile.ZipFile(R/'docs/stage4-evidence/raw-runs.zip') as z:z.extractall(tmp/'source')
   analyze(tmp/'source/sealed_primary',tmp/'tables');plot(tmp/'tables',tmp/'figures')
   self.assertEqual(len(list((tmp/'figures').glob('*.png'))),6)
