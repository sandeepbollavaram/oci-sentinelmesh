# Roadmap

## v0.1 Scaffold

Create the initial repository structure, documentation, local-safe examples, and placeholder package directories.

## v0.2 Mock Collector

Add a local mock collector that reads fixture data and produces normalized resource observations without calling OCI APIs.

## v0.3 FastAPI Backend

Introduce a FastAPI service with local endpoints for health checks, mock observations, findings, and rule evaluation results.

## v0.4 Compliance Rules

Define the first local compliance rule format, sample rules, tests, and deterministic matching behavior.

## v0.5 Dashboard

Build an initial dashboard for viewing mock resource health, compliance findings, explanations, and alert status.

## v0.6 OCI Read-Only Integration

Add read-only OCI SDK integration after safety review, using least-privilege credentials and no resource mutation.

## v0.7 Oracle DB Integration

Add Oracle Database or Oracle Autonomous Database persistence for findings, rules, audit history, and configuration.

## v0.8 Kubernetes/Helm Deployment

Add Kubernetes manifests and Helm charts for deployment after the local-first system is stable and reviewed.
