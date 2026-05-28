from __future__ import annotations

from fastapi.testclient import TestClient

from apps.api.main import app


client = TestClient(app)


def test_get_health_returns_200() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "oci-sentinelmesh-api",
        "mode": "mock",
    }


def test_get_telemetry_returns_list() -> None:
    response = client.get("/telemetry")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert len(body) == 12
    assert {"resource_id", "resource_type", "name", "compartment_id", "region", "timestamp", "metadata"} <= set(body[0])


def test_get_alerts_returns_expected_alert_list() -> None:
    response = client.get("/alerts")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert len(body) == 8
    assert {alert["severity"] for alert in body} == {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
    assert {
        "alert_id",
        "rule_id",
        "category",
        "resource_id",
        "resource_type",
        "severity",
        "title",
        "description",
        "recommendation",
        "timestamp",
    } <= set(body[0])
    assert "NETWORK_PUBLIC_SSH:ocid1.securityrule.oc1.iad.mockpublicssh" in {
        alert["alert_id"] for alert in body
    }


def test_post_scan_returns_counts() -> None:
    response = client.post("/scan")

    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "mock"
    assert body["telemetry_count"] == 12
    assert body["alert_count"] == 8
    assert len(body["alerts"]) == 8
