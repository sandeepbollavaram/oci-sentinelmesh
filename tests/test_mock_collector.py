from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "collector"))

from oci_sentinelmesh_collector import ResourceType, collect_mock_telemetry


class MockCollectorTests(unittest.TestCase):
    def test_collect_mock_telemetry_returns_expected_resources(self) -> None:
        telemetry = collect_mock_telemetry()

        self.assertEqual(len(telemetry), 8)
        self.assertEqual(
            {item.resource_type for item in telemetry},
            {
                ResourceType.COMPUTE_INSTANCE,
                ResourceType.OBJECT_STORAGE_BUCKET,
                ResourceType.IAM_POLICY_CHANGE,
                ResourceType.NETWORK_SECURITY_RULE,
            },
        )
        self.assertIn("normal-compute-instance", {item.name for item in telemetry})
        self.assertIn("high-cpu-compute-instance", {item.name for item in telemetry})
        self.assertIn("private-audit-logs", {item.name for item in telemetry})
        self.assertIn("public-export-bucket", {item.name for item in telemetry})
        self.assertIn("normal-iam-policy-change", {item.name for item in telemetry})
        self.assertIn("risky-iam-policy-change", {item.name for item in telemetry})
        self.assertIn("safe-network-rule", {item.name for item in telemetry})
        self.assertIn("open-public-ssh-rule", {item.name for item in telemetry})


if __name__ == "__main__":
    unittest.main()
