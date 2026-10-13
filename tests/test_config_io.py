import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from config_io import MAX_BYTES, read_config  # noqa: E402


class ConfigIOTests(unittest.TestCase):
    def read_bytes(self, data):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            path.write_bytes(data)
            return read_config(path)

    def test_exact_size_and_utf8(self):
        self.assertEqual(self.read_bytes(b"{}" + b" " * (MAX_BYTES - 2)), {})
        with self.assertRaises(ValueError):
            self.read_bytes(b"{}" + b" " * (MAX_BYTES - 1))
        with self.assertRaises(ValueError):
            self.read_bytes(b"\xff")

    def test_actual_read_is_bounded_without_stat(self):
        stream = io.BytesIO(b"{}" + b" " * MAX_BYTES)
        with (
            patch.object(Path, "open", return_value=stream),
            patch.object(
                Path, "stat", side_effect=AssertionError("stat is not a size gate")
            ),
        ):
            with self.assertRaises(ValueError):
                read_config("stream.json")

    def test_duplicate_fields_at_any_depth(self):
        for data in [
            b'{"synthetic":false,"synthetic":true}',
            b'{"segments":[{"speed_rpm":0,"speed_rpm":1000}]}',
        ]:
            with (
                self.subTest(data=data),
                self.assertRaisesRegex(ValueError, "duplicate JSON field"),
            ):
                self.read_bytes(data)

    def test_deep_json_has_controlled_error(self):
        with self.assertRaisesRegex(ValueError, "nested too deeply"):
            self.read_bytes(b"[" * 16000 + b"0" + b"]" * 16000)

    def test_both_clis_preserve_existing_output_on_invalid_input(self):
        for content in [
            b"\xff",
            b"[" * 16000 + b"0" + b"]" * 16000,
            b'{"synthetic":false,"synthetic":true}',
            b"{}" + b" " * MAX_BYTES,
        ]:
            for script in ["bearing.py", "duty_cycle.py"]:
                with (
                    self.subTest(script=script, size=len(content)),
                    tempfile.TemporaryDirectory() as directory,
                ):
                    root = Path(directory)
                    source = root / "input.json"
                    source.write_bytes(content)
                    output = root / "existing"
                    if script == "bearing.py":
                        output.mkdir()
                        target = output / "report.json"
                    else:
                        target = output
                    target.write_text("retained")
                    result = subprocess.run(
                        [
                            sys.executable,
                            str(ROOT / "src" / script),
                            str(source),
                            str(output),
                        ],
                        capture_output=True,
                        text=True,
                        timeout=20,
                    )
                    self.assertEqual(result.returncode, 2, result.stderr)
                    self.assertNotIn("Traceback", result.stderr)
                    self.assertEqual(target.read_text(), "retained")

    def test_examples_decode_without_alteration(self):
        for name in ["bearing", "duty_cycle"]:
            path = ROOT / "examples" / f"{name}.json"
            self.assertEqual(read_config(path), json.loads(path.read_text()))
