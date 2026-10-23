"""Kiểm thử mô hình bàn giao và kiểm thử SUMO khi có phần mềm."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from greenwave.simulation.model import binary, generate_sources
from greenwave.simulation.validation import validate, smoke_test
ROOT=Path(__file__).resolve().parents[1]

class ModelTests(unittest.TestCase):
    def test_structure_routes_and_signal_conflicts(self):
        self.assertEqual(validate(ROOT)["controlled_connections"],16)

    def test_invalid_cycle_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            (root/"config").mkdir()
            for name in ["network.json","signals.json"]:
                (root/"config"/name).write_text((ROOT/"config"/name).read_text(encoding="utf-8"),encoding="utf-8")
            path=root/"config/signals.json"
            config=json.loads(path.read_text(encoding="utf-8"))
            config["cycle_s"]=119
            path.write_text(json.dumps(config),encoding="utf-8")
            with self.assertRaises(ValueError):
                generate_sources(root)

    def test_sumo_integration(self):
        try:
            binary("sumo")
        except FileNotFoundError:
            self.skipTest("SUMO chưa cài: chưa kiểm thử tích hợp")
        self.assertEqual(smoke_test(ROOT)["arrived"],85)
