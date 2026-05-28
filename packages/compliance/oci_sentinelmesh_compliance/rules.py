"""Severity-based compliance rule registry."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from oci_sentinelmesh_collector import ResourceType, TelemetryItem

from .models import RuleCategory, RuleId, Severity

RuleMatcher = Callable[[TelemetryItem], bool]
TextBuilder = Callable[[TelemetryItem], str]


@dataclass(frozen=True, slots=True)
class ComplianceRule:
    """Definition for one local mock compliance rule."""

    rule_id: RuleId
    category: RuleCategory
    resource_type: ResourceType
    severity: Severity
    title: str
    description: TextBuilder
    recommendation: str
    matches: RuleMatcher


def _bucket_is_public(item: TelemetryItem) -> bool:
    return item.metadata.get("is_public") is True


def _bucket_is_unencrypted(item: TelemetryItem) -> bool:
    return item.metadata.get("encryption_enabled") is False


def _compute_cpu_above_80(item: TelemetryItem) -> bool:
    cpu_percent = _as_float(item.metadata.get("cpu_percent"))
    return cpu_percent is not None and cpu_percent > 80.0


def _compute_missing_required_tags(item: TelemetryItem) -> bool:
    required_tags = {"environment", "owner"}
    tags = item.metadata.get("freeform_tags")
    if not isinstance(tags, dict):
        return True
    normalized_tags = {str(key).lower() for key in tags}
    return not required_tags.issubset(normalized_tags)


def _iam_policy_has_broad_admin(item: TelemetryItem) -> bool:
    statement = str(item.metadata.get("policy_statement", "")).lower()
    return "manage all-resources" in statement and "tenancy" in statement


def _iam_policy_change_after_hours(item: TelemetryItem) -> bool:
    return item.timestamp.hour < 9 or item.timestamp.hour >= 18


def _network_exposes_public_ssh(item: TelemetryItem) -> bool:
    return _is_public_ingress_port(item, 22)


def _network_exposes_public_database_port(item: TelemetryItem) -> bool:
    return _is_public_ingress_port(item, 1521)


def _is_public_ingress_port(item: TelemetryItem, port: int) -> bool:
    protocol = str(item.metadata.get("protocol", "")).lower()
    source = str(item.metadata.get("source", ""))
    destination_port = _as_int(item.metadata.get("destination_port"))
    action = str(item.metadata.get("action", "")).upper()
    direction = str(item.metadata.get("direction", "")).upper()
    return (
        direction == "INGRESS"
        and action == "ALLOW"
        and protocol == "tcp"
        and source == "0.0.0.0/0"
        and destination_port == port
    )


def _cpu_description(item: TelemetryItem) -> str:
    cpu_percent = _as_float(item.metadata.get("cpu_percent"))
    if cpu_percent is None:
        return f"Compute instance '{item.name}' reports CPU usage above the allowed threshold."
    return f"Compute instance '{item.name}' reports CPU usage at {cpu_percent:.1f}%."


def _missing_tags_description(item: TelemetryItem) -> str:
    return f"Compute instance '{item.name}' is missing one or more required tags: environment, owner."


def _after_hours_description(item: TelemetryItem) -> str:
    return f"IAM policy change '{item.name}' occurred outside business hours."


RULES: tuple[ComplianceRule, ...] = (
    ComplianceRule(
        rule_id=RuleId.STORAGE_PUBLIC_ACCESS,
        category=RuleCategory.STORAGE,
        resource_type=ResourceType.OBJECT_STORAGE_BUCKET,
        severity=Severity.HIGH,
        title="Public object storage bucket",
        description=lambda item: f"Bucket '{item.name}' is marked public.",
        recommendation="Review bucket visibility and restrict public access unless it is explicitly required.",
        matches=_bucket_is_public,
    ),
    ComplianceRule(
        rule_id=RuleId.COMPUTE_HIGH_CPU,
        category=RuleCategory.COMPUTE,
        resource_type=ResourceType.COMPUTE_INSTANCE,
        severity=Severity.MEDIUM,
        title="Compute CPU above 80%",
        description=_cpu_description,
        recommendation="Investigate workload pressure, scaling options, or runaway processes.",
        matches=_compute_cpu_above_80,
    ),
    ComplianceRule(
        rule_id=RuleId.IAM_BROAD_ADMIN,
        category=RuleCategory.IAM,
        resource_type=ResourceType.IAM_POLICY_CHANGE,
        severity=Severity.HIGH,
        title="Broad IAM admin permission",
        description=lambda item: f"IAM policy change '{item.name}' grants broad administrative access.",
        recommendation="Apply least privilege and scope administrative grants to the smallest required group and compartment.",
        matches=_iam_policy_has_broad_admin,
    ),
    ComplianceRule(
        rule_id=RuleId.NETWORK_PUBLIC_SSH,
        category=RuleCategory.NETWORK,
        resource_type=ResourceType.NETWORK_SECURITY_RULE,
        severity=Severity.CRITICAL,
        title="SSH exposed to the public internet",
        description=lambda item: f"Network security rule '{item.name}' allows TCP/22 from 0.0.0.0/0.",
        recommendation="Restrict SSH to trusted source ranges or use a bastion/private access pattern.",
        matches=_network_exposes_public_ssh,
    ),
    ComplianceRule(
        rule_id=RuleId.NETWORK_PUBLIC_DATABASE_PORT,
        category=RuleCategory.NETWORK,
        resource_type=ResourceType.NETWORK_SECURITY_RULE,
        severity=Severity.CRITICAL,
        title="Database port exposed to the public internet",
        description=lambda item: f"Network security rule '{item.name}' allows TCP/1521 from 0.0.0.0/0.",
        recommendation="Restrict database access to private networks or trusted application source ranges.",
        matches=_network_exposes_public_database_port,
    ),
    ComplianceRule(
        rule_id=RuleId.STORAGE_UNENCRYPTED_BUCKET,
        category=RuleCategory.STORAGE,
        resource_type=ResourceType.OBJECT_STORAGE_BUCKET,
        severity=Severity.HIGH,
        title="Unencrypted object storage bucket",
        description=lambda item: f"Bucket '{item.name}' does not have encryption enabled.",
        recommendation="Enable bucket encryption and review data classification before storing sensitive content.",
        matches=_bucket_is_unencrypted,
    ),
    ComplianceRule(
        rule_id=RuleId.COMPUTE_MISSING_TAGS,
        category=RuleCategory.COMPUTE,
        resource_type=ResourceType.COMPUTE_INSTANCE,
        severity=Severity.LOW,
        title="Compute instance missing required tags",
        description=_missing_tags_description,
        recommendation="Add required ownership and environment tags to support governance and incident response.",
        matches=_compute_missing_required_tags,
    ),
    ComplianceRule(
        rule_id=RuleId.IAM_POLICY_CHANGE_AFTER_HOURS,
        category=RuleCategory.IAM,
        resource_type=ResourceType.IAM_POLICY_CHANGE,
        severity=Severity.MEDIUM,
        title="IAM policy changed after business hours",
        description=_after_hours_description,
        recommendation="Verify the change was approved and expected; review audit context for unusual access patterns.",
        matches=_iam_policy_change_after_hours,
    ),
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
