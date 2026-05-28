"""Run the local mock collector and compliance scanner."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "collector"))
sys.path.insert(0, str(ROOT / "packages" / "compliance"))

from oci_sentinelmesh_collector import collect_mock_telemetry  # noqa: E402
from oci_sentinelmesh_compliance import scan_telemetry  # noqa: E402


def main() -> None:
    telemetry = collect_mock_telemetry()
    alerts = scan_telemetry(telemetry)
    print(json.dumps([alert.to_dict() for alert in alerts], indent=2))


if __name__ == "__main__":
    main()
