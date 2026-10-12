import json
import math
import sys
import unittest
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from bearing import analyze, life, validate


class BearingTests(unittest.TestCase):
    def fixture(self):
        return json.loads(Path("examples/bearing.json").read_text())

    def test_numerical_limits(self):
        for rating in [1e-300, 1e-110]:
            c = self.fixture()
            c["dynamic_rating"] = rating
            with self.assertRaises(ValueError):
                analyze(c)
        with self.assertRaises(ValueError):
            life(1e-300, 2000.0, 1500.0, 3.0)

    def test_reference(self):
        r, _ = analyze(self.fixture())
        self.assertAlmostEqual(r["basic_L10_revolutions"], 125e6)
        self.assertAlmostEqual(r["basic_L10_hours"], 125e6 / 90000)

    def test_dimension_invariance(self):
        c = self.fixture()
        r, _ = analyze(c)
        c.update(force_unit="N", dynamic_rating=10000.0, radial_load=2000.0)
        s, _ = analyze(c)
        self.assertEqual(r["basic_L10_hours"], s["basic_L10_hours"])

    def test_scaling(self):
        for p in [3.0, 10 / 3]:
            base = life(10000, 2000, 1500, p)[1]
            self.assertAlmostEqual(life(20000, 2000, 1500, p)[1] / base, 2**p)
            self.assertAlmostEqual(life(10000, 4000, 1500, p)[1] / base, 2 ** (-p))
            self.assertAlmostEqual(life(10000, 2000, 3000, p)[1] / base, 0.5)

    def test_sensitivity_derivatives(self):
        C, P, n, p, _ = validate(self.fixture())
        h = 1e-5
        base = life(C, P, n, p)[1]
        for i, expected in enumerate([p, -p, -1]):
            args = [C, P, n]
            args[i] *= math.exp(h)
            d = math.log(life(*args, p)[1] / base) / h
            self.assertAlmostEqual(d, expected, places=7)

    def test_rejection(self):
        for key, v in [
            ("speed", 0),
            ("speed", float("nan")),
            ("dynamic_rating", -1),
            ("axial_load", 1),
            ("force_unit", "lbf"),
            ("speed_unit", "Hz"),
            ("samples", 100000),
            ("speed", True),
        ]:
            c = self.fixture()
            c[key] = v
            with self.assertRaises(ValueError):
                analyze(c)

    def test_roller_reference(self):
        c = self.fixture()
        c["bearing_type"] = "roller"
        r, _ = analyze(c)
        self.assertAlmostEqual(r["basic_L10_hours"], 1e6 / 90000 * 5 ** (10 / 3))

    def test_seeded_and_exact_uncertainty(self):
        r, a = analyze(self.fixture())
        s, b = analyze(self.fixture())
        self.assertTrue(np.array_equal(a, b))
        self.assertTrue(
            np.max(np.abs(r["uncertainty"]["monte_carlo_relative_quantile_error"]))
            < 0.05
        )

    def test_zero_uncertainty(self):
        c = self.fixture()
        c["cv"] = {"rating": 0.0, "load": 0.0, "speed": 0.0}
        r, a = analyze(c)
        self.assertAlmostEqual(float(np.std(a)), 0.0, places=10)
        self.assertAlmostEqual(
            r["uncertainty"]["analytic_lognormal_quantiles_hours"][0],
            r["basic_L10_hours"],
        )

    def test_units_ratio_and_unknown_fields(self):
        c = self.fixture()
        c["extra"] = "unsupported"
        with self.assertRaises(ValueError):
            analyze(c)


if __name__ == "__main__":
    unittest.main()
