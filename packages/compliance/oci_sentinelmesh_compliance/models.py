"""Compliance alert models."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum

from oci_sentinelmesh_collector import ResourceType


class Severity(str, Enum):
    """Supported alert severities."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RuleCategory(str, Enum):
    """High-level compliance rule categories."""

    STORAGE = "STORAGE"
    COMPUTE = "COMPUTE"
    IAM = "IAM"
    NETWORK = "NETWORK"


class RuleId(str, Enum):
    """Stable compliance rule identifiers."""

    STORAGE_PUBLIC_ACCESS = "STORAGE_PUBLIC_ACCESS"
    COMPUTE_HIGH_CPU = "COMPUTE_HIGH_CPU"
    IAM_BROAD_ADMIN = "IAM_BROAD_ADMIN"
    NETWORK_PUBLIC_SSH = "NETWORK_PUBLIC_SSH"
    NETWORK_PUBLIC_DATABASE_PORT = "NETWORK_PUBLIC_DATABASE_PORT"
    STORAGE_UNENCRYPTED_BUCKET = "STORAGE_UNENCRYPTED_BUCKET"
    COMPUTE_MISSING_TAGS = "COMPUTE_MISSING_TAGS"
    IAM_POLICY_CHANGE_AFTER_HOURS = "IAM_POLICY_CHANGE_AFTER_HOURS"


@dataclass(frozen=True, slots=True)
class Alert:
    """A scanner alert produced from local telemetry."""

    alert_id: str
    rule_id: RuleId
    category: RuleCategory
    resource_id: str
    resource_type: ResourceType
    severity: Severity
    title: str
    description: str
    recommendation: str
    timestamp: datetime

    def to_dict(self) -> dict[str, str]:
        """Return a JSON-friendly representation of the alert."""

        data = asdict(self)
        data["rule_id"] = self.rule_id.value
        data["category"] = self.category.value
        data["resource_type"] = self.resource_type.value
        data["severity"] = self.severity.value
        data["timestamp"] = self.timestamp.isoformat()
        return data
