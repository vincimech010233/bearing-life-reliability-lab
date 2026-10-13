import copy
from decimal import Decimal, localcontext
import json
import math
from pathlib import Path
import random
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from duty_cycle import calculate  # noqa: E402


def fixture():
    return json.loads((ROOT / "examples/duty_cycle.json").read_text())


class DutyCycleReferenceTests(unittest.TestCase):
    def test_independent_decimal_damage_reference(self):
        rng = random.Random(1749)
        for kind in ["ball", "roller"]:
            for _ in range(20):
                config = fixture()
                config["bearing_type"] = kind
                config["dynamic_rating"] = rng.uniform(1, 100)
                config["segments"] = [
                    {
                        "radial_load": rng.uniform(0.01, 30),
                        "speed_rpm": rng.uniform(0.01, 100000),
                        "duration_hours": rng.uniform(0.001, 100),
                    }
                    for _ in range(rng.randint(1, 100))
                ]
                with localcontext() as context:
                    context.prec = 60
                    p = Decimal(3) if kind == "ball" else Decimal(10) / Decimal(3)
                    rating = Decimal(str(config["dynamic_rating"]))
                    hours, revolutions, damage = Decimal(0), Decimal(0), Decimal(0)
                    for segment in config["segments"]:
                        duration = Decimal(str(segment["duration_hours"]))
                        rev = (
                            Decimal(60) * Decimal(str(segment["speed_rpm"])) * duration
                        )
                        hours += duration
                        revolutions += rev
                        damage += (
                            rev
                            / Decimal(1000000)
                            * (Decimal(str(segment["radial_load"])) / rating) ** p
                        )
                    expected_hours = float(hours / damage)
                    expected_rev = float(revolutions / damage / Decimal(1000000))
                report = calculate(config)
                self.assertTrue(
                    math.isclose(
                        report["basic_L10_hours"], expected_hours, rel_tol=2e-14
                    )
                )
                self.assertTrue(
                    math.isclose(
                        report["basic_L10_million_revolutions"],
                        expected_rev,
                        rel_tol=2e-14,
                    )
                )
                self.assertAlmostEqual(
                    sum(
                        s["fraction_of_modeled_fatigue_damage"]
                        for s in report["normalized"]["segments"]
                    ),
                    1,
                )

    def test_units_and_rating_load_scaling(self):
        config = fixture()
        baseline = calculate(config)
        config["force_unit"] = "N"
        config["dynamic_rating"] *= 1000
        for segment in config["segments"]:
            segment["radial_load"] *= 1000
        self.assertEqual(
            calculate(config)["basic_L10_hours"], baseline["basic_L10_hours"]
        )
        for kind, p in [("ball", 3), ("roller", 10 / 3)]:
            config["bearing_type"] = kind
            base = calculate(config)["basic_L10_hours"]
            doubled = copy.deepcopy(config)
            doubled["dynamic_rating"] *= 2
            self.assertAlmostEqual(calculate(doubled)["basic_L10_hours"] / base, 2**p)

    def test_order_split_duration_and_speed_invariants(self):
        config = fixture()
        base = calculate(config)
        config["segments"].reverse()
        self.assertEqual(calculate(config)["basic_L10_hours"], base["basic_L10_hours"])
        config = fixture()
        segment = config["segments"].pop()
        segment["duration_hours"] /= 2
        config["segments"].extend([dict(segment), dict(segment)])
        self.assertEqual(calculate(config)["basic_L10_hours"], base["basic_L10_hours"])
        for segment in config["segments"]:
            segment["duration_hours"] *= 10
        scaled = calculate(config)
        self.assertAlmostEqual(scaled["basic_L10_hours"], base["basic_L10_hours"])
        self.assertAlmostEqual(
            scaled["modeled_duty_cycle_fatigue_fraction"],
            10 * base["modeled_duty_cycle_fatigue_fraction"],
        )
        for segment in config["segments"]:
            segment["speed_rpm"] *= 2
        self.assertAlmostEqual(
            calculate(config)["basic_L10_hours"], base["basic_L10_hours"] / 2
        )

    def test_extreme_supported_single_segments_match_closed_form(self):
        for kind, p in [("ball", 3), ("roller", 10 / 3)]:
            for rating in [1e-3, 1e9]:
                for load in [1e-3, 1e9]:
                    for speed in [0.01, 100000]:
                        for hours in [1e-6, 1e6]:
                            config = fixture()
                            config.update(
                                bearing_type=kind,
                                force_unit="N",
                                dynamic_rating=rating,
                                segments=[
                                    {
                                        "radial_load": load,
                                        "speed_rpm": speed,
                                        "duration_hours": hours,
                                    }
                                ],
                            )
                            report = calculate(config)
                            expected = 1e6 * (rating / load) ** p / (60 * speed)
                            self.assertTrue(
                                math.isclose(
                                    report["basic_L10_hours"], expected, rel_tol=2e-14
                                )
                            )
                            self.assertTrue(
                                math.isclose(
                                    report["equivalent_radial_load_N"],
                                    load,
                                    rel_tol=2e-14,
                                )
                            )

    def test_invalid_segment_numbers_and_schema(self):
        for key in ["radial_load", "speed_rpm", "duration_hours"]:
            for value in [True, None, "2", 0, -1, float("nan"), float("inf"), 10**1000]:
                config = fixture()
                config["segments"][0][key] = value
                with (
                    self.subTest(key=key, type=type(value).__name__),
                    self.assertRaises(ValueError),
                ):
                    calculate(config)
        for key, value in [
            ("bearing_type", []),
            ("force_unit", {}),
            ("dynamic_rating", 10**1000),
            ("segments", [dict(fixture()["segments"][0], axial_load=0)]),
        ]:
            config = fixture()
            config[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                calculate(config)
