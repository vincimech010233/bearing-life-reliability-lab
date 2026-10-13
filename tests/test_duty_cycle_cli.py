import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from duty_cycle import main  # noqa: E402


class CLIValidationTests(unittest.TestCase):
    def test_report_and_bounded_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            out = root / "report.json"
            self.assertEqual(
                main([str(ROOT / "examples/duty_cycle.json"), str(out)]), 0
            )
            report = json.loads(out.read_text())
            self.assertAlmostEqual(report["basic_L10_hours"], 245.09803921568624)
            invalid = root / "oversized.json"
            invalid.write_text("x" * 65537)
            absent = root / "should-not-exist.json"
            self.assertEqual(main([str(invalid), str(absent)]), 2)
            self.assertFalse(absent.exists())
