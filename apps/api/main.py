"""FastAPI app exposing local mock telemetry and compliance scans."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4
import sys

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "packages" / "collector"))
sys.path.insert(0, str(ROOT / "packages" / "compliance"))
sys.path.insert(0, str(ROOT / "packages" / "db"))

from oci_sentinelmesh_collector import collect_mock_telemetry  # noqa: E402
from oci_sentinelmesh_compliance import scan_telemetry  # noqa: E402
from oci_sentinelmesh_db import SQLiteRepository, persistence_enabled  # noqa: E402
from oci_sentinelmesh_db.models import (  # noqa: E402
    AuditEvent,
    PersistedAlert,
    ScanRun,
    TelemetryEvent,
)

app = FastAPI(
    title="OCI-SentinelMesh API",
    description="Local mock-first API for OCI telemetry and compliance alerts.",
    version="0.6.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
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
def alerts() -> list[dict[str, Any]]:
    """Return alerts from scanning local mock telemetry."""

    items = collect_mock_telemetry()
    return [alert.to_dict() for alert in scan_telemetry(items)]


@app.post("/scan")
def scan() -> dict[str, Any]:
    """Run a full local mock telemetry collection and compliance scan."""

    started_at = _utc_now_iso()
    scan_id = str(uuid4())
    items = collect_mock_telemetry()
    scan_alerts = scan_telemetry(items)
    completed_at = _utc_now_iso()
    response = {
        "scan_id": scan_id,
        "mode": "mock",
        "telemetry_count": len(items),
        "alert_count": len(scan_alerts),
        "alerts": [alert.to_dict() for alert in scan_alerts],
    }

    if persistence_enabled():
        repository = SQLiteRepository()
        scan_run = ScanRun(
            scan_id=scan_id,
            mode="mock",
            telemetry_count=len(items),
            alert_count=len(scan_alerts),
            started_at=started_at,
            completed_at=completed_at,
        )
        repository.save_scan(
            scan_run=scan_run,
            telemetry_events=[
                TelemetryEvent(
                    scan_id=scan_id,
                    resource_id=item.resource_id,
                    resource_type=item.resource_type.value,
                    name=item.name,
                    compartment_id=item.compartment_id,
                    region=item.region,
                    timestamp=item.timestamp.isoformat(),
                    metadata=item.metadata,
                )
                for item in items
            ],
            alerts=[
                PersistedAlert(
                    scan_id=scan_id,
                    alert_id=alert.alert_id,
                    rule_id=alert.rule_id.value,
                    category=alert.category.value,
                    resource_id=alert.resource_id,
                    resource_type=alert.resource_type.value,
                    severity=alert.severity.value,
                    title=alert.title,
                    description=alert.description,
                    recommendation=alert.recommendation,
                    timestamp=alert.timestamp.isoformat(),
                )
                for alert in scan_alerts
            ],
            audit_event=AuditEvent.create(
                scan_id=scan_id,
                action="mock_scan",
                status="success",
                message=f"Persisted mock scan with {len(items)} telemetry events and {len(scan_alerts)} alerts.",
                timestamp=completed_at,
            ),
        )

    return response


@app.get("/scan-runs")
def scan_runs() -> list[dict[str, Any]]:
    """Return recent persisted scan runs."""

    return SQLiteRepository().list_scan_runs()


@app.get("/scan-runs/{scan_id}")
def scan_run(scan_id: str) -> dict[str, Any]:
    """Return one persisted scan run with telemetry and alerts."""

    result = SQLiteRepository().get_scan_run(scan_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Scan run not found")
    return result


@app.get("/audit-log")
def audit_log() -> list[dict[str, Any]]:
    """Return recent local audit log entries."""

    return SQLiteRepository().list_audit_log()


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
