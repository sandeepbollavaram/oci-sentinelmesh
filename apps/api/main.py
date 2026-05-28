"""FastAPI app exposing local mock telemetry and compliance scans."""

from __future__ import annotations

from pathlib import Path
from typing import Any
import sys

from fastapi import FastAPI

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "packages" / "collector"))
sys.path.insert(0, str(ROOT / "packages" / "compliance"))

from oci_sentinelmesh_collector import collect_mock_telemetry  # noqa: E402
from oci_sentinelmesh_compliance import scan_telemetry  # noqa: E402

app = FastAPI(
    title="OCI-SentinelMesh API",
    description="Local mock-first API for OCI telemetry and compliance alerts.",
    version="0.3.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    """Return service health for local development."""

    return {
        "status": "ok",
        "service": "oci-sentinelmesh-api",
        "mode": "mock",
    }


@app.get("/telemetry")
def telemetry() -> list[dict[str, Any]]:
    """Return all local mock telemetry items."""

    return [item.to_dict() for item in collect_mock_telemetry()]


@app.get("/alerts")
def alerts() -> list[dict[str, str]]:
    """Return alerts from scanning local mock telemetry."""

    items = collect_mock_telemetry()
    return [alert.to_dict() for alert in scan_telemetry(items)]


@app.post("/scan")
def scan() -> dict[str, Any]:
    """Run a full local mock telemetry collection and compliance scan."""

    items = collect_mock_telemetry()
    scan_alerts = scan_telemetry(items)
    return {
        "mode": "mock",
        "telemetry_count": len(items),
        "alert_count": len(scan_alerts),
        "alerts": [alert.to_dict() for alert in scan_alerts],
    }
