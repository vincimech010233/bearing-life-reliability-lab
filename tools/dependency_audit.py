"""Query OSV for locked dependency versions; fail closed on incomplete evidence."""

import argparse
import datetime
import json
from pathlib import Path
import sys
import tomllib
import urllib.request


def dependencies(root):
    packages, licenses = [], []
    if (root / "Cargo.lock").exists():
        for item in tomllib.loads((root / "Cargo.lock").read_text())["package"]:
            if item.get("source", "").startswith("registry"):
                packages.append(
                    {
                        "package": {"name": item["name"], "ecosystem": "crates.io"},
                        "version": item["version"],
                    }
                )
    if (root / "package-lock.json").exists():
        for name, item in json.loads((root / "package-lock.json").read_text())[
            "packages"
        ].items():
            if name:
                packages.append(
                    {
                        "package": {
                            "name": name.split("node_modules/")[-1],
                            "ecosystem": "npm",
                        },
                        "version": item["version"],
                    }
                )
                licenses.append(
                    {"package": name, "license": item.get("license", "NOT_VERIFIED")}
                )
    for filename in ["requirements.lock", "requirements-dev.txt"]:
        if (root / filename).exists():
            for raw in (root / filename).read_text().splitlines():
                line = raw.strip()
                if "==" in line and not line.startswith("#"):
                    name, version = line.split("==")
                    packages.append(
                        {
                            "package": {"name": name, "ecosystem": "PyPI"},
                            "version": version,
                        }
                    )
    return packages, licenses


def audit(root):
    packages, licenses = dependencies(root)
    result = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "scope": "Registry versions in local locks; OSV database only. No application security or vulnerability-free claim.",
        "queries": packages,
        "licenses": licenses,
    }
    try:
        if not packages:
            raise ValueError("no locked dependencies found")
        request = urllib.request.Request(
            "https://api.osv.dev/v1/querybatch",
            data=json.dumps({"queries": packages}).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            result["response"] = json.load(response)
        if not isinstance(result["response"], dict) or "error" in result["response"]:
            raise ValueError("OSV returned an invalid or error response")
        entries = result["response"].get("results")
        if not isinstance(entries, list) or len(entries) != len(packages):
            raise ValueError("OSV response does not cover every locked dependency")
        if any(
            not isinstance(entry, dict)
            or "error" in entry
            or not isinstance(entry.get("vulns", []), list)
            for entry in entries
        ):
            raise ValueError("invalid OSV result entries")
        result["advisory_count"] = sum(len(entry.get("vulns", [])) for entry in entries)
        result["classification"] = "OBSERVED"
        return result, 1 if result["advisory_count"] else 0
    except (OSError, ValueError, TypeError, AttributeError) as error:
        result.update(classification="NOT_VERIFIED", error=str(error))
        return result, 2


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path("."))
    parser.add_argument(
        "--output",
        type=Path,
        help="Save evidence here instead of replacing the historical audit",
    )
    args = parser.parse_args(argv)
    result, status = audit(args.root)
    output = args.output or args.root / "results/dependency-audit.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(
        result["classification"],
        len(result["queries"]),
        "queries",
        result.get("advisory_count", "unknown"),
        "advisories",
    )
    return status


if __name__ == "__main__":
    sys.exit(main())
