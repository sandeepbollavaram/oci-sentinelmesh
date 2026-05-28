"""Rule-engine scanner for local mock OCI telemetry."""

from __future__ import annotations

from collections.abc import Iterable

from oci_sentinelmesh_collector import TelemetryItem

from .models import Alert
from .rules import RULES, ComplianceRule


def scan_telemetry(items: Iterable[TelemetryItem]) -> list[Alert]:
    """Scan telemetry with registered compliance rules."""

    alerts: list[Alert] = []
    for item in items:
        for rule in RULES:
            if rule.resource_type == item.resource_type and rule.matches(item):
                alerts.append(_build_alert(rule, item))
    return alerts


def _build_alert(rule: ComplianceRule, item: TelemetryItem) -> Alert:
    return Alert(
        alert_id=f"{rule.rule_id.value}:{item.resource_id}",
        rule_id=rule.rule_id,
        category=rule.category,
        resource_id=item.resource_id,
        resource_type=item.resource_type,
        severity=rule.severity,
        title=rule.title,
        description=rule.description(item),
        recommendation=rule.recommendation,
        timestamp=item.timestamp,
    )
