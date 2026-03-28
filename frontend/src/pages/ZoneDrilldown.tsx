import { Link, useParams } from "react-router-dom";

export default function ZoneDrilldown() {
  const { gridId = "4812" } = useParams<{ gridId: string }>();
  const label =
    gridId === "4812"
      ? "Atlantic Ave / 4th Ave"
      : `Zone ${gridId}`;

  return (
    <div className="zone-page">
      <div className="topbar">
        <Link className="back-btn" to="/">
          ← Dashboard
        </Link>
        <div style={{ flex: 1, minWidth: 200 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
            <span className="zone-id">
              Grid {gridId} · {label}
            </span>
            <span className="badge badge-danger">High risk</span>
            <span className="badge badge-info">Active alert</span>
          </div>
          <div className="zone-sub">
            Brooklyn · District 14 · 500m × 500m · Updated 06:00 today
          </div>
        </div>
        <div className="zone-top-actions">
          <button type="button" className="act-btn">
            Recommend intervention ↗
          </button>
          <button type="button" className="act-btn primary">
            Export zone report
          </button>
        </div>
      </div>

      <div className="zone-body">
        <div className="left-col">
          <div className="card">
            <div className="metric-grid">
              <div className="metric-cell">
                <div className="metric-label">Risk score</div>
                <div
                  className="metric-val"
                  style={{ color: "var(--color-text-danger)" }}
                >
                  0.91
                </div>
                <div className="metric-sub" style={{ color: "var(--color-text-danger)" }}>
                  ↑ 0.08 vs last week
                </div>
              </div>
              <div className="metric-cell">
                <div className="metric-label">Crashes (30d)</div>
                <div className="metric-val">47</div>
                <div className="metric-sub" style={{ color: "var(--color-text-danger)" }}>
                  ↑ 12 vs prior 30d
                </div>
              </div>
              <div className="metric-cell">
                <div className="metric-label">Injuries (30d)</div>
                <div className="metric-val">9</div>
                <div className="metric-sub" style={{ color: "var(--color-text-danger)" }}>
                  ↑ 3 vs prior 30d
                </div>
              </div>
              <div className="metric-cell">
                <div className="metric-label">Fatalities (30d)</div>
                <div className="metric-val">1</div>
                <div
                  className="metric-sub"
                  style={{ color: "var(--color-text-secondary)" }}
                >
                  Same as prior 30d
                </div>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              Zone mini-map <span className="card-sub">500m grid cell</span>
            </div>
            <div className="map-placeholder">
              <svg width="100%" height="100%" viewBox="0 0 300 200">
                <defs>
                  <pattern
                    id="g2"
                    width={20}
                    height={20}
                    patternUnits="userSpaceOnUse"
                  >
                    <path
                      d="M20 0L0 0 0 20"
                      fill="none"
                      stroke="#888"
                      strokeWidth={0.3}
                      opacity={0.3}
                    />
                  </pattern>
                </defs>
                <rect width={300} height={200} fill="#e8e4dc" />
                <rect width={300} height={200} fill="url(#g2)" />
                <rect
                  x={95}
                  y={60}
                  width={110}
                  height={80}
                  fill="#E24B4A"
                  opacity={0.25}
                  rx={3}
                />
                <rect
                  x={95}
                  y={60}
                  width={110}
                  height={80}
                  fill="none"
                  stroke="#E24B4A"
                  strokeWidth={1.5}
                  rx={3}
                />
                <line
                  x1={0}
                  y1={100}
                  x2={300}
                  y2={100}
                  stroke="#555"
                  strokeWidth={1.5}
                  opacity={0.5}
                />
                <line
                  x1={150}
                  y1={0}
                  x2={150}
                  y2={200}
                  stroke="#555"
                  strokeWidth={1}
                  opacity={0.3}
                />
                <line
                  x1={0}
                  y1={60}
                  x2={300}
                  y2={60}
                  stroke="#555"
                  strokeWidth={1}
                  opacity={0.3}
                />
                <text
                  x={100}
                  y={95}
                  fontSize={10}
                  fill="#A32D2D"
                  fontFamily="sans-serif"
                >
                  Grid {gridId}
                </text>
                <circle cx={130} cy={110} r={4} fill="#E24B4A" opacity={0.8} />
                <circle cx={155} cy={90} r={3} fill="#E24B4A" opacity={0.8} />
                <circle cx={175} cy={115} r={4} fill="#EF9F27" opacity={0.8} />
                <circle cx={145} cy={125} r={3} fill="#E24B4A" opacity={0.8} />
                <circle cx={120} cy={80} r={2.5} fill="#EF9F27" opacity={0.8} />
                <text x={8} y={194} fontSize={9} fill="#888" fontFamily="sans-serif">
                  Atlantic Ave
                </text>
                <text x={8} y={55} fontSize={9} fill="#888" fontFamily="sans-serif">
                  4th Ave
                </text>
              </svg>
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              Crash breakdown <span className="card-sub">last 30 days</span>
            </div>
            <div style={{ padding: "10px 12px 6px" }}>
              <div
                style={{
                  fontSize: 11,
                  color: "var(--color-text-secondary)",
                  marginBottom: 6,
                }}
              >
                By type
              </div>
              <div className="bar-stack" style={{ marginBottom: 4 }}>
                <div className="bar-seg" style={{ width: "38%", background: "#E24B4A" }} />
                <div className="bar-seg" style={{ width: "27%", background: "#EF9F27" }} />
                <div className="bar-seg" style={{ width: "20%", background: "#378ADD" }} />
                <div className="bar-seg" style={{ width: "15%", background: "#888780" }} />
              </div>
              <div
                style={{
                  display: "flex",
                  gap: 12,
                  fontSize: 11,
                  color: "var(--color-text-secondary)",
                  marginBottom: 10,
                  flexWrap: "wrap",
                }}
              >
                <span>
                  <span
                    style={{
                      display: "inline-block",
                      width: 8,
                      height: 8,
                      borderRadius: "50%",
                      background: "#E24B4A",
                      marginRight: 3,
                    }}
                  />
                  Rear-end 38%
                </span>
                <span>
                  <span
                    style={{
                      display: "inline-block",
                      width: 8,
                      height: 8,
                      borderRadius: "50%",
                      background: "#EF9F27",
                      marginRight: 3,
                    }}
                  />
                  Angle 27%
                </span>
                <span>
                  <span
                    style={{
                      display: "inline-block",
                      width: 8,
                      height: 8,
                      borderRadius: "50%",
                      background: "#378ADD",
                      marginRight: 3,
                    }}
                  />
                  Sideswipe 20%
                </span>
                <span>
                  <span
                    style={{
                      display: "inline-block",
                      width: 8,
                      height: 8,
                      borderRadius: "50%",
                      background: "#888780",
                      marginRight: 3,
                    }}
                  />
                  Other 15%
                </span>
              </div>
              <div
                style={{
                  fontSize: 11,
                  color: "var(--color-text-secondary)",
                  marginBottom: 5,
                }}
              >
                By time of day
              </div>
              <div className="timeline-row">
                {[
                  20, 15, 12, 18, 45, 70, 55, 40, 30, 35, 80, 65,
                ].map((pct, i) => (
                  <div
                    key={i}
                    className="t-bar"
                    style={{
                      height: `${pct}%`,
                      background:
                        pct >= 55 ? "#E24B4A" : pct >= 35 ? "#EF9F27" : "var(--color-border-secondary)",
                    }}
                  />
                ))}
              </div>
              <div className="t-labels">
                <span>12am</span>
                <span>4am</span>
                <span>8am</span>
                <span>12pm</span>
                <span>4pm</span>
                <span>8pm</span>
              </div>
            </div>
          </div>
        </div>

        <div className="right-col">
          <div className="card">
            <div className="card-header">
              Model feature contributions{" "}
              <span className="card-sub">SHAP values · this zone</span>
            </div>
            {(
              [
                {
                  name: "Crash rate 30d (rolling)",
                  w: "91%",
                  c: "#E24B4A",
                  v: "0.41",
                  vc: "var(--color-text-danger)",
                },
                {
                  name: "Peak hour traffic volume",
                  w: "68%",
                  c: "#EF9F27",
                  v: "0.28",
                  vc: "var(--color-text-warning)",
                },
                {
                  name: "Wet road probability",
                  w: "44%",
                  c: "#378ADD",
                  v: "0.18",
                  vc: "var(--color-text-info)",
                },
                {
                  name: "Moving violations density",
                  w: "32%",
                  c: "#EF9F27",
                  v: "0.13",
                  vc: "var(--color-text-warning)",
                },
                { name: "Street rating (poor)", w: "20%", c: "#888780", v: "0.08" },
                { name: "No speed hump present", w: "12%", c: "#888780", v: "0.05" },
                { name: "Distance to bike route", w: "8%", c: "#888780", v: "0.03" },
              ] as const
            ).map((f) => (
              <div key={f.name} className="feat-row">
                <span className="feat-name">{f.name}</span>
                <div className="feat-bar-wrap">
                  <div
                    className="feat-bar"
                    style={{ width: f.w, background: f.c }}
                  />
                </div>
                <span
                  className="feat-val"
                  style={"vc" in f ? { color: f.vc } : undefined}
                >
                  {f.v}
                </span>
              </div>
            ))}
          </div>

          <div className="card">
            <div className="card-header">
              Recent incidents <span className="card-sub">last 14 days</span>
            </div>
            <table className="tbl">
              <thead>
                <tr>
                  <th style={{ width: 70 }}>Date</th>
                  <th>Type</th>
                  <th style={{ width: 60 }}>Severity</th>
                  <th style={{ width: 55 }}>Injuries</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Mar 20</td>
                  <td>Rear-end · Atlantic/4th</td>
                  <td>
                    <span className="badge badge-danger">Fatal</span>
                  </td>
                  <td>2</td>
                </tr>
                <tr>
                  <td>Mar 18</td>
                  <td>Angle collision · 4th/Dean</td>
                  <td>
                    <span className="badge badge-danger">Injury</span>
                  </td>
                  <td>1</td>
                </tr>
                <tr>
                  <td>Mar 17</td>
                  <td>Sideswipe · Atlantic Ave</td>
                  <td>
                    <span className="badge badge-warning">Minor</span>
                  </td>
                  <td>0</td>
                </tr>
                <tr>
                  <td>Mar 15</td>
                  <td>Rear-end · 4th/Pacific</td>
                  <td>
                    <span className="badge badge-warning">Minor</span>
                  </td>
                  <td>1</td>
                </tr>
                <tr>
                  <td>Mar 12</td>
                  <td>Pedestrian · Atlantic Ave</td>
                  <td>
                    <span className="badge badge-danger">Injury</span>
                  </td>
                  <td>1</td>
                </tr>
                <tr>
                  <td>Mar 10</td>
                  <td>Angle collision · 4th Ave</td>
                  <td>
                    <span className="badge badge-warning">Minor</span>
                  </td>
                  <td>0</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div className="card">
            <div className="card-header">
              Infrastructure context{" "}
              <span className="card-sub">from silver layer</span>
            </div>
            <table className="tbl">
              <tbody>
                <tr>
                  <td
                    style={{
                      color: "var(--color-text-secondary)",
                      width: "50%",
                    }}
                  >
                    Street rating
                  </td>
                  <td>
                    <span className="badge badge-danger">Poor (2/10)</span>
                  </td>
                </tr>
                <tr>
                  <td style={{ color: "var(--color-text-secondary)" }}>
                    Speed limit
                  </td>
                  <td>30 mph</td>
                </tr>
                <tr>
                  <td style={{ color: "var(--color-text-secondary)" }}>
                    Speed humps
                  </td>
                  <td>None in zone</td>
                </tr>
                <tr>
                  <td style={{ color: "var(--color-text-secondary)" }}>
                    Bike route proximity
                  </td>
                  <td>480m (outside zone)</td>
                </tr>
                <tr>
                  <td style={{ color: "var(--color-text-secondary)" }}>
                    Last salt treatment
                  </td>
                  <td>Mar 14 (8 days ago)</td>
                </tr>
                <tr>
                  <td style={{ color: "var(--color-text-secondary)" }}>
                    Traffic volume (daily avg)
                  </td>
                  <td>18,400 vehicles</td>
                </tr>
              </tbody>
            </table>
            <div className="action-row">
              <button type="button" className="act-btn" style={{ flex: 1 }}>
                Suggest improvements ↗
              </button>
              <button type="button" className="act-btn" style={{ flex: 1 }}>
                Compare to similar zones ↗
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
