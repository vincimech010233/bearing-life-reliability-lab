import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from duty_cycle import calculate  # noqa: E402


class DutyCycleValidationTests(unittest.TestCase):
    def test_rejects_bad_inputs(self):
        base = {
            "synthetic": True,
            "bearing_type": "ball",
            "dynamic_rating": 10,
            "force_unit": "kN",
            "segments": [{"radial_load": 2, "speed_rpm": 1000, "duration_hours": 1}],
        }
        for key, value in [
            ("synthetic", False),
            ("dynamic_rating", True),
            ("dynamic_rating", float("nan")),
            ("force_unit", "lbf"),
            ("segments", []),
            ("segments", [{}] * 101),
        ]:
            config = dict(base)
            config[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                calculate(config)
