import { useState } from "react";
import { Link } from "react-router-dom";

const MODES = ["Live risk", "Historical", "Forecast 24h"] as const;
const BOROUGHS = [
  "All",
  "Manhattan",
  "Brooklyn",
  "Queens",
  "Bronx",
  "Staten Island",
] as const;
const WINDOWS = ["7 days", "30 days", "90 days"] as const;
const CONDITIONS = ["Wet road", "Snow/ice", "Peak hours"] as const;

const HOTSPOTS = [
  {
    rank: 1,
    name: "Atlantic Ave / 4th Ave",
    zone: "Brooklyn · Zone 14",
    gridId: "4812",
    width: 90,
    riskClass: "risk-high" as const,
    badgeClass: "badge-danger" as const,
    score: "0.91",
  },
  {
    rank: 2,
    name: "Queens Blvd / Union Tpk",
    zone: "Queens · Zone 27",
    gridId: "4827",
    width: 85,
    riskClass: "risk-high" as const,
    badgeClass: "badge-danger" as const,
    score: "0.87",
  },
  {
    rank: 3,
    name: "Grand Concourse / 161st",
    zone: "Bronx · Zone 8",
    gridId: "4808",
    width: 78,
    riskClass: "risk-high" as const,
    badgeClass: "badge-danger" as const,
    score: "0.81",
  },
  {
    rank: 4,
    name: "34th St / 8th Ave",
    zone: "Manhattan · Zone 3",
    gridId: "4803",
    width: 64,
    riskClass: "risk-med" as const,
    badgeClass: "badge-warning" as const,
    score: "0.67",
  },
  {
    rank: 5,
    name: "Hylan Blvd / Richmond",
    zone: "Staten Is · Zone 2",
    gridId: "4802",
    width: 55,
    riskClass: "risk-med" as const,
    badgeClass: "badge-warning" as const,
    score: "0.58",
  },
];

function toggleInSet<T extends string>(set: Set<T>, key: T): Set<T> {
  const next = new Set(set);
  if (next.has(key)) next.delete(key);
  else next.add(key);
  return next;
}

export default function HotspotDashboard() {
  const [mode, setMode] = useState<(typeof MODES)[number]>("Live risk");
  const [borough, setBorough] = useState<(typeof BOROUGHS)[number]>("All");
  const [windowDays, setWindowDays] =
    useState<(typeof WINDOWS)[number]>("7 days");
  const [conditions, setConditions] = useState<Set<string>>(new Set());

  return (
    <div className="hotspot-dash">
      <div className="topbar">
        <div>
          <div className="topbar-title">NYC crash hotspot intelligence</div>
          <div className="topbar-meta">
            Model: XGBoost v2.1 · Last run: today 06:00 · Grid: 500m × 500m
          </div>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          {MODES.map((m) => (
            <button
              key={m}
              type="button"
              className={`pill${mode === m ? " active" : ""}`}
              onClick={() => setMode(m)}
            >
              {m}
            </button>
          ))}
        </div>
      </div>

      <div className="filters">
        <span className="filter-label">Borough</span>
        <div className="pill-group">
          {BOROUGHS.map((b) => (
            <button
              key={b}
              type="button"
              className={`pill${borough === b ? " active" : ""}`}
              onClick={() => setBorough(b)}
            >
              {b}
            </button>
          ))}
        </div>
        <span style={{ marginLeft: 8 }} className="filter-label">
          Time window
        </span>
        <div className="pill-group">
          {WINDOWS.map((w) => (
            <button
              key={w}
              type="button"
              className={`pill${windowDays === w ? " active" : ""}`}
              onClick={() => setWindowDays(w)}
            >
              {w}
            </button>
          ))}
        </div>
        <span style={{ marginLeft: 8 }} className="filter-label">
          Conditions
        </span>
        <div className="pill-group">
          {CONDITIONS.map((c) => (
            <button
              key={c}
              type="button"
              className={`pill${conditions.has(c) ? " active" : ""}`}
              onClick={() =>
                setConditions((prev) => toggleInSet(prev, c as string))
              }
            >
              {c}
            </button>
          ))}
        </div>
      </div>

      <div className="dash-body">
        <div className="map-panel">
          <div className="map-header">
            <span className="map-header-title">
              Predicted risk heatmap · NYC grid
            </span>
            <span className="panel-sub">Click a cell to inspect features</span>
          </div>
          <div className="map-body">
            <svg
              className="map-grid"
              width="100%"
              height="100%"
              style={{ position: "absolute", inset: 0, opacity: 0.18 }}
            >
              <defs>
                <pattern
                  id="grid"
                  width={24}
                  height={24}
                  patternUnits="userSpaceOnUse"
                >
                  <path
                    d="M 24 0 L 0 0 0 24"
                    fill="none"
                    stroke="#555"
                    strokeWidth={0.5}
                  />
                </pattern>
              </defs>
              <rect width="100%" height="100%" fill="url(#grid)" />
            </svg>
            <svg
              style={{ position: "absolute", inset: 0, width: "100%", height: "100%" }}
              preserveAspectRatio="none"
              viewBox="0 0 400 320"
            >
              <path
                d="M80,60 L180,40 L260,70 L280,140 L220,200 L160,210 L90,170 Z"
                fill="none"
                stroke="#aaa8a0"
                strokeWidth={1}
                opacity={0.5}
              />
              <path
                d="M160,210 L280,140 L340,180 L370,260 L300,310 L210,300 Z"
                fill="none"
                stroke="#aaa8a0"
                strokeWidth={1}
                opacity={0.5}
              />
              <path
                d="M280,140 L400,90 L460,130 L440,200 L370,260 Z"
                fill="none"
                stroke="#aaa8a0"
                strokeWidth={1}
                opacity={0.5}
              />
            </svg>
            <div
              className="heat-dot"
              style={{
                width: 52,
                height: 52,
                background: "radial-gradient(circle,#E24B4A,transparent)",
                top: 80,
                left: 190,
              }}
            />
            <div
              className="heat-dot"
              style={{
                width: 44,
                height: 44,
                background: "radial-gradient(circle,#E24B4A,transparent)",
                top: 130,
                left: 230,
              }}
            />
            <div
              className="heat-dot"
              style={{
                width: 38,
                height: 38,
                background: "radial-gradient(circle,#EF9F27,transparent)",
                top: 55,
                left: 135,
              }}
            />
            <div
              className="heat-dot"
              style={{
                width: 34,
                height: 34,
                background: "radial-gradient(circle,#EF9F27,transparent)",
                top: 170,
                left: 160,
              }}
            />
            <div
              className="heat-dot"
              style={{
                width: 28,
                height: 28,
                background: "radial-gradient(circle,#EF9F27,transparent)",
                top: 200,
                left: 290,
              }}
            />
            <div
              className="heat-dot"
              style={{
                width: 24,
                height: 24,
                background: "radial-gradient(circle,#639922,transparent)",
                top: 250,
                left: 100,
              }}
            />
            <div
              className="heat-dot"
              style={{
                width: 44,
                height: 44,
                background: "radial-gradient(circle,#E24B4A,transparent)",
                top: 60,
                left: 310,
              }}
            />
            <div
              style={{
                position: "absolute",
                top: 82,
                left: 192,
                width: 24,
                height: 24,
                border: "2px solid #E24B4A",
                borderRadius: 3,
                background: "transparent",
              }}
            />
            <Link
              to="/zones/4812"
              style={{
                position: "absolute",
                top: 50,
                left: 218,
                background: "var(--color-background-primary)",
                border: "0.5px solid var(--color-border-secondary)",
                borderRadius: "var(--border-radius-md)",
                padding: "7px 10px",
                fontSize: 11,
                boxShadow: "none",
                minWidth: 130,
                textDecoration: "none",
                color: "inherit",
              }}
            >
              <div
                style={{
                  fontWeight: 500,
                  fontSize: 12,
                  marginBottom: 3,
                }}
              >
                Grid 4812 · Midtown
              </div>
              <div style={{ color: "var(--color-text-secondary)" }}>
                Risk score{" "}
                <span style={{ color: "#E24B4A", fontWeight: 500 }}>0.87</span>
              </div>
              <div style={{ color: "var(--color-text-secondary)" }}>
                Crashes 7d: 12
              </div>
              <div style={{ color: "var(--color-text-secondary)" }}>
                Wet road · peak
              </div>
            </Link>
            <div className="map-legend">
              <div className="legend-row">
                <div className="legend-dot" style={{ background: "#E24B4A" }} />
                High risk
              </div>
              <div className="legend-row">
                <div className="legend-dot" style={{ background: "#EF9F27" }} />
                Medium risk
              </div>
              <div className="legend-row">
                <div className="legend-dot" style={{ background: "#639922" }} />
                Low risk
              </div>
            </div>
          </div>
        </div>

        <div className="right-col">
          <div className="metric-row">
            <div className="metric-card">
              <div className="metric-label">High-risk zones</div>
              <div className="metric-val">38</div>
              <div className="metric-sub metric-up">↑ 4 vs last week</div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Crashes (7d)</div>
              <div className="metric-val">214</div>
              <div className="metric-sub metric-dn">↓ 8 vs last week</div>
            </div>
          </div>
          <div className="metric-row">
            <div className="metric-card">
              <div className="metric-label">Model accuracy</div>
              <div className="metric-val">84%</div>
              <div className="metric-sub">Precision @ 0.5</div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Alert zones</div>
              <div className="metric-val">7</div>
              <div className="metric-sub metric-up">Forecast spike 24h</div>
            </div>
          </div>

          <div className="panel">
            <div className="panel-header">
              <span>Top hotspots</span>
              <span className="panel-sub">by predicted risk score</span>
            </div>
            {HOTSPOTS.map((h) => (
              <Link
                key={h.rank}
                className="hotspot-row"
                to={`/zones/${h.gridId}`}
              >
                <span className="hs-rank">{h.rank}</span>
                <div style={{ flex: 1 }}>
                  <div className="hs-name">{h.name}</div>
                  <div className="hs-zone">{h.zone}</div>
                </div>
                <div className="risk-bar-wrap">
                  <div
                    className={`risk-bar ${h.riskClass}`}
                    style={{ width: `${h.width}%` }}
                  />
                </div>
                <span className={`badge ${h.badgeClass}`}>{h.score}</span>
              </Link>
            ))}
          </div>
        </div>
      </div>

      <div className="bottom-strip">
        <div className="model-stat">
          <div className="model-stat-title">
            Top contributing features (selected cell)
          </div>
          <div className="sparkrow">
            <span className="spark-label">Crash rate 30d</span>
            <svg className="spark-svg" width={70} height={20}>
              <polyline
                points="0,18 14,15 28,10 42,8 56,4 70,2"
                fill="none"
                stroke="#E24B4A"
                strokeWidth={1.5}
              />
            </svg>
            <span style={{ fontSize: 11, fontWeight: 500 }}>0.41</span>
          </div>
          <div className="sparkrow">
            <span className="spark-label">Traffic volume</span>
            <svg className="spark-svg" width={70} height={20}>
              <polyline
                points="0,12 14,8 28,14 42,6 56,10 70,4"
                fill="none"
                stroke="#BA7517"
                strokeWidth={1.5}
              />
            </svg>
            <span style={{ fontSize: 11, fontWeight: 500 }}>0.28</span>
          </div>
          <div className="sparkrow">
            <span className="spark-label">Wet road probability</span>
            <svg className="spark-svg" width={70} height={20}>
              <polyline
                points="0,16 14,14 28,16 42,12 56,10 70,8"
                fill="none"
                stroke="#185FA5"
                strokeWidth={1.5}
              />
            </svg>
            <span style={{ fontSize: 11, fontWeight: 500 }}>0.18</span>
          </div>
          <div className="sparkrow" style={{ borderBottom: "none" }}>
            <span className="spark-label">Moving violations</span>
            <svg className="spark-svg" width={70} height={20}>
              <polyline
                points="0,14 14,16 28,12 42,10 56,12 70,8"
                fill="none"
                stroke="#3B6D11"
                strokeWidth={1.5}
              />
            </svg>
            <span style={{ fontSize: 11, fontWeight: 500 }}>0.13</span>
          </div>
        </div>
        <div className="model-stat">
          <div className="model-stat-title">Model performance · last eval</div>
          <div className="perf-row">
            <span>Precision</span>
            <span className="perf-val">0.84</span>
          </div>
          <div className="perf-row">
            <span>Recall</span>
            <span className="perf-val">0.79</span>
          </div>
          <div className="perf-row">
            <span>AUC-ROC</span>
            <span className="perf-val">0.91</span>
          </div>
          <div className="perf-row">
            <span>F1 score</span>
            <span className="perf-val">0.81</span>
          </div>
          <div
            className="perf-row"
            style={{ marginTop: 8, borderBottom: "none" }}
          >
            <span
              style={{ fontSize: 11, color: "var(--color-text-secondary)" }}
            >
              Active model
            </span>
            <span
              className="pill active"
              style={{ fontSize: 11, cursor: "default" }}
            >
              XGBoost v2.1
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
