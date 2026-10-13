import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from duty_cycle import calculate  # noqa: E402

class DutyCycleTests(unittest.TestCase):
    def test_one_case(self):
        config = {'synthetic': True, 'bearing_type': 'ball', 'dynamic_rating': 10, 'force_unit': 'kN', 'segments': [{'radial_load': 2, 'speed_rpm': 1500, 'duration_hours': 1}]}
        r = calculate(config)
        self.assertAlmostEqual(r['basic_L10_million_revolutions'], 125)
