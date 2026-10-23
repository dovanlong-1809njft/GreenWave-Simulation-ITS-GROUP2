import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from greenwave.algorithms.offset import corridor_offsets, travel_time_seconds


class OffsetTests(unittest.TestCase):
    def test_travel_time(self):
        self.assertAlmostEqual(travel_time_seconds(300, 36), 30)

    def test_four_junction_offsets(self):
        self.assertEqual(corridor_offsets([300, 300, 300], 36, 120), [0, 30, 60, 90])

    def test_offset_modulo_cycle(self):
        self.assertEqual(corridor_offsets([1500], 36, 120), [0, 30])

    def test_invalid_speed(self):
        with self.assertRaises(ValueError):
            travel_time_seconds(100, 0)


if __name__ == "__main__":
    unittest.main()
