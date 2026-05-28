# OCI-SentinelMesh

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

Scaffold phase. The repository currently contains project structure, initial documentation, placeholder module READMEs, and local-safe configuration examples only.

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
