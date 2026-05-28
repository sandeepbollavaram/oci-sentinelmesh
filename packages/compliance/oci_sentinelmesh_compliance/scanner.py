"""Simple local compliance scanner for mock OCI telemetry."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from oci_sentinelmesh_collector import ResourceType, TelemetryItem

from .models import Alert, Severity


def scan_telemetry(items: Iterable[TelemetryItem]) -> list[Alert]:
    """Scan telemetry and return compliance alerts."""

    alerts: list[Alert] = []
    for item in items:
        if item.resource_type == ResourceType.OBJECT_STORAGE_BUCKET:
            alerts.extend(_scan_bucket(item))
        elif item.resource_type == ResourceType.COMPUTE_INSTANCE:
            alerts.extend(_scan_compute(item))
        elif item.resource_type == ResourceType.IAM_POLICY_CHANGE:
            alerts.extend(_scan_iam_policy_change(item))
        elif item.resource_type == ResourceType.NETWORK_SECURITY_RULE:
            alerts.extend(_scan_network_security_rule(item))
    return alerts


def _scan_bucket(item: TelemetryItem) -> list[Alert]:
    if item.metadata.get("is_public") is True:
        return [
            _alert(
                rule_id="public-object-storage-bucket",
                item=item,
                severity=Severity.HIGH,
                title="Public object storage bucket",
                description=f"Bucket '{item.name}' is marked public.",
                recommendation="Review bucket visibility and restrict public access unless it is explicitly required.",
            )
        ]
    return []


def _scan_compute(item: TelemetryItem) -> list[Alert]:
    cpu_percent = _as_float(item.metadata.get("cpu_percent"))
    if cpu_percent is not None and cpu_percent > 80.0:
        return [
            _alert(
                rule_id="compute-high-cpu",
                item=item,
                severity=Severity.MEDIUM,
                title="Compute CPU above 80%",
                description=f"Compute instance '{item.name}' reports CPU usage at {cpu_percent:.1f}%.",
                recommendation="Investigate workload pressure, scaling options, or runaway processes.",
            )
        ]
    return []


def _scan_iam_policy_change(item: TelemetryItem) -> list[Alert]:
    statement = str(item.metadata.get("policy_statement", "")).lower()
    has_broad_admin = "manage all-resources" in statement and "tenancy" in statement
    if has_broad_admin:
        return [
            _alert(
                rule_id="broad-iam-admin-permission",
                item=item,
                severity=Severity.HIGH,
                title="Broad IAM admin permission",
                description=f"IAM policy change '{item.name}' grants broad administrative access.",
                recommendation="Apply least privilege and scope administrative grants to the smallest required group and compartment.",
            )
        ]
    return []


def _scan_network_security_rule(item: TelemetryItem) -> list[Alert]:
    protocol = str(item.metadata.get("protocol", "")).lower()
    source = str(item.metadata.get("source", ""))
    port = _as_int(item.metadata.get("destination_port"))
    action = str(item.metadata.get("action", "")).upper()
    direction = str(item.metadata.get("direction", "")).upper()

    exposes_public_ssh = (
        direction == "INGRESS"
        and action == "ALLOW"
        and protocol == "tcp"
        and source == "0.0.0.0/0"
        and port == 22
    )
    if exposes_public_ssh:
        return [
            _alert(
                rule_id="public-ssh-ingress",
                item=item,
                severity=Severity.CRITICAL,
                title="SSH exposed to the public internet",
                description=f"Network security rule '{item.name}' allows TCP/22 from 0.0.0.0/0.",
                recommendation="Restrict SSH to trusted source ranges or use a bastion/private access pattern.",
            )
        ]
    return []


def _alert(
    *,
    rule_id: str,
    item: TelemetryItem,
    severity: Severity,
    title: str,
    description: str,
    recommendation: str,
) -> Alert:
    return Alert(
        alert_id=f"{rule_id}:{item.resource_id}",
        resource_id=item.resource_id,
        severity=severity,
        title=title,
        description=description,
        recommendation=recommendation,
        timestamp=item.timestamp,
    )


def _as_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _as_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
