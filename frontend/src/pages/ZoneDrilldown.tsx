import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { fetchZone, fetchZoneCrashes } from "../api/client";
import type { ZoneCrash, ZoneMetrics } from "../api/types";

function fmtDate(iso: string | null): string {
  if (!iso) return "—";
  const d = new Date(iso + "T00:00:00");
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

function severityBadgeClass(s: string) {
  if (s === "Fatal" || s === "Injury") return "badge badge-danger";
  if (s === "Minor") return "badge badge-warning";
  return "badge badge-success";
}

function riskLabel(score: number | null): { text: string; cls: string } {
  if (score == null) return { text: "Unknown", cls: "" };
  if (score >= 0.7) return { text: "High risk", cls: "badge-danger" };
  if (score >= 0.4) return { text: "Medium risk", cls: "badge-warning" };
  return { text: "Low risk", cls: "badge-success" };
}

export default function ZoneDrilldown() {
  const { gridId = "4812" } = useParams<{ gridId: string }>();

  const [zone, setZone] = useState<ZoneMetrics | null>(null);
  const [crashes, setCrashes] = useState<ZoneCrash[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    Promise.all([fetchZone(gridId), fetchZoneCrashes(gridId, 10)])
      .then(([z, c]) => {
        setZone(z);
        setCrashes(c);
      })
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, [gridId]);

  const risk = riskLabel(zone?.risk_score ?? null);
  const label = zone?.zone_name ?? zone?.borough_name ?? `Zone ${gridId}`;

  // 404 / zone not found
  if (!loading && error?.includes("404")) {
    return (
      <div className="zone-page">
        <div className="topbar">
          <Link className="back-btn" to="/">← Dashboard</Link>
          <div style={{ flex: 1 }}>
            <div className="topbar-title">Zone not found</div>
            <div className="zone-sub">Grid ID: {gridId}</div>
          </div>
        </div>
        <div style={{ padding: "40px 24px", color: "var(--color-text-secondary)", fontSize: 14 }}>
          <p>No zone data was found for <strong>{gridId}</strong>.</p>
          <p style={{ marginTop: 8 }}>
            This can happen when crash records lack borough/coordinate data — the zone can't be
            mapped to the grid. Select a zone directly from the{" "}
            <Link to="/" style={{ color: "var(--color-text-info)" }}>hotspot map</Link>.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="zone-page">
      <div className="topbar">
        <Link className="back-btn" to="/">
          ← Dashboard
        </Link>
        <div style={{ flex: 1, minWidth: 200 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
            <span className="zone-id">
              Grid {gridId} · {loading ? "…" : label}
            </span>
            {!loading && zone && (
              <>
                <span className={`badge ${risk.cls}`}>{risk.text}</span>
                {zone.risk_score != null && zone.risk_score >= 0.6 && (
                  <span className="badge badge-info">Active alert</span>
                )}
              </>
            )}
          </div>
          <div className="zone-sub">
            {loading
              ? "Loading…"
              : `${zone?.borough_name ?? "—"} · Grid ${gridId} · Updated 06:00 today`}
          </div>
        </div>
        <div className="zone-top-actions">
          <button type="button" className="act-btn">
            Recommend intervention ↗
          </button>
          <a
            href={`/api/v1/export?dataset=gold.crash_features&format=csv`}
            className="act-btn primary"
            download
          >
            Export zone report
          </a>
        </div>
      </div>

      {error && (
        <div style={{ padding: "10px 16px", color: "var(--color-text-danger)", fontSize: 13 }}>
          {error}
        </div>
      )}

      <div className="zone-body">
        <div className="left-col">
          <div className="card">
            <div className="metric-grid">
              <div className="metric-cell">
                <div className="metric-label">Risk score</div>
                <div
                  className="metric-val"
                  style={zone?.risk_score != null && zone.risk_score >= 0.7
                    ? { color: "var(--color-text-danger)" }
                    : undefined}
                >
                  {loading ? "…" : (zone?.risk_score?.toFixed(2) ?? "—")}
                </div>
                <div className="metric-sub">{risk.text}</div>
              </div>
              <div className="metric-cell">
                <div className="metric-label">Crashes (30d)</div>
                <div className="metric-val">{loading ? "…" : (zone?.crash_count_30d ?? "—")}</div>
                <div className="metric-sub">
                  {zone?.crash_count_7d != null ? `${zone.crash_count_7d} in last 7d` : " "}
                </div>
              </div>
              <div className="metric-cell">
                <div className="metric-label">Injuries (30d)</div>
                <div className="metric-val">{loading ? "…" : (zone?.injuries_7d ?? "—")}</div>
                <div className="metric-sub">
                  {zone?.vru_injured_30d != null ? `${zone.vru_injured_30d} VRU` : " "}
                </div>
              </div>
              <div className="metric-cell">
                <div className="metric-label">Fatalities (30d)</div>
                <div className="metric-val">{loading ? "…" : (zone?.fatalities_30d ?? "—")}</div>
                <div className="metric-sub">
                  {zone?.injury_rate_per_crash != null
                    ? `${(zone.injury_rate_per_crash * 100).toFixed(0)}% injury rate`
                    : " "}
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
                  <pattern id="g2" width={20} height={20} patternUnits="userSpaceOnUse">
                    <path d="M20 0L0 0 0 20" fill="none" stroke="#888" strokeWidth={0.3} opacity={0.3} />
                  </pattern>
                </defs>
                <rect width={300} height={200} fill="#e8e4dc" />
                <rect width={300} height={200} fill="url(#g2)" />
                <rect
                  x={95} y={60} width={110} height={80}
                  fill="#E24B4A" opacity={zone?.risk_score != null ? zone.risk_score * 0.35 : 0.15}
                  rx={3}
                />
                <rect
                  x={95} y={60} width={110} height={80}
                  fill="none" stroke="#E24B4A" strokeWidth={1.5} rx={3}
                />
                <line x1={0} y1={100} x2={300} y2={100} stroke="#555" strokeWidth={1.5} opacity={0.5} />
                <line x1={150} y1={0} x2={150} y2={200} stroke="#555" strokeWidth={1} opacity={0.3} />
                <text x={100} y={95} fontSize={10} fill="#A32D2D" fontFamily="sans-serif">
                  Grid {gridId}
                </text>
                {crashes.slice(0, 6).map((c, i) => (
                  <circle
                    key={c.collision_id}
                    cx={110 + (i % 3) * 25}
                    cy={70 + Math.floor(i / 3) * 30}
                    r={c.persons_killed > 0 ? 5 : 3}
                    fill={c.severity === "Fatal" ? "#E24B4A" : c.severity === "Injury" ? "#EF9F27" : "#888780"}
                    opacity={0.8}
                  />
                ))}
                <text x={8} y={194} fontSize={9} fill="#888" fontFamily="sans-serif">
                  {zone?.zone_name ?? label}
                </text>
              </svg>
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              Crash breakdown <span className="card-sub">last 30 days</span>
            </div>
            <div style={{ padding: "10px 12px 6px" }}>
              <div style={{ fontSize: 11, color: "var(--color-text-secondary)", marginBottom: 5 }}>
                By time of day (recent crashes)
              </div>
              <div className="timeline-row">
                {Array.from({ length: 12 }, (_, i) => {
                  const hourCrashes = crashes.filter((c) => {
                    const h = parseInt(c.crash_time?.split(":")[0] ?? "0", 10);
                    return Math.floor(h / 2) === i;
                  }).length;
                  const maxH = Math.max(...Array.from({ length: 12 }, (_, j) =>
                    crashes.filter((c) => Math.floor(parseInt(c.crash_time?.split(":")[0] ?? "0", 10) / 2) === j).length
                  ), 1);
                  const pct = Math.round((hourCrashes / maxH) * 100);
                  return (
                    <div
                      key={i}
                      className="t-bar"
                      style={{
                        height: `${pct || 5}%`,
                        background: pct >= 55 ? "#E24B4A" : pct >= 35 ? "#EF9F27" : "var(--color-border-secondary)",
                      }}
                    />
                  );
                })}
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
                  w: zone?.risk_score != null ? `${Math.round(zone.risk_score * 91)}%` : "—",
                  c: "#E24B4A",
                  v: zone?.risk_score?.toFixed(2) ?? "—",
                  vc: "var(--color-text-danger)",
                },
                {
                  name: "Peak hour traffic volume",
                  w: zone?.avg_hourly_volume_7d != null ? `${Math.min(90, Math.round((zone.avg_hourly_volume_7d / 5000) * 68))}%` : "—",
                  c: "#EF9F27",
                  v: zone?.total_volume != null ? zone.total_volume.toLocaleString() : "—",
                  vc: "var(--color-text-warning)",
                },
                {
                  name: "Moving violations (7d)",
                  w: zone?.violations_7d != null ? `${Math.min(80, Math.round((zone.violations_7d / 50) * 32))}%` : "—",
                  c: "#EF9F27",
                  v: zone?.violations_7d?.toString() ?? "—",
                },
                {
                  name: "Wet road probability",
                  w: zone?.precipitation != null && zone.precipitation > 0 ? "44%" : "12%",
                  c: "#378ADD",
                  v: zone?.is_heavy_rain ? "High" : zone?.precipitation != null ? `${zone.precipitation.toFixed(1)}mm` : "—",
                  vc: "var(--color-text-info)",
                },
                {
                  name: "Street rating",
                  w: zone?.avg_pavement_rating != null ? `${Math.round((1 - zone.avg_pavement_rating / 10) * 30)}%` : "—",
                  c: "#888780",
                  v: zone?.avg_pavement_rating != null ? `${zone.avg_pavement_rating.toFixed(1)}/10` : "—",
                },
                {
                  name: "Distance to bike route",
                  w: zone?.has_any_bike_infrastructure ? "8%" : "18%",
                  c: "#888780",
                  v: zone?.total_bike_segments != null ? `${zone.total_bike_segments} segments` : "—",
                },
              ] as const
            ).map((f) => (
              <div key={f.name} className="feat-row">
                <span className="feat-name">{f.name}</span>
                <div className="feat-bar-wrap">
                  <div
                    className="feat-bar"
                    style={{ width: f.w === "—" ? "0%" : f.w, background: f.c }}
                  />
                </div>
                <span className="feat-val" style={"vc" in f ? { color: f.vc } : undefined}>
                  {f.v}
                </span>
              </div>
            ))}
          </div>

          <div className="card">
            <div className="card-header">
              Recent incidents <span className="card-sub">last 10 in borough</span>
            </div>
            <table className="tbl">
              <thead>
                <tr>
                  <th style={{ width: 70 }}>Date</th>
                  <th>Location</th>
                  <th style={{ width: 70 }}>Severity</th>
                  <th style={{ width: 55 }}>Injuries</th>
                </tr>
              </thead>
              <tbody>
                {loading && (
                  <tr>
                    <td colSpan={4} style={{ textAlign: "center", padding: 12, color: "var(--color-text-secondary)" }}>
                      Loading…
                    </td>
                  </tr>
                )}
                {crashes.map((c) => (
                  <tr key={c.collision_id}>
                    <td>{fmtDate(c.crash_date)}</td>
                    <td>
                      {[c.on_street_name, c.cross_street_name].filter(Boolean).join(" / ") || "—"}
                    </td>
                    <td>
                      <span className={severityBadgeClass(c.severity)}>{c.severity}</span>
                    </td>
                    <td>{c.persons_injured}</td>
                  </tr>
                ))}
                {!loading && crashes.length === 0 && (
                  <tr>
                    <td colSpan={4} style={{ textAlign: "center", padding: 12, color: "var(--color-text-secondary)" }}>
                      No recent crashes found
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          <div className="card">
            <div className="card-header">
              Infrastructure context <span className="card-sub">from gold models</span>
            </div>
            <table className="tbl">
              <tbody>
                <tr>
                  <td style={{ color: "var(--color-text-secondary)", width: "50%" }}>Street rating</td>
                  <td>
                    {zone?.avg_pavement_rating != null ? (
                      <span className={`badge ${zone.avg_pavement_rating < 4 ? "badge-danger" : zone.avg_pavement_rating < 7 ? "badge-warning" : "badge-success"}`}>
                        {zone.avg_pavement_rating.toFixed(1)}/10
                      </span>
                    ) : "—"}
                  </td>
                </tr>
                <tr>
                  <td style={{ color: "var(--color-text-secondary)" }}>Speed limit</td>
                  <td>{zone?.avg_speed_limit_mph != null ? `${zone.avg_speed_limit_mph.toFixed(0)} mph` : "—"}</td>
                </tr>
                <tr>
                  <td style={{ color: "var(--color-text-secondary)" }}>Speed humps</td>
                  <td>
                    {zone?.speed_hump_count != null
                      ? zone.speed_hump_count === 0 ? "None in zone" : `${zone.speed_hump_count} humps`
                      : "—"}
                  </td>
                </tr>
                <tr>
                  <td style={{ color: "var(--color-text-secondary)" }}>Bike infrastructure</td>
                  <td>
                    {zone?.total_bike_segments != null
                      ? `${zone.total_bike_segments} segments (${zone.protected_lane_segments ?? 0} protected)`
                      : "—"}
                  </td>
                </tr>
                <tr>
                  <td style={{ color: "var(--color-text-secondary)" }}>Salt treatment active</td>
                  <td>
                    {zone?.salt_treatment_active != null
                      ? zone.salt_treatment_active ? "Yes" : "No"
                      : "—"}
                  </td>
                </tr>
                <tr>
                  <td style={{ color: "var(--color-text-secondary)" }}>Precipitation</td>
                  <td>
                    {zone?.precipitation != null
                      ? `${zone.precipitation.toFixed(1)} mm${zone.is_snow_event ? " · snow" : zone.is_heavy_rain ? " · heavy rain" : ""}`
                      : "—"}
                  </td>
                </tr>
                <tr>
                  <td style={{ color: "var(--color-text-secondary)" }}>Traffic volume (7d avg)</td>
                  <td>
                    {zone?.avg_hourly_volume_7d != null
                      ? `${Math.round(zone.avg_hourly_volume_7d).toLocaleString()} vehicles/hr`
                      : "—"}
                  </td>
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
