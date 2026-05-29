"""SQLite schema for local OCI-SentinelMesh persistence."""

from __future__ import annotations

import sqlite3

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS scan_runs (
    scan_id TEXT PRIMARY KEY,
    mode TEXT NOT NULL,
    telemetry_count INTEGER NOT NULL,
    alert_count INTEGER NOT NULL,
    started_at TEXT NOT NULL,
    completed_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS telemetry_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_id TEXT NOT NULL,
    resource_id TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    name TEXT NOT NULL,
    compartment_id TEXT NOT NULL,
    region TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    metadata_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS alerts (
    alert_id TEXT NOT NULL,
    scan_id TEXT NOT NULL,
    rule_id TEXT NOT NULL,
    category TEXT NOT NULL,
    resource_id TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    recommendation TEXT NOT NULL,
    timestamp TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_log (
    audit_id TEXT PRIMARY KEY,
    scan_id TEXT,
    action TEXT NOT NULL,
    status TEXT NOT NULL,
    message TEXT NOT NULL,
    timestamp TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_telemetry_events_scan_id
    ON telemetry_events (scan_id);

CREATE INDEX IF NOT EXISTS idx_alerts_scan_id
    ON alerts (scan_id);

CREATE INDEX IF NOT EXISTS idx_alerts_severity
    ON alerts (severity);

CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp
    ON audit_log (timestamp);
"""


def initialize_schema(connection: sqlite3.Connection) -> None:
    """Create local persistence tables and indexes."""

    connection.executescript(SCHEMA_SQL)
    connection.commit()
