"""Telemetry data models for local mock collection."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class ResourceType(str, Enum):
    """Supported local mock OCI telemetry resource types."""

    COMPUTE_INSTANCE = "compute_instance"
    OBJECT_STORAGE_BUCKET = "object_storage_bucket"
    IAM_POLICY_CHANGE = "iam_policy_change"
    NETWORK_SECURITY_RULE = "network_security_rule"


@dataclass(frozen=True, slots=True)
class TelemetryItem:
    """A normalized mock telemetry item.

    The model intentionally contains no OCI SDK objects or credentials so it can
    be safely used in local tests and demos.
    """

    resource_id: str
    resource_type: ResourceType
    name: str
    compartment_id: str
    region: str
    timestamp: datetime
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly representation of the telemetry item."""

        data = asdict(self)
        data["resource_type"] = self.resource_type.value
        data["timestamp"] = self.timestamp.isoformat()
        return data
