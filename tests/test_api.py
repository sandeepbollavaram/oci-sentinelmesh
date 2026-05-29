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


def test_post_scan_returns_counts(monkeypatch) -> None:
    monkeypatch.setenv("OCI_SENTINEL_PERSISTENCE_ENABLED", "false")

    response = client.post("/scan")

    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "mock"
    assert body["telemetry_count"] == 12
    assert body["alert_count"] == 8
    assert len(body["alerts"]) == 8


def test_scan_persists_when_enabled(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("OCI_SENTINEL_PERSISTENCE_ENABLED", "true")
    monkeypatch.setenv("OCI_SENTINEL_DB_PATH", str(tmp_path / "api-scan.db"))

    response = client.post("/scan")

    assert response.status_code == 200
    body = response.json()
    assert body["scan_id"]

    scan_runs_response = client.get("/scan-runs")
    assert scan_runs_response.status_code == 200
    scan_runs = scan_runs_response.json()
    assert scan_runs[0]["scan_id"] == body["scan_id"]

    scan_run_response = client.get(f"/scan-runs/{body['scan_id']}")
    assert scan_run_response.status_code == 200
    scan_run = scan_run_response.json()
    assert scan_run["scan"]["scan_id"] == body["scan_id"]
    assert len(scan_run["telemetry"]) == body["telemetry_count"]
    assert len(scan_run["alerts"]) == body["alert_count"]


def test_get_audit_log_returns_entries_after_persisted_scan(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("OCI_SENTINEL_PERSISTENCE_ENABLED", "true")
    monkeypatch.setenv("OCI_SENTINEL_DB_PATH", str(tmp_path / "api-audit.db"))

    scan_response = client.post("/scan")
    audit_response = client.get("/audit-log")

    assert scan_response.status_code == 200
    assert audit_response.status_code == 200
    audit_entries = audit_response.json()
    assert audit_entries[0]["action"] == "mock_scan"
    assert audit_entries[0]["status"] == "success"
    assert audit_entries[0]["scan_id"] == scan_response.json()["scan_id"]


def test_scan_runs_endpoint_works_with_empty_database(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("OCI_SENTINEL_DB_PATH", str(tmp_path / "empty.db"))

    response = client.get("/scan-runs")

    assert response.status_code == 200
    assert response.json() == []


def test_persistence_disabled_does_not_break_scan(tmp_path, monkeypatch) -> None:
    db_path = tmp_path / "disabled.db"
    monkeypatch.setenv("OCI_SENTINEL_PERSISTENCE_ENABLED", "false")
    monkeypatch.setenv("OCI_SENTINEL_DB_PATH", str(db_path))

    response = client.post("/scan")

    assert response.status_code == 200
    assert response.json()["alert_count"] == 8
    assert not db_path.exists()
