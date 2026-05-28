# Architecture

OCI-SentinelMesh is planned as a safety-first monitoring flow that starts with observation and ends with explainable alerts. Remediation is a future capability and is not part of the scaffold phase.

## Observe

The collector will observe OCI resource state, events, configuration, health signals, and inventory metadata. During early development, this layer should use local mocks and fixtures instead of live OCI API calls.

## Detect

Detection logic will identify abnormal, risky, or policy-relevant states from observed data. Initial detection should focus on deterministic local checks that are easy to test and review.

## Match Compliance Rule

Findings will be matched against compliance rules that describe expected cloud posture. Rules should be versioned, auditable, and explicit about severity, evidence, and affected resources.

## Alert

The system will raise alerts for findings that require attention. Alerts should include enough context for an operator to understand what happened, which resource is affected, and why the finding matters.

## Explain

The agent will generate clear explanations for findings, including observed evidence, matched rules, risk level, and recommended human review steps. Explanations should avoid implying that changes were made automatically.

## Future Remediation

Auto-remediation is a future milestone. Any remediation capability should require explicit safety controls, dry-run behavior, audit logs, approval gates, and least-privilege OCI access before it is considered.
