import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { fetchHotspotSummary, fetchHotspots, fetchZonesGeoJSON } from "../api/client";
import type { HotspotRow, HotspotSummary, ZoneGeoJSON } from "../api/types";

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

function riskClass(score: number): "risk-high" | "risk-med" | "risk-low" {
  if (score >= 0.7) return "risk-high";
  if (score >= 0.4) return "risk-med";
  return "risk-low";
}

function badgeClass(score: number) {
  if (score >= 0.7) return "badge-danger";
  if (score >= 0.4) return "badge-warning";
  return "badge-success";
}

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

  const [hotspots, setHotspots] = useState<HotspotRow[]>([]);
  const [summary, setSummary] = useState<HotspotSummary | null>(null);
  const [geoZones, setGeoZones] = useState<ZoneGeoJSON[]>([]);
  const [hoveredZone, setHoveredZone] = useState<ZoneGeoJSON | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch geo zones once (static data — doesn't change with borough filter)
  useEffect(() => {
    fetchZonesGeoJSON().then(setGeoZones).catch(() => {});
  }, []);

  useEffect(() => {
    setLoading(true);
    setError(null);
    Promise.all([
      fetchHotspots({ borough: borough !== "All" ? borough : undefined }),
      fetchHotspotSummary(),
    ])
      .then(([hs, sum]) => {
        setHotspots(hs);
        setSummary(sum);
      })
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, [borough]);

  // ── SVG projection helpers ────────────────────────────────────────────────
  const W = 500, H = 400;
  // NYC bounding box with a little padding
  const LON_MIN = -74.26, LON_MAX = -73.69;
  const LAT_MIN = 40.47,  LAT_MAX = 40.93;

  const project = (lon: number, lat: number): [number, number] => [
    ((lon - LON_MIN) / (LON_MAX - LON_MIN)) * W,
    ((LAT_MAX - lat) / (LAT_MAX - LAT_MIN)) * H,
  ];

  const ringToD = (ring: number[][]): string =>
    ring.map(([lon, lat], i) => {
      const [x, y] = project(lon, lat);
      return `${i === 0 ? "M" : "L"}${x.toFixed(1)},${y.toFixed(1)}`;
    }).join(" ") + " Z";

  const zoneToPath = (z: ZoneGeoJSON): string => {
    const geom = z.geometry;
    const rings: number[][][] =
      geom.type === "MultiPolygon"
        ? (geom.coordinates as number[][][][]).flatMap((poly) => poly)
        : (geom.coordinates as unknown as number[][][]);
    return rings.map(ringToD).join(" ");
  };

  const riskFill = (score: number): string => {
    if (score >= 0.7) return "#E24B4A";
    if (score >= 0.4) return "#EF9F27";
    if (score > 0)    return "#639922";
    return "#888780";
  };

  // Merge geo zone risk scores with hotspot filter state
  const visibleGeoZones = useMemo(() => {
    if (borough === "All") return geoZones;
    return geoZones.filter((z) =>
      z.zonename.toLowerCase().includes(borough.toLowerCase()) ||
      (borough === "Brooklyn" && z.zone.startsWith("BK")) ||
      (borough === "Queens" && z.zone.startsWith("Q")) ||
      (borough === "Bronx" && z.zone === "BX") ||
      (borough === "Manhattan" && z.zone === "MN") ||
      (borough === "Staten Island" && z.zone === "SI")
    );
  }, [geoZones, borough]);

  const topZone = hoveredZone ?? (geoZones.length > 0
    ? [...geoZones].sort((a, b) => b.risk_score - a.risk_score)[0]
    : null);

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
              Predicted risk heatmap · NYC DSNY zones
            </span>
            <span className="panel-sub">
              {hoveredZone
                ? `${hoveredZone.zonename} · Risk ${hoveredZone.risk_score.toFixed(2)} · ${hoveredZone.crash_count_7d} crashes 7d`
                : "Hover a zone to inspect"}
            </span>
          </div>
          <div className="map-body">
            {/* Real NYC zone map projected from GeoJSON */}
            <svg
              viewBox={`0 0 ${W} ${H}`}
              preserveAspectRatio="xMidYMid meet"
              style={{ position: "absolute", inset: 0, width: "100%", height: "100%" }}
            >
              <rect width={W} height={H} fill="var(--color-background-secondary, #1a1a1a)" />

              {/* Zone polygons */}
              {geoZones.map((z) => {
                const fill = riskFill(z.risk_score);
                const isHovered = hoveredZone?.grid_cell_id === z.grid_cell_id;
                const isDimmed = borough !== "All" && !visibleGeoZones.includes(z);
                return (
                  <g key={z.grid_cell_id}>
                    <path
                      d={zoneToPath(z)}
                      fill={fill}
                      fillOpacity={isDimmed ? 0.06 : isHovered ? 0.55 : 0.28}
                      stroke={fill}
                      strokeWidth={isHovered ? 1.5 : 0.6}
                      strokeOpacity={isDimmed ? 0.2 : 0.7}
                      style={{ cursor: "pointer", transition: "fill-opacity 0.15s" }}
                      onMouseEnter={() => setHoveredZone(z)}
                      onMouseLeave={() => setHoveredZone(null)}
                    />
                  </g>
                );
              })}

              {/* Centroid labels */}
              {geoZones.map((z) => {
                const [cx, cy] = project(z.centroid_lon, z.centroid_lat);
                const isDimmed = borough !== "All" && !visibleGeoZones.includes(z);
                if (isDimmed) return null;
                return (
                  <g key={`label-${z.grid_cell_id}`} style={{ pointerEvents: "none" }}>
                    <text
                      x={cx}
                      y={cy - 6}
                      textAnchor="middle"
                      fontSize={9}
                      fontFamily="sans-serif"
                      fontWeight={600}
                      fill="#fff"
                      opacity={0.85}
                    >
                      {z.zonename}
                    </text>
                    <text
                      x={cx}
                      y={cy + 7}
                      textAnchor="middle"
                      fontSize={8}
                      fontFamily="sans-serif"
                      fill="#fff"
                      opacity={0.6}
                    >
                      {z.crash_count_7d} crashes 7d
                    </text>
                  </g>
                );
              })}

              {/* Tooltip callout for hovered / top zone */}
              {topZone && (() => {
                const [cx, cy] = project(topZone.centroid_lon, topZone.centroid_lat);
                const bx = Math.min(cx + 10, W - 145);
                const by = Math.max(cy - 70, 4);
                const fill = riskFill(topZone.risk_score);
                return (
                  <g style={{ pointerEvents: "none" }}>
                    <line x1={cx} y1={cy} x2={bx + 4} y2={by + 30} stroke={fill} strokeWidth={1} opacity={0.6} />
                    <rect x={bx} y={by} width={140} height={58} rx={4}
                      fill="var(--color-background-primary, #111)" opacity={0.92}
                      stroke={fill} strokeWidth={0.8}
                    />
                    <text x={bx + 8} y={by + 14} fontSize={9.5} fontWeight={600} fill="#fff" fontFamily="sans-serif">
                      {topZone.zonename}
                    </text>
                    <text x={bx + 8} y={by + 27} fontSize={8.5} fill="#aaa" fontFamily="sans-serif">
                      Risk score{" "}
                      <tspan fill={fill} fontWeight={600}>{topZone.risk_score.toFixed(2)}</tspan>
                    </text>
                    <text x={bx + 8} y={by + 40} fontSize={8.5} fill="#aaa" fontFamily="sans-serif">
                      Crashes 7d: {topZone.crash_count_7d}
                    </text>
                    <text x={bx + 8} y={by + 52} fontSize={8.5} fill="#aaa" fontFamily="sans-serif">
                      Injuries 7d: {topZone.injuries_7d}
                    </text>
                  </g>
                );
              })()}
            </svg>

            {/* Click-through link for top / hovered zone */}
            {topZone && (
              <Link
                to={`/zones/${topZone.grid_cell_id}`}
                style={{
                  position: "absolute",
                  bottom: 42,
                  right: 10,
                  background: "var(--color-background-primary)",
                  border: "0.5px solid var(--color-border-secondary)",
                  borderRadius: "var(--border-radius-md)",
                  padding: "5px 10px",
                  fontSize: 11,
                  textDecoration: "none",
                  color: "inherit",
                  opacity: 0.9,
                }}
              >
                Open zone detail ↗
              </Link>
            )}

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
              <div className="metric-val">
                {loading ? "…" : (summary?.high_risk_zones ?? "—")}
              </div>
              <div className="metric-sub">
                {summary ? `of ${summary.active_zones} active zones` : " "}
              </div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Crashes (7d)</div>
              <div className="metric-val">
                {loading ? "…" : (summary?.total_crashes_7d ?? "—")}
              </div>
              <div className="metric-sub">
                {summary ? `${summary.total_injuries_7d} injuries` : " "}
              </div>
            </div>
          </div>
          <div className="metric-row">
            <div className="metric-card">
              <div className="metric-label">Fatalities (30d)</div>
              <div className="metric-val">
                {loading ? "…" : (summary?.total_fatalities_30d ?? "—")}
              </div>
              <div className="metric-sub">
                {summary ? `${summary.total_vru_injured_30d} VRU injured` : " "}
              </div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Model accuracy</div>
              <div className="metric-val">84%</div>
              <div className="metric-sub">Precision @ 0.5</div>
            </div>
          </div>

          {error && (
            <div style={{ padding: "8px 12px", color: "var(--color-text-danger)", fontSize: 12 }}>
              {error}
            </div>
          )}

          <div className="panel">
            <div className="panel-header">
              <span>Top hotspots</span>
              <span className="panel-sub">by predicted risk score</span>
            </div>
            {loading && (
              <div style={{ padding: "12px 14px", color: "var(--color-text-secondary)", fontSize: 12 }}>
                Loading…
              </div>
            )}
            {hotspots.map((h, i) => (
              <Link
                key={h.grid_cell_id}
                className="hotspot-row"
                to={`/zones/${h.grid_cell_id}`}
              >
                <span className="hs-rank">{i + 1}</span>
                <div style={{ flex: 1 }}>
                  <div className="hs-name">
                    {h.zone_name ?? `Grid ${h.grid_cell_id}`}
                  </div>
                  <div className="hs-zone">
                    {h.borough_name ?? "—"} · Zone {h.grid_cell_id}
                  </div>
                </div>
                <div className="risk-bar-wrap">
                  <div
                    className={`risk-bar ${riskClass(h.risk_score)}`}
                    style={{ width: `${Math.round(h.risk_score * 100)}%` }}
                  />
                </div>
                <span className={`badge ${badgeClass(h.risk_score)}`}>
                  {h.risk_score.toFixed(2)}
                </span>
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
            <span style={{ fontSize: 11, color: "var(--color-text-secondary)" }}>
              Active model
            </span>
            <span className="pill active" style={{ fontSize: 11, cursor: "default" }}>
              XGBoost v2.1
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
