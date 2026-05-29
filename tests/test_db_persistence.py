from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "collector"))
sys.path.insert(0, str(ROOT / "packages" / "compliance"))
sys.path.insert(0, str(ROOT / "packages" / "db"))

from oci_sentinelmesh_collector import collect_mock_telemetry
from oci_sentinelmesh_compliance import scan_telemetry
from oci_sentinelmesh_db import SQLiteRepository
from oci_sentinelmesh_db.connection import connect
from oci_sentinelmesh_db.models import (
    AuditEvent,
    PersistedAlert,
    ScanRun,
    TelemetryEvent,
)
from oci_sentinelmesh_db.schema import initialize_schema


def test_schema_initialization_creates_tables(tmp_path: Path) -> None:
    db_path = tmp_path / "sentinelmesh.db"

    with connect(db_path) as connection:
        initialize_schema(connection)
        tables = {
            row["name"]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }

    assert {"scan_runs", "telemetry_events", "alerts", "audit_log"} <= tables


def test_repository_saves_and_reads_scan_data(tmp_path: Path) -> None:
    db_path = tmp_path / "nested" / "sentinelmesh.db"
    repository = SQLiteRepository(db_path)
    telemetry = collect_mock_telemetry()
    alerts = scan_telemetry(telemetry)
    scan_run = ScanRun(
        scan_id="scan-test-001",
        mode="mock",
        telemetry_count=len(telemetry),
        alert_count=len(alerts),
        started_at="2026-01-01T00:00:00+00:00",
        completed_at="2026-01-01T00:00:02+00:00",
    )

    repository.save_scan(
        scan_run=scan_run,
        telemetry_events=[
            TelemetryEvent(
                scan_id=scan_run.scan_id,
                resource_id=item.resource_id,
                resource_type=item.resource_type.value,
                name=item.name,
                compartment_id=item.compartment_id,
                region=item.region,
                timestamp=item.timestamp.isoformat(),
                metadata=item.metadata,
            )
            for item in telemetry
        ],
        alerts=[
            PersistedAlert(
                alert_id=alert.alert_id,
                scan_id=scan_run.scan_id,
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
            for alert in alerts
        ],
        audit_event=AuditEvent(
            audit_id="audit-test-001",
            scan_id=scan_run.scan_id,
            action="mock_scan",
            status="success",
            message="Persisted test scan.",
            timestamp=scan_run.completed_at,
        ),
    )

    scan_runs = repository.list_scan_runs()
    persisted_scan = repository.get_scan_run(scan_run.scan_id)
    audit_log = repository.list_audit_log()

    assert db_path.exists()
    assert scan_runs[0]["scan_id"] == scan_run.scan_id
    assert persisted_scan is not None
    assert persisted_scan["scan"]["telemetry_count"] == len(telemetry)
    assert len(persisted_scan["telemetry"]) == len(telemetry)
    assert len(persisted_scan["alerts"]) == len(alerts)
    assert persisted_scan["telemetry"][0]["metadata"]
    assert audit_log[0]["audit_id"] == "audit-test-001"


def test_repository_returns_none_for_missing_scan(tmp_path: Path) -> None:
    repository = SQLiteRepository(tmp_path / "sentinelmesh.db")

    assert repository.get_scan_run("missing-scan") is None
