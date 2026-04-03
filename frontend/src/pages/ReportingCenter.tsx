import { useState } from "react";
import { buildExportUrl } from "../api/client";

const FORMATS = ["csv", "json"] as const;
type ExportFormat = (typeof FORMATS)[number];

const DATASETS = [
  { value: "gold.crash_features", label: "gold.crash_features" },
  { value: "gold.env_features", label: "gold.env_features" },
  { value: "gold.traffic_features", label: "gold.traffic_features" },
  { value: "gold.spatial_features", label: "gold.spatial_features" },
  { value: "silver.crashes", label: "silver.crashes (incidents)" },
] as const;

const BOROUGHS = ["All boroughs", "Brooklyn", "Manhattan", "Queens", "Bronx", "Staten Island"];

export default function ReportingCenter() {
  const [format, setFormat] = useState<ExportFormat>("csv");
  const [dataset, setDataset] = useState<string>("gold.crash_features");
  const [borough, setBorough] = useState<string>("All boroughs");

  const exportUrl = buildExportUrl({
    dataset,
    format,
    borough: borough === "All boroughs" ? undefined : borough,
  });

  return (
    <div className="reporting-page">
      <div className="topbar">
        <div>
          <div className="topbar-title">Reporting &amp; export center</div>
          <div className="topbar-sub">
            Scheduled reports · ad-hoc exports · delivery management
          </div>
        </div>
        <a href={exportUrl} className="act-btn primary" download>
          Generate report ↗
        </a>
      </div>

      <div className="reporting-body">
        <div className="three-col">
          <div className="card">
            <div className="card-header">
              Executive summary <span className="badge badge-success">Scheduled</span>
            </div>
            <div className="tpl-card">
              <div className="tpl-icon" style={{ background: "var(--color-background-info)" }}>
                <svg width={16} height={16} viewBox="0 0 16 16" fill="none" aria-hidden>
                  <rect x={2} y={2} width={12} height={3} rx={1} fill="var(--color-text-info)" />
                  <rect x={2} y={7} width={8} height={1.5} rx={0.75} fill="var(--color-text-info)" opacity={0.6} />
                  <rect x={2} y={10} width={10} height={1.5} rx={0.75} fill="var(--color-text-info)" opacity={0.6} />
                  <rect x={2} y={13} width={6} height={1.5} rx={0.75} fill="var(--color-text-info)" opacity={0.4} />
                </svg>
              </div>
              <div className="tpl-name">Weekly executive brief</div>
              <div className="tpl-desc">
                Top 10 hotspots, borough-level summary, model accuracy, crash
                trend vs prior week. CSV format from gold.crash_features.
              </div>
              <div className="tpl-footer">
                <span className="tpl-cadence">Every Monday 07:00</span>
                <a
                  href={buildExportUrl({ dataset: "gold.crash_features", format: "csv" })}
                  className="act-btn"
                  download
                >
                  Run now
                </a>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              Borough operations{" "}
              <span className="badge badge-success">Scheduled</span>
            </div>
            <div className="tpl-card">
              <div className="tpl-icon" style={{ background: "var(--color-background-warning)" }}>
                <svg width={16} height={16} viewBox="0 0 16 16" fill="none" aria-hidden>
                  <circle cx={8} cy={8} r={5.5} stroke="var(--color-text-warning)" strokeWidth={1.5} fill="none" />
                  <path d="M8 5v3.5l2 1.5" stroke="var(--color-text-warning)" strokeWidth={1.2} strokeLinecap="round" fill="none" />
                </svg>
              </div>
              <div className="tpl-name">Daily ops briefing</div>
              <div className="tpl-desc">
                High-risk zones for next 24h, active alerts, weather
                interaction flags. Powered by gold.env_features.
              </div>
              <div className="tpl-footer">
                <span className="tpl-cadence">Daily 06:30 · all boroughs</span>
                <a
                  href={buildExportUrl({ dataset: "gold.env_features", format: "csv" })}
                  className="act-btn"
                  download
                >
                  Run now
                </a>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              Model performance{" "}
              <span className="badge badge-info">Monthly</span>
            </div>
            <div className="tpl-card">
              <div className="tpl-icon" style={{ background: "var(--color-background-success)" }}>
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
                and retrain recommendations. All gold features exported.
              </div>
              <div className="tpl-footer">
                <span className="tpl-cadence">1st of month · ML team</span>
                <a
                  href={buildExportUrl({ dataset: "gold.spatial_features", format: "json" })}
                  className="act-btn"
                  download
                >
                  Run now
                </a>
              </div>
            </div>
          </div>
        </div>

        <div className="two-col">
          <div className="card">
            <div className="card-header">Recent report runs</div>
            {[
              { name: "gold.crash_features export", meta: "Latest data · CSV", status: "Available" as const, url: buildExportUrl({ dataset: "gold.crash_features", format: "csv" }) },
              { name: "gold.env_features export", meta: "Latest data · CSV", status: "Available" as const, url: buildExportUrl({ dataset: "gold.env_features", format: "csv" }) },
              { name: "gold.traffic_features export", meta: "Latest data · CSV", status: "Available" as const, url: buildExportUrl({ dataset: "gold.traffic_features", format: "csv" }) },
              { name: "gold.spatial_features export", meta: "Latest data · JSON", status: "Available" as const, url: buildExportUrl({ dataset: "gold.spatial_features", format: "json" }) },
              { name: "silver.crashes export", meta: "Last 10,000 records · CSV", status: "Available" as const, url: buildExportUrl({ dataset: "silver.crashes", format: "csv" }) },
            ].map((run) => (
              <div key={run.name} className="run-row">
                <div style={{ flex: 1, minWidth: 160 }}>
                  <div className="run-name">{run.name}</div>
                  <div className="run-meta">{run.meta}</div>
                </div>
                <span className="badge badge-success">{run.status}</span>
                <a href={run.url} className="act-btn" download>
                  Download
                </a>
              </div>
            ))}
          </div>

          <div className="card">
            <div className="card-header">Ad-hoc export</div>
            <div className="sched-form">
              <div className="form-row">
                <span className="form-label">Dataset</span>
                <select
                  className="form-input"
                  aria-label="Dataset"
                  value={dataset}
                  onChange={(e) => setDataset(e.target.value)}
                >
                  {DATASETS.map((d) => (
                    <option key={d.value} value={d.value}>
                      {d.label}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-row">
                <span className="form-label">Filter by</span>
                <select
                  className="form-input"
                  aria-label="Borough filter"
                  value={borough}
                  onChange={(e) => setBorough(e.target.value)}
                >
                  {BOROUGHS.map((b) => (
                    <option key={b}>{b}</option>
                  ))}
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
                      {f.toUpperCase()}
                    </button>
                  ))}
                </div>
              </div>
              <div className="divider" />
              <div style={{ display: "flex", gap: 8 }}>
                <a
                  href={exportUrl}
                  className="act-btn primary"
                  style={{ flex: 1, textAlign: "center", textDecoration: "none" }}
                  download
                >
                  Export now ↗
                </a>
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
                REST API · gold.crash_features
              </div>
              <div className="export-desc">
                GET /api/v1/hotspots · JSON · real-time zone risk scores
              </div>
            </div>
            <span className="badge badge-success">Active</span>
            <a href="/api/docs" target="_blank" rel="noreferrer" className="act-btn">
              API docs ↗
            </a>
          </div>
          <div className="export-row">
            <div>
              <div className="export-label" style={{ fontWeight: 500 }}>
                REST API · silver.crashes
              </div>
              <div className="export-desc">
                GET /api/v1/crashes · paginated incident records
              </div>
            </div>
            <span className="badge badge-success">Active</span>
            <a href="/api/docs" target="_blank" rel="noreferrer" className="act-btn">
              API docs ↗
            </a>
          </div>
          <div className="export-row">
            <div>
              <div className="export-label" style={{ fontWeight: 500 }}>
                Export · CSV / JSON
              </div>
              <div className="export-desc">
                GET /api/v1/export?dataset=…&amp;format=csv — all gold + silver tables
              </div>
            </div>
            <span className="badge badge-success">Active</span>
            <a href="/api/docs" target="_blank" rel="noreferrer" className="act-btn">
              API docs ↗
            </a>
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
