import { useEffect, useMemo, useState, type CSSProperties } from "react";
import {
  fetchCrashSummary,
  fetchCrashes,
  fetchDailyBars,
} from "../api/client";
import type {
  CrashPage,
  CrashRow,
  CrashSeverity,
  CrashSummary,
  DailyBar,
} from "../api/types";

const SEVERITY_FILTERS = ["All", "Fatal", "Injury", "Property only"] as const;
const BOROUGHS = ["All", "Manhattan", "Brooklyn", "Queens", "Bronx", "Staten Island"] as const;

function severityBadgeClass(s: CrashSeverity) {
  if (s === "Fatal" || s === "Injury") return "badge badge-danger";
  if (s === "Minor") return "badge badge-warning";
  return "badge badge-success";
}

function riskCellStyle(score: number | null): CSSProperties {
  if (!score) return {};
  if (score >= 0.7) return { color: "var(--color-text-danger)" };
  if (score >= 0.4) return { color: "var(--color-text-warning)" };
  return {};
}

function locationLabel(crash: CrashRow): string {
  const parts = [crash.on_street_name, crash.cross_street_name ?? crash.off_street_name]
    .filter(Boolean)
    .map((s) => s!.trim());
  if (parts.length === 0) return crash.borough ?? "Unknown";
  const boro = crash.borough ? `, ${crash.borough.charAt(0).toUpperCase()}${crash.borough.slice(1).toLowerCase()}` : "";
  return parts.join(" / ") + boro;
}

function formatDate(iso: string | null): string {
  if (!iso) return "—";
  const d = new Date(iso + "T00:00:00");
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

function barColor(d: DailyBar): string {
  if (d.fatalities > 0) return "#E24B4A";
  if (d.injuries > 0) return "#EF9F27";
  return "#888780";
}

export default function IncidentExplorer() {
  const [severity, setSeverity] =
    useState<(typeof SEVERITY_FILTERS)[number]>("All");
  const [borough, setBorough] = useState<(typeof BOROUGHS)[number]>("All");
  const [page, setPage] = useState(1);
  const [selectedId, setSelectedId] = useState<number | null>(null);

  const [crashPage, setCrashPage] = useState<CrashPage | null>(null);
  const [summary, setSummary] = useState<CrashSummary | null>(null);
  const [dailyBars, setDailyBars] = useState<DailyBar[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const PAGE_SIZE = 20;

  useEffect(() => {
    setLoading(true);
    setError(null);
    Promise.all([
      fetchCrashes({
        page,
        page_size: PAGE_SIZE,
        borough: borough !== "All" ? borough : undefined,
        severity: severity !== "All" ? severity : undefined,
      }),
      fetchCrashSummary(borough !== "All" ? borough : undefined),
      fetchDailyBars(30),
    ])
      .then(([cp, sum, bars]) => {
        setCrashPage(cp);
        setSummary(sum);
        setDailyBars(bars);
        if (cp.items.length > 0 && selectedId === null) {
          setSelectedId(cp.items[0].collision_id);
        }
      })
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, [page, borough, severity]); // eslint-disable-line react-hooks/exhaustive-deps

  const selected = useMemo(
    () => crashPage?.items.find((i) => i.collision_id === selectedId) ?? crashPage?.items[0] ?? null,
    [crashPage, selectedId]
  );

  const totalPages = crashPage ? Math.ceil(crashPage.total / PAGE_SIZE) : 1;
  const maxBarH = useMemo(
    () => Math.max(...dailyBars.map((b) => b.crash_count), 1),
    [dailyBars]
  );

  return (
    <div className="incident-page">
      <div className="topbar">
        <div>
          <div className="topbar-title">Incident explorer</div>
          <div className="topbar-sub">
            {summary ? `${summary.total.toLocaleString()} incidents` : "…"} ·{" "}
            {borough !== "All" ? borough : "All boroughs"}
          </div>
        </div>
        <a
          href="/api/v1/export?dataset=silver.crashes&format=csv"
          className="act-btn"
          download
        >
          Export CSV
        </a>
      </div>

      <div className="filter-strip">
        <input
          className="search-bar"
          placeholder="Search by location, type, zone ID..."
          type="search"
          aria-label="Search incidents"
        />
        <span className="filter-label">Severity</span>
        {SEVERITY_FILTERS.map((s) => (
          <button
            key={s}
            type="button"
            className={`pill${severity === s ? " active" : ""}`}
            onClick={() => { setSeverity(s); setPage(1); }}
          >
            {s}
          </button>
        ))}
        <span className="filter-label" style={{ marginLeft: 4 }}>
          Borough
        </span>
        {BOROUGHS.map((b) => (
          <button
            key={b}
            type="button"
            className={`pill${borough === b ? " active" : ""}`}
            onClick={() => { setBorough(b); setPage(1); }}
          >
            {b}
          </button>
        ))}
      </div>

      <div className="explorer-body">
        <div className="summary-strip">
          <div className="summary-cell">
            <div className="s-label">Total incidents</div>
            <div className="s-val">{loading ? "…" : (summary?.total.toLocaleString() ?? "—")}</div>
          </div>
          <div className="summary-cell">
            <div className="s-label">Fatalities</div>
            <div className="s-val" style={{ color: "var(--color-text-danger)" }}>
              {loading ? "…" : (summary?.fatalities ?? "—")}
            </div>
          </div>
          <div className="summary-cell">
            <div className="s-label">Injuries</div>
            <div className="s-val" style={{ color: "var(--color-text-warning)" }}>
              {loading ? "…" : (summary?.injuries ?? "—")}
            </div>
          </div>
          <div className="summary-cell">
            <div className="s-label">Pedestrian injuries</div>
            <div className="s-val">{loading ? "…" : (summary?.pedestrian_injuries ?? "—")}</div>
          </div>
          <div className="summary-cell">
            <div className="s-label">Cyclist injuries</div>
            <div className="s-val">{loading ? "…" : (summary?.cyclist_injuries ?? "—")}</div>
          </div>
        </div>

        {error && (
          <div style={{ padding: "8px 14px", color: "var(--color-text-danger)", fontSize: 12 }}>
            {error}
          </div>
        )}

        <div className="card">
          <div className="card-header">
            Daily incident count{" "}
            <span className="card-sub">last 30 days · bars coloured by max severity</span>
          </div>
          <div className="timeline-area">
            <div className="chart-row">
              {dailyBars.map((bar) => (
                <div
                  key={bar.day}
                  className="c-bar"
                  style={{
                    height: `${Math.round((bar.crash_count / maxBarH) * 100)}%`,
                    background: barColor(bar),
                  }}
                  title={`${bar.day} · ${bar.crash_count} incidents`}
                />
              ))}
            </div>
            <div className="x-labels">
              {dailyBars.length > 0 && (
                <>
                  <span>{formatDate(dailyBars[0].day)}</span>
                  {dailyBars.length > 10 && (
                    <span>{formatDate(dailyBars[Math.floor(dailyBars.length / 3)].day)}</span>
                  )}
                  {dailyBars.length > 20 && (
                    <span>{formatDate(dailyBars[Math.floor((dailyBars.length * 2) / 3)].day)}</span>
                  )}
                  <span>{formatDate(dailyBars[dailyBars.length - 1].day)}</span>
                </>
              )}
            </div>
            <div style={{ display: "flex", gap: 14, padding: "0 0 10px", fontSize: 11, color: "var(--color-text-secondary)" }}>
              <span>
                <span style={{ display: "inline-block", width: 8, height: 8, borderRadius: 2, background: "#E24B4A", marginRight: 4 }} />
                Fatal/injury
              </span>
              <span>
                <span style={{ display: "inline-block", width: 8, height: 8, borderRadius: 2, background: "#EF9F27", marginRight: 4 }} />
                Minor injury
              </span>
              <span>
                <span style={{ display: "inline-block", width: 8, height: 8, borderRadius: 2, background: "#888780", marginRight: 4 }} />
                Property only
              </span>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="split-body">
            <div>
              <table className="tbl">
                <thead>
                  <tr>
                    <th style={{ width: 70 }}>Date</th>
                    <th>Location</th>
                    <th style={{ width: 80 }}>Severity</th>
                    <th style={{ width: 60 }}>Injuries</th>
                  </tr>
                </thead>
                <tbody>
                  {loading && (
                    <tr>
                      <td colSpan={4} style={{ textAlign: "center", color: "var(--color-text-secondary)", padding: 16 }}>
                        Loading…
                      </td>
                    </tr>
                  )}
                  {(crashPage?.items ?? []).map((row) => (
                    <tr
                      key={row.collision_id}
                      onClick={() => setSelectedId(row.collision_id)}
                      style={{
                        outline: selectedId === row.collision_id
                          ? "2px solid var(--color-border-info)"
                          : undefined,
                        outlineOffset: -2,
                        cursor: "pointer",
                      }}
                    >
                      <td>{formatDate(row.crash_date)}</td>
                      <td>{locationLabel(row)}</td>
                      <td>
                        <span className={severityBadgeClass(row.severity)}>
                          {row.severity}
                        </span>
                      </td>
                      <td style={riskCellStyle(row.persons_injured > 0 ? 0.8 : null)}>
                        {row.persons_injured}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <div className="pagination">
                <span>
                  Showing {crashPage ? ((page - 1) * PAGE_SIZE + 1) : 0}–
                  {crashPage ? Math.min(page * PAGE_SIZE, crashPage.total) : 0} of{" "}
                  {crashPage?.total.toLocaleString() ?? "…"}
                </span>
                <div style={{ flex: 1 }} />
                <button
                  type="button"
                  className="pg-btn"
                  disabled={page <= 1}
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                >
                  ←
                </button>
                {Array.from({ length: Math.min(3, totalPages) }, (_, i) => {
                  const p = Math.max(1, Math.min(page - 1 + i, totalPages - 2 + i));
                  return (
                    <button
                      key={p}
                      type="button"
                      className={`pg-btn${page === p ? " active" : ""}`}
                      onClick={() => setPage(p)}
                    >
                      {p}
                    </button>
                  );
                })}
                {totalPages > 3 && <span>…</span>}
                {totalPages > 3 && (
                  <button
                    type="button"
                    className="pg-btn"
                    onClick={() => setPage(totalPages)}
                  >
                    {totalPages}
                  </button>
                )}
                <button
                  type="button"
                  className="pg-btn"
                  disabled={page >= totalPages}
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                >
                  →
                </button>
              </div>
            </div>

            {selected && (
              <div className="detail-panel">
                <div className="detail-title">
                  {formatDate(selected.crash_date)} · {selected.severity} · {locationLabel(selected)}
                </div>
                {[
                  { key: "Borough", val: selected.borough ?? "—" },
                  { key: "On street", val: selected.on_street_name ?? "—" },
                  { key: "Cross street", val: selected.cross_street_name ?? selected.off_street_name ?? "—" },
                  { key: "Time", val: selected.crash_time ?? "—" },
                  { key: "Fatalities", val: String(selected.persons_killed), valStyle: selected.persons_killed > 0 ? { color: "var(--color-text-danger)" } as CSSProperties : undefined },
                  { key: "Injuries", val: String(selected.persons_injured) },
                  { key: "Pedestrians injured", val: String(selected.pedestrians_injured) },
                  { key: "Cyclists injured", val: String(selected.cyclists_injured) },
                  { key: "Motorists injured", val: String(selected.motorists_injured) },
                  { key: "Severity", val: selected.severity, valStyle: selected.severity === "Fatal" ? { color: "var(--color-text-danger)" } as CSSProperties : undefined },
                ].map((r) => (
                  <div key={r.key} className="detail-row">
                    <span className="detail-key">{r.key}</span>
                    <span className="detail-val" style={r.valStyle}>{r.val}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
