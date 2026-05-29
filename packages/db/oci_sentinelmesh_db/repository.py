"""SQLite repository for local scan persistence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .connection import connect
from .models import AuditEvent, PersistedAlert, ScanRun, TelemetryEvent
from .schema import initialize_schema


class SQLiteRepository:
    """Repository for local SQLite persistence."""

    def __init__(self, db_path: str | Path | None = None) -> None:
        self.db_path = db_path
        self.initialize()

    def initialize(self) -> None:
        with connect(self.db_path) as connection:
            initialize_schema(connection)

    def save_scan(
        self,
        *,
        scan_run: ScanRun,
        telemetry_events: list[TelemetryEvent],
        alerts: list[PersistedAlert],
        audit_event: AuditEvent,
    ) -> None:
        with connect(self.db_path) as connection:
            initialize_schema(connection)
            connection.execute(
                """
                INSERT INTO scan_runs (
                    scan_id, mode, telemetry_count, alert_count, started_at, completed_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    scan_run.scan_id,
                    scan_run.mode,
                    scan_run.telemetry_count,
                    scan_run.alert_count,
                    scan_run.started_at,
                    scan_run.completed_at,
                ),
            )
            connection.executemany(
                """
                INSERT INTO telemetry_events (
                    scan_id, resource_id, resource_type, name, compartment_id,
                    region, timestamp, metadata_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        item.scan_id,
                        item.resource_id,
                        item.resource_type,
                        item.name,
                        item.compartment_id,
                        item.region,
                        item.timestamp,
                        _json_dumps(item.metadata),
                    )
                    for item in telemetry_events
                ],
            )
            connection.executemany(
                """
                INSERT INTO alerts (
                    alert_id, scan_id, rule_id, category, resource_id, resource_type,
                    severity, title, description, recommendation, timestamp
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        alert.alert_id,
                        alert.scan_id,
                        alert.rule_id,
                        alert.category,
                        alert.resource_id,
                        alert.resource_type,
                        alert.severity,
                        alert.title,
                        alert.description,
                        alert.recommendation,
                        alert.timestamp,
                    )
                    for alert in alerts
                ],
            )
            self.save_audit_event(audit_event, connection=connection)
            connection.commit()

    def save_audit_event(self, audit_event: AuditEvent, *, connection: Any = None) -> None:
        should_close = connection is None
        active_connection = connection or connect(self.db_path)
        try:
            initialize_schema(active_connection)
            active_connection.execute(
                """
                INSERT INTO audit_log (
                    audit_id, scan_id, action, status, message, timestamp
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    audit_event.audit_id,
                    audit_event.scan_id,
                    audit_event.action,
                    audit_event.status,
                    audit_event.message,
                    audit_event.timestamp,
                ),
            )
            if should_close:
                active_connection.commit()
        finally:
            if should_close:
                active_connection.close()

    def list_scan_runs(self, *, limit: int = 20) -> list[dict[str, Any]]:
        with connect(self.db_path) as connection:
            initialize_schema(connection)
            rows = connection.execute(
                """
                SELECT scan_id, mode, telemetry_count, alert_count, started_at, completed_at
                FROM scan_runs
                ORDER BY completed_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def get_scan_run(self, scan_id: str) -> dict[str, Any] | None:
        with connect(self.db_path) as connection:
            initialize_schema(connection)
            scan_row = connection.execute(
                """
                SELECT scan_id, mode, telemetry_count, alert_count, started_at, completed_at
                FROM scan_runs
                WHERE scan_id = ?
                """,
                (scan_id,),
            ).fetchone()
            if scan_row is None:
                return None

            telemetry_rows = connection.execute(
                """
                SELECT scan_id, resource_id, resource_type, name, compartment_id,
                    region, timestamp, metadata_json
                FROM telemetry_events
                WHERE scan_id = ?
                ORDER BY id ASC
                """,
                (scan_id,),
            ).fetchall()
            alert_rows = connection.execute(
                """
                SELECT alert_id, scan_id, rule_id, category, resource_id, resource_type,
                    severity, title, description, recommendation, timestamp
                FROM alerts
                WHERE scan_id = ?
                ORDER BY severity ASC, alert_id ASC
                """,
                (scan_id,),
            ).fetchall()

        return {
            "scan": dict(scan_row),
            "telemetry": [_telemetry_row_to_dict(row) for row in telemetry_rows],
            "alerts": [dict(row) for row in alert_rows],
        }

    def list_audit_log(self, *, limit: int = 50) -> list[dict[str, Any]]:
        with connect(self.db_path) as connection:
            initialize_schema(connection)
            rows = connection.execute(
                """
                SELECT audit_id, scan_id, action, status, message, timestamp
                FROM audit_log
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]


def _telemetry_row_to_dict(row: Any) -> dict[str, Any]:
    data = dict(row)
    metadata_json = data.pop("metadata_json")
    data["metadata"] = json.loads(metadata_json)
    return data


def _json_dumps(value: Any) -> str:
    return json.dumps(value, default=str, sort_keys=True, separators=(",", ":"))
