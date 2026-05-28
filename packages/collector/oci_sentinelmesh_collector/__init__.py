"""Local mock telemetry collector for OCI-SentinelMesh."""

from .mock import collect_mock_telemetry
from .models import ResourceType, TelemetryItem

__all__ = ["ResourceType", "TelemetryItem", "collect_mock_telemetry"]
