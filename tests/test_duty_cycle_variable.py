import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from duty_cycle import calculate  # noqa: E402


def fixture():
    return {
        "synthetic": True,
        "bearing_type": "ball",
        "dynamic_rating": 10,
        "force_unit": "kN",
        "segments": [
            {"radial_load": 2, "speed_rpm": 1000, "duration_hours": 1},
            {"radial_load": 4, "speed_rpm": 2000, "duration_hours": 1},
        ],
    }


class VariableLoadTests(unittest.TestCase):
    def test_speed_weighted_inverse_life(self):
        r = calculate(fixture())
        self.assertAlmostEqual(r["average_speed_rpm"], 1500)
        self.assertAlmostEqual(r["basic_L10_hours"], 1e6 / 90000 * 3000 / 136)
        self.assertAlmostEqual(
            r["basic_L10_million_revolutions"],
            1 / ((1 / 3) / 125 + (2 / 3) / 15.625),
        )

    def test_rare_heavy_load_contribution(self):
        c = fixture()
        c["segments"] = [
            {"radial_load": 2, "speed_rpm": 1000, "duration_hours": 99},
            {"radial_load": 8, "speed_rpm": 1000, "duration_hours": 1},
        ]
        r = calculate(c)
        self.assertGreater(
            r["normalized"]["segments"][1]["fraction_of_modeled_fatigue_damage"], 0.35
        )

    def test_roller_exponent(self):
        c = fixture()
        c["bearing_type"] = "roller"
        r = calculate(c)
        self.assertAlmostEqual(r["normalized"]["basic_life_exponent"], 10 / 3)
