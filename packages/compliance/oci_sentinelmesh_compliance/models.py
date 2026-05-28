"""Compliance alert models."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum


class Severity(str, Enum):
    """Supported alert severities."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True, slots=True)
class Alert:
    """A scanner alert produced from local telemetry."""

    alert_id: str
    resource_id: str
    severity: Severity
    title: str
    description: str
    recommendation: str
    timestamp: datetime

    def to_dict(self) -> dict[str, str]:
        """Return a JSON-friendly representation of the alert."""

        data = asdict(self)
        data["severity"] = self.severity.value
        data["timestamp"] = self.timestamp.isoformat()
        return data
