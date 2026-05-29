"""Persistence data models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def utc_now_iso() -> str:
    """Return the current UTC timestamp as an ISO 8601 string."""

    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True, slots=True)
class ScanRun:
    scan_id: str
    mode: str
    telemetry_count: int
    alert_count: int
    started_at: str
    completed_at: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "scan_id": self.scan_id,
            "mode": self.mode,
            "telemetry_count": self.telemetry_count,
            "alert_count": self.alert_count,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
        }


@dataclass(frozen=True, slots=True)
class TelemetryEvent:
    scan_id: str
    resource_id: str
    resource_type: str
    name: str
    compartment_id: str
    region: str
    timestamp: str
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "scan_id": self.scan_id,
            "resource_id": self.resource_id,
            "resource_type": self.resource_type,
            "name": self.name,
            "compartment_id": self.compartment_id,
            "region": self.region,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }


@dataclass(frozen=True, slots=True)
class PersistedAlert:
    alert_id: str
    scan_id: str
    rule_id: str
    category: str
    resource_id: str
    resource_type: str
    severity: str
    title: str
    description: str
    recommendation: str
    timestamp: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "scan_id": self.scan_id,
            "rule_id": self.rule_id,
            "category": self.category,
            "resource_id": self.resource_id,
            "resource_type": self.resource_type,
            "severity": self.severity,
            "title": self.title,
            "description": self.description,
            "recommendation": self.recommendation,
            "timestamp": self.timestamp,
        }


@dataclass(frozen=True, slots=True)
class AuditEvent:
    audit_id: str
    scan_id: str | None
    action: str
    status: str
    message: str
    timestamp: str

    @classmethod
    def create(
        cls,
        *,
        action: str,
        status: str,
        message: str,
        scan_id: str | None = None,
        timestamp: str | None = None,
    ) -> "AuditEvent":
        return cls(
            audit_id=str(uuid4()),
            scan_id=scan_id,
            action=action,
            status=status,
            message=message,
            timestamp=timestamp or utc_now_iso(),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "audit_id": self.audit_id,
            "scan_id": self.scan_id,
            "action": self.action,
            "status": self.status,
            "message": self.message,
            "timestamp": self.timestamp,
        }
