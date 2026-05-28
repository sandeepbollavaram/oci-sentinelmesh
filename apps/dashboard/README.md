# OCI-SentinelMesh Dashboard

React + TypeScript dashboard for the local OCI-SentinelMesh mock backend. The UI displays API health, scan summary, severity counts, compliance alerts, and mock telemetry from the FastAPI service.

## Setup

Install dependencies from this directory:

```powershell
npm install
```

Create local environment configuration from the example:

```powershell
Copy-Item .env.example .env
```

The dashboard expects the backend at:

```text
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## Available Scripts

```powershell
npm run dev
npm run build
npm run preview
```

No lint script is configured yet.

## Backend Dependency

Start the FastAPI mock backend from the repository root before running the dashboard:

```powershell
uvicorn apps.api.main:app --reload
```

The dashboard uses only local mock endpoints and does not call OCI APIs.
