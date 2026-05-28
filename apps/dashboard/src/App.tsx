import { useCallback, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import {
  Activity,
  AlertTriangle,
  Cloud,
  Database,
  RefreshCw,
  ShieldCheck
} from "lucide-react";

type Severity = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";

type HealthResponse = {
  status: string;
  service: string;
  mode: string;
};

type TelemetryItem = {
  resource_id: string;
  resource_type: string;
  name: string;
  compartment_id: string;
  region: string;
  timestamp: string;
  metadata: Record<string, unknown>;
};

type AlertItem = {
  alert_id: string;
  rule_id: string;
  category: string;
  resource_id: string;
  resource_type: string;
  severity: Severity;
  title: string;
  description: string;
  recommendation: string;
  timestamp: string;
};

type ScanResponse = {
  mode: string;
  telemetry_count: number;
  alert_count: number;
  alerts: AlertItem[];
};

type DashboardState = {
  health: HealthResponse | null;
  telemetry: TelemetryItem[];
  alerts: AlertItem[];
  scan: ScanResponse | null;
};

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") ??
  "http://127.0.0.1:8000";

const severities: Severity[] = ["CRITICAL", "HIGH", "MEDIUM", "LOW"];

const initialState: DashboardState = {
  health: null,
  telemetry: [],
  alerts: [],
  scan: null
};

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, init);
  if (!response.ok) {
    throw new Error(`${path} returned ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export function App() {
  const [state, setState] = useState<DashboardState>(initialState);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadDashboard = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const [health, telemetry, alerts, scan] = await Promise.all([
        requestJson<HealthResponse>("/health"),
        requestJson<TelemetryItem[]>("/telemetry"),
        requestJson<AlertItem[]>("/alerts"),
        requestJson<ScanResponse>("/scan", { method: "POST" })
      ]);

      setState({ health, telemetry, alerts, scan });
    } catch (caught) {
      const message =
        caught instanceof Error
          ? caught.message
          : "Unable to load dashboard data.";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadDashboard();
  }, [loadDashboard]);

  const severityCounts = useMemo(() => {
    return severities.reduce<Record<Severity, number>>(
      (counts, severity) => {
        counts[severity] = state.alerts.filter(
          (alert) => alert.severity === severity
        ).length;
        return counts;
      },
      { CRITICAL: 0, HIGH: 0, MEDIUM: 0, LOW: 0 }
    );
  }, [state.alerts]);

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand-lockup" aria-label="OCI-SentinelMesh">
          <div className="brand-mark" aria-hidden="true">
            <ShieldCheck size={24} strokeWidth={1.8} />
          </div>
          <div>
            <h1>OCI-SentinelMesh</h1>
            <p>Mock cloud health and compliance command center</p>
          </div>
        </div>
        <button
          className="refresh-button"
          type="button"
          onClick={() => void loadDashboard()}
          disabled={isLoading}
          aria-label="Refresh dashboard data"
        >
          <RefreshCw
            size={18}
            strokeWidth={2}
            className={isLoading ? "spin" : undefined}
            aria-hidden="true"
          />
          Refresh
        </button>
      </header>

      <main className="dashboard" aria-busy={isLoading}>
        {error ? (
          <ErrorState message={error} onRetry={loadDashboard} />
        ) : (
          <>
            <section className="summary-grid" aria-label="Dashboard summary">
              <MetricCard
                icon={<Activity size={20} aria-hidden="true" />}
                label="System status"
                value={state.health?.status.toUpperCase() ?? "PENDING"}
                detail={`${state.health?.service ?? "oci-sentinelmesh-api"} · ${
                  state.health?.mode ?? "mock"
                }`}
                tone="status"
                loading={isLoading}
              />
              <MetricCard
                icon={<Cloud size={20} aria-hidden="true" />}
                label="Telemetry resources"
                value={state.scan?.telemetry_count ?? state.telemetry.length}
                detail="Collected from local mock data"
                tone="neutral"
                loading={isLoading}
              />
              <MetricCard
                icon={<AlertTriangle size={20} aria-hidden="true" />}
                label="Open alerts"
                value={state.scan?.alert_count ?? state.alerts.length}
                detail="Compliance findings only"
                tone="warning"
                loading={isLoading}
              />
              <MetricCard
                icon={<Database size={20} aria-hidden="true" />}
                label="API base"
                value={new URL(API_BASE_URL).host}
                detail="Configured by VITE_API_BASE_URL"
                tone="neutral"
                loading={isLoading}
              />
            </section>

            <section className="severity-grid" aria-label="Severity summary">
              {severities.map((severity) => (
                <SeverityCard
                  key={severity}
                  severity={severity}
                  count={severityCounts[severity]}
                  loading={isLoading}
                />
              ))}
            </section>

            <section className="panel">
              <SectionHeader
                title="Alerts"
                description="Severity-ranked findings returned by GET /alerts"
              />
              <AlertsTable alerts={state.alerts} loading={isLoading} />
            </section>

            <section className="panel">
              <SectionHeader
                title="Telemetry"
                description="Mock resource observations returned by GET /telemetry"
              />
              <TelemetryTable telemetry={state.telemetry} loading={isLoading} />
            </section>
          </>
        )}
      </main>
    </div>
  );
}

function MetricCard({
  icon,
  label,
  value,
  detail,
  tone,
  loading
}: {
  icon: ReactNode;
  label: string;
  value: string | number;
  detail: string;
  tone: "neutral" | "status" | "warning";
  loading: boolean;
}) {
  return (
    <article className={`metric-card tone-${tone}`}>
      <div className="metric-icon">{icon}</div>
      <div>
        <p className="metric-label">{label}</p>
        {loading ? <div className="skeleton metric-skeleton" /> : <strong>{value}</strong>}
        <span>{detail}</span>
      </div>
    </article>
  );
}

function SeverityCard({
  severity,
  count,
  loading
}: {
  severity: Severity;
  count: number;
  loading: boolean;
}) {
  return (
    <article className={`severity-card severity-${severity.toLowerCase()}`}>
      <span>{severity}</span>
      {loading ? <div className="skeleton count-skeleton" /> : <strong>{count}</strong>}
    </article>
  );
}

function SectionHeader({
  title,
  description
}: {
  title: string;
  description: string;
}) {
  return (
    <div className="section-header">
      <div>
        <h2>{title}</h2>
        <p>{description}</p>
      </div>
    </div>
  );
}

function AlertsTable({
  alerts,
  loading
}: {
  alerts: AlertItem[];
  loading: boolean;
}) {
  if (loading) {
    return <TableLoading rows={4} />;
  }

  if (alerts.length === 0) {
    return <EmptyState message="No alerts returned by the mock scanner." />;
  }

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Severity</th>
            <th>Rule</th>
            <th>Resource</th>
            <th>Finding</th>
            <th>Recommendation</th>
          </tr>
        </thead>
        <tbody>
          {alerts.map((alert) => (
            <tr key={alert.alert_id}>
              <td>
                <SeverityBadge severity={alert.severity} />
              </td>
              <td>
                <code>{alert.rule_id}</code>
                <span className="cell-subtext">{alert.category}</span>
              </td>
              <td>
                <span className="resource-name">{alert.resource_type}</span>
                <span className="cell-subtext truncate">{alert.resource_id}</span>
              </td>
              <td>
                <strong>{alert.title}</strong>
                <span className="cell-subtext">{alert.description}</span>
              </td>
              <td>{alert.recommendation}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function TelemetryTable({
  telemetry,
  loading
}: {
  telemetry: TelemetryItem[];
  loading: boolean;
}) {
  if (loading) {
    return <TableLoading rows={5} />;
  }

  if (telemetry.length === 0) {
    return <EmptyState message="No telemetry returned by the mock collector." />;
  }

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Type</th>
            <th>Region</th>
            <th>Compartment</th>
            <th>Timestamp</th>
          </tr>
        </thead>
        <tbody>
          {telemetry.map((item) => (
            <tr key={item.resource_id}>
              <td>
                <strong>{item.name}</strong>
                <span className="cell-subtext truncate">{item.resource_id}</span>
              </td>
              <td>{item.resource_type}</td>
              <td>{item.region}</td>
              <td>
                <span className="truncate">{item.compartment_id}</span>
              </td>
              <td>{formatTimestamp(item.timestamp)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function SeverityBadge({ severity }: { severity: Severity }) {
  return (
    <span className={`severity-badge severity-${severity.toLowerCase()}`}>
      {severity}
    </span>
  );
}

function ErrorState({
  message,
  onRetry
}: {
  message: string;
  onRetry: () => void;
}) {
  return (
    <section className="state-panel" role="alert">
      <AlertTriangle size={28} aria-hidden="true" />
      <h2>Dashboard data unavailable</h2>
      <p>
        The dashboard could not reach the mock FastAPI backend at{" "}
        <code>{API_BASE_URL}</code>. Start the backend and try again.
      </p>
      <span>{message}</span>
      <button className="refresh-button" type="button" onClick={onRetry}>
        <RefreshCw size={18} aria-hidden="true" />
        Retry
      </button>
    </section>
  );
}

function EmptyState({ message }: { message: string }) {
  return (
    <div className="empty-state">
      <ShieldCheck size={22} aria-hidden="true" />
      <span>{message}</span>
    </div>
  );
}

function TableLoading({ rows }: { rows: number }) {
  return (
    <div className="loading-rows" aria-label="Loading table data">
      {Array.from({ length: rows }).map((_, index) => (
        <div className="loading-row" key={index}>
          <div className="skeleton" />
          <div className="skeleton" />
          <div className="skeleton" />
        </div>
      ))}
    </div>
  );
}

function formatTimestamp(value: string) {
  return new Intl.DateTimeFormat("en", {
    dateStyle: "medium",
    timeStyle: "short"
  }).format(new Date(value));
}
