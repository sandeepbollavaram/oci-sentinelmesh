from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "collector"))
sys.path.insert(0, str(ROOT / "packages" / "compliance"))

from oci_sentinelmesh_collector import collect_mock_telemetry
from oci_sentinelmesh_compliance import Severity, scan_telemetry


class ComplianceScannerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.telemetry = collect_mock_telemetry()
        self.alerts = scan_telemetry(self.telemetry)

    def test_public_bucket_creates_high_alert(self) -> None:
        alert = self._alert_for("ocid1.bucket.oc1.iad.mockpublicbucket")

        self.assertEqual(alert.severity, Severity.HIGH)
        self.assertEqual(alert.title, "Public object storage bucket")

    def test_high_cpu_creates_medium_alert(self) -> None:
        alert = self._alert_for("ocid1.instance.oc1.iad.mockhighcpu")

        self.assertEqual(alert.severity, Severity.MEDIUM)
        self.assertEqual(alert.title, "Compute CPU above 80%")

    def test_public_ssh_creates_critical_alert(self) -> None:
        alert = self._alert_for("ocid1.securityrule.oc1.iad.mockpublicssh")

        self.assertEqual(alert.severity, Severity.CRITICAL)
        self.assertEqual(alert.title, "SSH exposed to the public internet")

    def test_broad_iam_admin_creates_high_alert(self) -> None:
        alert = self._alert_for("ocid1.audit.oc1.iad.mockriskyadminpolicy")

        self.assertEqual(alert.severity, Severity.HIGH)
        self.assertEqual(alert.title, "Broad IAM admin permission")

    def _alert_for(self, resource_id: str):
        for alert in self.alerts:
            if alert.resource_id == resource_id:
                return alert
        self.fail(f"No alert found for resource_id={resource_id}")


if __name__ == "__main__":
    unittest.main()
