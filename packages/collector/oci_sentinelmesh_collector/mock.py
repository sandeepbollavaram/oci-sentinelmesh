"""Mock OCI telemetry source.

This module never calls OCI APIs. All telemetry is deterministic local sample
data for scanner development and tests.
"""

from __future__ import annotations

from datetime import datetime, timezone

from .models import ResourceType, TelemetryItem

MOCK_COMPARTMENT_ID = "ocid1.compartment.oc1..mock"
MOCK_REGION = "us-ashburn-1"
MOCK_TIMESTAMP = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
MOCK_AFTER_HOURS_TIMESTAMP = datetime(2026, 1, 1, 22, 30, 0, tzinfo=timezone.utc)


def collect_mock_telemetry() -> list[TelemetryItem]:
    """Return representative local mock OCI telemetry items."""

    return [
        TelemetryItem(
            resource_id="ocid1.instance.oc1.iad.mocknormalcompute",
            resource_type=ResourceType.COMPUTE_INSTANCE,
            name="normal-compute-instance",
            compartment_id=MOCK_COMPARTMENT_ID,
            region=MOCK_REGION,
            timestamp=MOCK_TIMESTAMP,
            metadata={
                "lifecycle_state": "RUNNING",
                "shape": "VM.Standard.E4.Flex",
                "cpu_percent": 24.5,
                "freeform_tags": {
                    "environment": "dev",
                    "owner": "platform",
                },
            },
        ),
        TelemetryItem(
            resource_id="ocid1.instance.oc1.iad.mockhighcpu",
            resource_type=ResourceType.COMPUTE_INSTANCE,
            name="high-cpu-compute-instance",
            compartment_id=MOCK_COMPARTMENT_ID,
            region=MOCK_REGION,
            timestamp=MOCK_TIMESTAMP,
            metadata={
                "lifecycle_state": "RUNNING",
                "shape": "VM.Standard.E4.Flex",
                "cpu_percent": 91.2,
                "freeform_tags": {
                    "environment": "dev",
                    "owner": "platform",
                },
            },
        ),
        TelemetryItem(
            resource_id="ocid1.instance.oc1.iad.mockmissingtags",
            resource_type=ResourceType.COMPUTE_INSTANCE,
            name="missing-tags-compute-instance",
            compartment_id=MOCK_COMPARTMENT_ID,
            region=MOCK_REGION,
            timestamp=MOCK_TIMESTAMP,
            metadata={
                "lifecycle_state": "RUNNING",
                "shape": "VM.Standard.E4.Flex",
                "cpu_percent": 16.8,
                "freeform_tags": {
                    "environment": "dev",
                },
            },
        ),
        TelemetryItem(
            resource_id="ocid1.bucket.oc1.iad.mockprivatebucket",
            resource_type=ResourceType.OBJECT_STORAGE_BUCKET,
            name="private-audit-logs",
            compartment_id=MOCK_COMPARTMENT_ID,
            region=MOCK_REGION,
            timestamp=MOCK_TIMESTAMP,
            metadata={
                "namespace": "mocknamespace",
                "is_public": False,
                "storage_tier": "Standard",
                "encryption_enabled": True,
            },
        ),
        TelemetryItem(
            resource_id="ocid1.bucket.oc1.iad.mockpublicbucket",
            resource_type=ResourceType.OBJECT_STORAGE_BUCKET,
            name="public-export-bucket",
            compartment_id=MOCK_COMPARTMENT_ID,
            region=MOCK_REGION,
            timestamp=MOCK_TIMESTAMP,
            metadata={
                "namespace": "mocknamespace",
                "is_public": True,
                "storage_tier": "Standard",
                "encryption_enabled": True,
            },
        ),
        TelemetryItem(
            resource_id="ocid1.bucket.oc1.iad.mockunencryptedbucket",
            resource_type=ResourceType.OBJECT_STORAGE_BUCKET,
            name="unencrypted-backup-bucket",
            compartment_id=MOCK_COMPARTMENT_ID,
            region=MOCK_REGION,
            timestamp=MOCK_TIMESTAMP,
            metadata={
                "namespace": "mocknamespace",
                "is_public": False,
                "storage_tier": "Standard",
                "encryption_enabled": False,
            },
        ),
        TelemetryItem(
            resource_id="ocid1.audit.oc1.iad.mocknormalpolicy",
            resource_type=ResourceType.IAM_POLICY_CHANGE,
            name="normal-iam-policy-change",
            compartment_id=MOCK_COMPARTMENT_ID,
            region=MOCK_REGION,
            timestamp=MOCK_TIMESTAMP,
            metadata={
                "actor": "mock-security-admin",
                "change_type": "UPDATE",
                "policy_statement": "Allow group Observers to read instances in compartment Sandbox",
            },
        ),
        TelemetryItem(
            resource_id="ocid1.audit.oc1.iad.mockriskyadminpolicy",
            resource_type=ResourceType.IAM_POLICY_CHANGE,
            name="risky-iam-policy-change",
            compartment_id=MOCK_COMPARTMENT_ID,
            region=MOCK_REGION,
            timestamp=MOCK_TIMESTAMP,
            metadata={
                "actor": "mock-platform-admin",
                "change_type": "CREATE",
                "policy_statement": "Allow group Contractors to manage all-resources in tenancy",
            },
        ),
        TelemetryItem(
            resource_id="ocid1.audit.oc1.iad.mockafterhourspolicy",
            resource_type=ResourceType.IAM_POLICY_CHANGE,
            name="after-hours-iam-policy-change",
            compartment_id=MOCK_COMPARTMENT_ID,
            region=MOCK_REGION,
            timestamp=MOCK_AFTER_HOURS_TIMESTAMP,
            metadata={
                "actor": "mock-security-admin",
                "change_type": "UPDATE",
                "policy_statement": "Allow group Auditors to read audit-events in tenancy",
            },
        ),
        TelemetryItem(
            resource_id="ocid1.securityrule.oc1.iad.mocksafenetworkrule",
            resource_type=ResourceType.NETWORK_SECURITY_RULE,
            name="safe-network-rule",
            compartment_id=MOCK_COMPARTMENT_ID,
            region=MOCK_REGION,
            timestamp=MOCK_TIMESTAMP,
            metadata={
                "direction": "INGRESS",
                "protocol": "tcp",
                "source": "10.0.0.0/24",
                "destination_port": 443,
                "action": "ALLOW",
            },
        ),
        TelemetryItem(
            resource_id="ocid1.securityrule.oc1.iad.mockpublicssh",
            resource_type=ResourceType.NETWORK_SECURITY_RULE,
            name="open-public-ssh-rule",
            compartment_id=MOCK_COMPARTMENT_ID,
            region=MOCK_REGION,
            timestamp=MOCK_TIMESTAMP,
            metadata={
                "direction": "INGRESS",
                "protocol": "tcp",
                "source": "0.0.0.0/0",
                "destination_port": 22,
                "action": "ALLOW",
            },
        ),
        TelemetryItem(
            resource_id="ocid1.securityrule.oc1.iad.mockpublicdb",
            resource_type=ResourceType.NETWORK_SECURITY_RULE,
            name="open-public-database-rule",
            compartment_id=MOCK_COMPARTMENT_ID,
            region=MOCK_REGION,
            timestamp=MOCK_TIMESTAMP,
            metadata={
                "direction": "INGRESS",
                "protocol": "tcp",
                "source": "0.0.0.0/0",
                "destination_port": 1521,
                "action": "ALLOW",
            },
        ),
    ]
