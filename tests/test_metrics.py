import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from greenwave.analysis.metrics import mean, reduction_percent


class MetricsTests(unittest.TestCase):
    def test_mean(self):
        self.assertEqual(mean([10, 20, 30]), 20)

    def test_reduction(self):
        self.assertAlmostEqual(reduction_percent(100, 70), 30)

    def test_increase_is_negative_reduction(self):
        self.assertAlmostEqual(reduction_percent(100, 110), -10)


if __name__ == "__main__":
    unittest.main()
