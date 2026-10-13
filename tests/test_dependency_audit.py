import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from dependency_audit import audit, main


class DependencyAuditTests(unittest.TestCase):
    def run_audit(self, response):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "requirements.lock").write_text("numpy==2.5.4\n")
            with patch(
                "dependency_audit.urllib.request.urlopen",
                return_value=io.BytesIO(json.dumps(response).encode()),
            ):
                return audit(root)

    def test_complete_clean_response(self):
        result, status = self.run_audit({"results": [{}]})
        self.assertEqual(status, 0)
        self.assertEqual(result["classification"], "OBSERVED")
        self.assertEqual(result["advisory_count"], 0)

    def test_advisory_is_failure(self):
        result, status = self.run_audit(
            {"results": [{"vulns": [{"id": "synthetic-advisory"}]}]}
        )
        self.assertEqual(status, 1)
        self.assertEqual(result["advisory_count"], 1)

    def test_incomplete_or_invalid_response_is_not_verified(self):
        for response in [
            {},
            {"results": []},
            {"results": [None]},
            {"results": [{"vulns": {}}]},
            {"results": [{"error": "synthetic server failure"}]},
            {"results": [{}], "error": "synthetic server failure"},
            {"results": [{"vulns": [], "error": {"code": 500}}]},
            None,
        ]:
            with self.subTest(response=response):
                result, status = self.run_audit(response)
                self.assertEqual(status, 2)
                self.assertEqual(result["classification"], "NOT_VERIFIED")

    def test_network_failure_and_empty_scope_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertEqual(audit(root)[1], 2)
            (root / "requirements.lock").write_text("numpy==2.5.4\n")
            with patch(
                "dependency_audit.urllib.request.urlopen",
                side_effect=OSError("synthetic offline fixture"),
            ):
                result, status = audit(root)
            self.assertEqual(status, 2)
            self.assertIn("synthetic offline", result["error"])

    def test_new_output_preserves_historical_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "requirements.lock").write_text("numpy==2.5.4\n")
            historical = root / "results/dependency-audit.json"
            historical.parent.mkdir()
            historical.write_text("retained")
            output = root / "new/audit.json"
            with patch(
                "dependency_audit.urllib.request.urlopen",
                return_value=io.BytesIO(b'{"results":[{}]}'),
            ):
                self.assertEqual(main([str(root), "--output", str(output)]), 0)
            self.assertEqual(historical.read_text(), "retained")
            self.assertEqual(json.loads(output.read_text())["advisory_count"], 0)
