from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVERS_ROOT = ROOT / "servers"
VALIDATOR = ROOT / "scripts" / "validate_mcp.py"


class ManifestTests(unittest.TestCase):
    def test_validator_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, str(VALIDATOR)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)

    def test_at_least_one_server(self) -> None:
        self.assertTrue(sorted(SERVERS_ROOT.glob("*/*/server.json")))

    def test_every_manifest_is_well_formed(self) -> None:
        for manifest in sorted(SERVERS_ROOT.glob("*/*/server.json")):
            with self.subTest(manifest=str(manifest.relative_to(ROOT))):
                data = json.loads(manifest.read_text(encoding="utf-8"))
                self.assertEqual(data["name"], manifest.parent.name)
                self.assertEqual(data["category"], manifest.parent.parent.name)


if __name__ == "__main__":
    unittest.main()
