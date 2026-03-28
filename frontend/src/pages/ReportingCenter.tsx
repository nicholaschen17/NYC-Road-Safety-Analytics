import { useState } from "react";

const FORMATS = ["CSV", "JSON", "GeoJSON", "Parquet"] as const;

export default function ReportingCenter() {
  const [format, setFormat] = useState<(typeof FORMATS)[number]>("CSV");

  return (
    <div className="reporting-page">
      <div className="topbar">
        <div>
          <div className="topbar-title">Reporting &amp; export center</div>
          <div className="topbar-sub">
            Scheduled reports · ad-hoc exports · delivery management
          </div>
        </div>
        <button type="button" className="act-btn primary">
          Generate report ↗
        </button>
      </div>

      <div className="reporting-body">
        <div className="three-col">
          <div className="card">
            <div className="card-header">
              Executive summary <span className="badge badge-success">Scheduled</span>
            </div>
            <div className="tpl-card">
              <div
                className="tpl-icon"
                style={{ background: "var(--color-background-info)" }}
              >
                <svg width={16} height={16} viewBox="0 0 16 16" fill="none" aria-hidden>
                  <rect
                    x={2}
                    y={2}
                    width={12}
                    height={3}
                    rx={1}
                    fill="var(--color-text-info)"
                  />
                  <rect
                    x={2}
                    y={7}
                    width={8}
                    height={1.5}
                    rx={0.75}
                    fill="var(--color-text-info)"
                    opacity={0.6}
                  />
                  <rect
                    x={2}
                    y={10}
                    width={10}
                    height={1.5}
                    rx={0.75}
                    fill="var(--color-text-info)"
                    opacity={0.6}
                  />
                  <rect
                    x={2}
                    y={13}
                    width={6}
                    height={1.5}
                    rx={0.75}
                    fill="var(--color-text-info)"
                    opacity={0.4}
                  />
                </svg>
              </div>
              <div className="tpl-name">Weekly executive brief</div>
              <div className="tpl-desc">
                Top 10 hotspots, borough-level summary, model accuracy, crash
                trend vs prior week. PDF format.
              </div>
              <div className="tpl-footer">
                <span className="tpl-cadence">Every Monday 07:00</span>
                <button type="button" className="act-btn">
                  Run now
                </button>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              Borough operations{" "}
              <span className="badge badge-success">Scheduled</span>
            </div>
            <div className="tpl-card">
              <div
                className="tpl-icon"
                style={{ background: "var(--color-background-warning)" }}
              >
                <svg width={16} height={16} viewBox="0 0 16 16" fill="none" aria-hidden>
                  <circle
                    cx={8}
                    cy={8}
                    r={5.5}
                    stroke="var(--color-text-warning)"
                    strokeWidth={1.5}
                    fill="none"
                  />
                  <path
                    d="M8 5v3.5l2 1.5"
                    stroke="var(--color-text-warning)"
                    strokeWidth={1.2}
                    strokeLinecap="round"
                    fill="none"
                  />
                </svg>
              </div>
              <div className="tpl-name">Daily ops briefing</div>
              <div className="tpl-desc">
                High-risk zones for next 24h, active alerts, weather
                interaction flags. Sent to borough ops leads.
              </div>
              <div className="tpl-footer">
                <span className="tpl-cadence">Daily 06:30 · all boroughs</span>
                <button type="button" className="act-btn">
                  Run now
                </button>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              Model performance{" "}
              <span className="badge badge-info">Monthly</span>
            </div>
            <div className="tpl-card">
              <div
                className="tpl-icon"
                style={{ background: "var(--color-background-success)" }}
              >
                <svg width={16} height={16} viewBox="0 0 16 16" fill="none" aria-hidden>
                  <polyline
                    points="2,12 6,8 9,10 14,4"
                    stroke="var(--color-text-success)"
                    strokeWidth={1.5}
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    fill="none"
                  />
                </svg>
              </div>
              <div className="tpl-name">Monthly model report</div>
              <div className="tpl-desc">
                Precision, recall, AUC drift, SHAP analysis, training history,
                and retrain recommendations.
              </div>
              <div className="tpl-footer">
                <span className="tpl-cadence">1st of month · ML team</span>
                <button type="button" className="act-btn">
                  Run now
                </button>
              </div>
            </div>
          </div>
        </div>

        <div className="two-col">
          <div className="card">
            <div className="card-header">Recent report runs</div>
            {[
              {
                name: "Weekly executive brief",
                meta: "Mar 17 07:01 · PDF · 3 recipients",
                status: "Delivered" as const,
              },
              {
                name: "Daily ops briefing · Brooklyn",
                meta: "Mar 22 06:31 · PDF · 2 recipients",
                status: "Delivered" as const,
              },
              {
                name: "Ad-hoc zone export · Grid 4812",
                meta: "Mar 20 14:12 · CSV · manual run",
                status: "Delivered" as const,
              },
              {
                name: "Monthly model report",
                meta: "Mar 1 08:00 · PDF · ML team",
                status: "Delivered" as const,
              },
              {
                name: "Weekly executive brief",
                meta: "Mar 10 07:01 · PDF · failed SMTP",
                status: "Failed" as const,
              },
            ].map((run) => (
              <div key={run.name + run.meta} className="run-row">
                <div style={{ flex: 1, minWidth: 160 }}>
                  <div className="run-name">{run.name}</div>
                  <div className="run-meta">{run.meta}</div>
                </div>
                <span
                  className={`badge ${run.status === "Delivered" ? "badge-success" : "badge-warning"}`}
                >
                  {run.status}
                </span>
                <button type="button" className="act-btn">
                  {run.status === "Failed" ? "Retry" : "Download"}
                </button>
              </div>
            ))}
          </div>

          <div className="card">
            <div className="card-header">Ad-hoc export</div>
            <div className="sched-form">
              <div className="form-row">
                <span className="form-label">Dataset</span>
                <select className="form-input" aria-label="Dataset">
                  <option>gold.crash_features</option>
                  <option>gold.env_features</option>
                  <option>silver.crashes</option>
                  <option>Risk score output (all zones)</option>
                  <option>Incident explorer (filtered view)</option>
                </select>
              </div>
              <div className="form-row">
                <span className="form-label">Date range</span>
                <input
                  className="form-input"
                  type="text"
                  defaultValue="Mar 1 – Mar 22, 2026"
                  aria-label="Date range"
                />
              </div>
              <div className="form-row">
                <span className="form-label">Filter by</span>
                <select className="form-input" aria-label="Borough filter">
                  <option>All boroughs</option>
                  <option>Brooklyn</option>
                  <option>Manhattan</option>
                  <option>Queens</option>
                </select>
              </div>
              <div className="form-row">
                <span className="form-label">Format</span>
                <div className="fmt-pills">
                  {FORMATS.map((f) => (
                    <button
                      key={f}
                      type="button"
                      className={`fmt-pill${format === f ? " active" : ""}`}
                      onClick={() => setFormat(f)}
                    >
                      {f}
                    </button>
                  ))}
                </div>
              </div>
              <div className="divider" />
              <div style={{ display: "flex", gap: 8 }}>
                <button type="button" className="act-btn primary" style={{ flex: 1 }}>
                  Export now ↗
                </button>
                <button type="button" className="act-btn" style={{ flex: 1 }}>
                  Schedule delivery
                </button>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            Data delivery targets{" "}
            <span className="card-sub">where reports are sent</span>
          </div>
          <div className="export-row">
            <div>
              <div className="export-label" style={{ fontWeight: 500 }}>
                Email · DOT leadership
              </div>
              <div className="export-desc">
                commissioner@dot.nyc.gov, deputy@dot.nyc.gov · weekly executive
                brief
              </div>
            </div>
            <span className="badge badge-success">Active</span>
            <button type="button" className="act-btn">
              Edit
            </button>
          </div>
          <div className="export-row">
            <div>
              <div className="export-label" style={{ fontWeight: 500 }}>
                Email · Borough ops leads
              </div>
              <div className="export-desc">
                5 recipients · daily ops briefing · 06:30
              </div>
            </div>
            <span className="badge badge-success">Active</span>
            <button type="button" className="act-btn">
              Edit
            </button>
          </div>
          <div className="export-row">
            <div>
              <div className="export-label" style={{ fontWeight: 500 }}>
                S3 bucket · data warehouse
              </div>
              <div className="export-desc">
                s3://nyc-crash-intelligence/exports/ · Parquet · daily gold
                snapshot
              </div>
            </div>
            <span className="badge badge-success">Active</span>
            <button type="button" className="act-btn">
              Edit
            </button>
          </div>
          <div className="export-row">
            <div>
              <div className="export-label" style={{ fontWeight: 500 }}>
                REST webhook · field ops app
              </div>
              <div className="export-desc">
                GeoJSON risk scores · pushed every 6h · /api/v1/hotspots
              </div>
            </div>
            <span className="badge badge-warning">Degraded</span>
            <button type="button" className="act-btn">
              Diagnose
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
