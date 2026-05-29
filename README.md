# OCI-SentinelMesh

[![CI](https://github.com/sandeepbollavaram/oci-sentinelmesh/actions/workflows/ci.yml/badge.svg)](https://github.com/sandeepbollavaram/oci-sentinelmesh/actions/workflows/ci.yml)

OCI-SentinelMesh is an autonomous cloud health and compliance monitoring agent for Oracle Cloud Infrastructure. The project is planned to observe OCI resource health, detect unusual or non-compliant states, match findings to compliance rules, and produce explainable alerts for operators while keeping remediation controlled and opt-in.

## Planned Architecture

- **Collector:** Gathers OCI health, inventory, configuration, and event data.
- **Compliance:** Maps observed states to local compliance rules and policy checks.
- **Agent:** Coordinates detection, explanation, alerting, and future remediation workflows.
- **API:** Exposes backend services for findings, rules, explanations, and integrations.
- **Dashboard:** Provides a human-facing view of health, compliance, and alerts.
- **Database:** Stores findings, rule metadata, audit history, and configuration.
- **Deploy:** Contains Kubernetes and Helm deployment assets when the system is ready.

## Safety-First Design

This repository starts mock/local-first. It must not contain real Oracle credentials, secrets, wallet files, tenancy identifiers, private keys, or paid cloud resource definitions. Early development should use fake data, local fixtures, and read-only assumptions. Auto-remediation is intentionally out of scope until monitoring, rule matching, explanations, and safety controls are designed and reviewed.

## Current Status

v0.2 local mock scanner foundation. The repository currently contains project structure, initial documentation, local-safe configuration examples, a deterministic mock telemetry collector, and a simple compliance scanner.

## v0.2 Local Mock Scan

The v0.2 workflow runs entirely on local mock data. It does not call OCI APIs, require Oracle credentials, create cloud resources, or perform remediation.

Run the mock scan:

```powershell
python scripts\mock_scan.py
```

Run tests:

```powershell
python -m unittest discover -s tests
```

The mock scan currently emits JSON alerts for public buckets, high compute CPU, broad IAM admin policy changes, and public SSH ingress.

## v0.3 FastAPI Backend

The v0.3 backend exposes the same local mock collector and compliance scanner through REST APIs. It remains mock-only and does not connect to OCI.

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Run the API:

```powershell
uvicorn apps.api.main:app --reload
```

Endpoints:

- `GET /health` returns service status.
- `GET /telemetry` returns all mock telemetry items.
- `GET /alerts` returns compliance alerts from mock telemetry.
- `POST /scan` runs a full mock scan and returns telemetry and alert counts with alerts.

Run tests:

```powershell
pytest
```

## v0.4 Compliance Severity Rule Engine

The v0.4 scanner uses a small severity-based rule engine with stable rule IDs, categories, and richer alert output. Alerts now include `alert_id`, `rule_id`, `category`, `resource_id`, `resource_type`, `severity`, `title`, `description`, `recommendation`, and `timestamp`.

Rules added:

- `STORAGE_PUBLIC_ACCESS`
- `COMPUTE_HIGH_CPU`
- `IAM_BROAD_ADMIN`
- `NETWORK_PUBLIC_SSH`
- `NETWORK_PUBLIC_DATABASE_PORT`
- `STORAGE_UNENCRYPTED_BUCKET`
- `COMPUTE_MISSING_TAGS`
- `IAM_POLICY_CHANGE_AFTER_HOURS`

Severity model:

- `LOW`
- `MEDIUM`
- `HIGH`
- `CRITICAL`

Safety note: v0.4 is alert-only. It uses deterministic local mock telemetry, does not call OCI APIs, does not require credentials, does not create resources, and does not perform remediation.

## v0.5 Dashboard

The v0.5 dashboard is a React + TypeScript Vite app that reads from the existing mock FastAPI backend. It shows system status, scan summary, severity totals, alerts, and telemetry in a local-first enterprise dashboard UI.

Run the backend:

```powershell
uvicorn apps.api.main:app --reload
```

Install frontend dependencies:

```powershell
cd apps\dashboard
npm install
```

Run the dashboard:

```powershell
npm run dev
```

Dashboard npm commands should be run from `apps/dashboard` because `package.json` is located there. Running `npm run build` from the repository root will fail.

```powershell
cd apps\dashboard
npm run build
```

Configure the API base URL with:

```text
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Safety note: v0.5 remains mock/local-first. The dashboard calls only the local FastAPI endpoints and does not call OCI APIs, require credentials, create resources, or perform remediation.

## v0.6 SQLite Persistence and Audit Log

The v0.6 backend can persist local mock scan history to SQLite. When enabled, each `POST /scan` stores the scan run, telemetry snapshot, generated alerts, and an audit log entry.

Environment variables:

```text
OCI_SENTINEL_DB_PATH=./data/oci-sentinelmesh.db
OCI_SENTINEL_PERSISTENCE_ENABLED=true
```

Run the API with persistence:

```powershell
$env:OCI_SENTINEL_PERSISTENCE_ENABLED="true"
$env:OCI_SENTINEL_DB_PATH="./data/oci-sentinelmesh.db"
uvicorn apps.api.main:app --reload
```

Run a persisted scan:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/scan
```

Inspect scan history:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/scan-runs
Invoke-RestMethod -Uri http://127.0.0.1:8000/audit-log
```

New API endpoints:

- `GET /scan-runs` returns recent persisted scan runs.
- `GET /scan-runs/{scan_id}` returns one scan run with telemetry events and alerts.
- `GET /audit-log` returns recent audit log entries.

Safety note: v0.6 uses local SQLite only. Oracle Database is not required yet, no real OCI APIs are called, no credentials are needed, no cloud resources are created, and no auto-remediation is performed.

## Planned Tech Stack

- Python
- FastAPI
- React
- TypeScript
- Oracle Cloud Infrastructure SDK
- Oracle Database or Oracle Autonomous Database
- Kubernetes
- Helm

## Local Development

Use `.env.example` as a template for local fake values only. Copy it to `.env` when needed, keep `.env` untracked, and do not connect to live OCI APIs or create cloud resources during the scaffold phase.
