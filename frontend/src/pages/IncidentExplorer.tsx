import { useMemo, useState, type CSSProperties } from "react";
import { Link } from "react-router-dom";

const SEVERITY_FILTERS = [
  "All",
  "Fatal",
  "Injury",
  "Property only",
] as const;
const BOROUGHS = ["All", "Manhattan", "Brooklyn", "Queens"] as const;
const CONDITION_FILTERS = ["Wet", "Snow/ice"] as const;

const DAILY_BARS: { h: number; bg: string; title?: string }[] = [
  { h: 42, bg: "#EF9F27", title: "Mar 1 · 9 incidents" },
  { h: 33, bg: "#888780", title: "Mar 2" },
  { h: 55, bg: "#E24B4A", title: "Mar 3 · fatal" },
  { h: 28, bg: "#888780" },
  { h: 38, bg: "#EF9F27" },
  { h: 60, bg: "#E24B4A" },
  { h: 45, bg: "#EF9F27" },
  { h: 30, bg: "#888780" },
  { h: 50, bg: "#EF9F27" },
  { h: 70, bg: "#E24B4A" },
  { h: 40, bg: "#EF9F27" },
  { h: 35, bg: "#888780" },
  { h: 55, bg: "#E24B4A" },
  { h: 48, bg: "#EF9F27" },
  { h: 32, bg: "#888780" },
  { h: 62, bg: "#E24B4A" },
  { h: 44, bg: "#EF9F27" },
  { h: 37, bg: "#888780" },
  { h: 80, bg: "#E24B4A" },
  { h: 52, bg: "#EF9F27" },
  { h: 58, bg: "#E24B4A" },
  { h: 46, bg: "#EF9F27" },
];

type IncidentRow = {
  id: string;
  date: string;
  location: string;
  severity: "Fatal" | "Injury" | "Minor" | "Property";
  zoneRisk: string;
  zoneRiskColor: "danger" | "warning" | "default";
  gridId: string;
};

const INCIDENTS: IncidentRow[] = [
  {
    id: "1",
    date: "Mar 20",
    location: "Atlantic Ave / 4th Ave, BK",
    severity: "Fatal",
    zoneRisk: "0.91",
    zoneRiskColor: "danger",
    gridId: "4812",
  },
  {
    id: "2",
    date: "Mar 20",
    location: "Queens Blvd / Union Tpk, QN",
    severity: "Injury",
    zoneRisk: "0.87",
    zoneRiskColor: "danger",
    gridId: "4827",
  },
  {
    id: "3",
    date: "Mar 19",
    location: "Grand Concourse / 161st, BX",
    severity: "Minor",
    zoneRisk: "0.74",
    zoneRiskColor: "warning",
    gridId: "4808",
  },
  {
    id: "4",
    date: "Mar 19",
    location: "34th St / 8th Ave, MN",
    severity: "Injury",
    zoneRisk: "0.67",
    zoneRiskColor: "warning",
    gridId: "4803",
  },
  {
    id: "5",
    date: "Mar 18",
    location: "Atlantic Ave / 4th Ave, BK",
    severity: "Injury",
    zoneRisk: "0.91",
    zoneRiskColor: "danger",
    gridId: "4812",
  },
  {
    id: "6",
    date: "Mar 18",
    location: "Hylan Blvd / Richmond Ave, SI",
    severity: "Minor",
    zoneRisk: "0.58",
    zoneRiskColor: "warning",
    gridId: "4802",
  },
  {
    id: "7",
    date: "Mar 17",
    location: "Flatbush Ave / Empire Blvd, BK",
    severity: "Property",
    zoneRisk: "0.44",
    zoneRiskColor: "default",
    gridId: "4815",
  },
  {
    id: "8",
    date: "Mar 16",
    location: "Northern Blvd / Main St, QN",
    severity: "Injury",
    zoneRisk: "0.69",
    zoneRiskColor: "warning",
    gridId: "4821",
  },
];

const DETAIL_BY_ID: Record<
  string,
  {
    title: string;
    rows: { key: string; val: string; valStyle?: CSSProperties }[];
  }
> = {
  "1": {
    title: "Mar 20 · Fatal · Atlantic Ave / 4th Ave",
    rows: [
      { key: "Zone", val: "Grid 4812 · Brooklyn" },
      { key: "Crash type", val: "Rear-end" },
      { key: "Time", val: "08:42 AM" },
      {
        key: "Fatalities",
        val: "1",
        valStyle: { color: "var(--color-text-danger)" },
      },
      { key: "Injuries", val: "2" },
      { key: "Weather", val: "Wet · 38°F" },
      { key: "Road condition", val: "Poor (2/10)" },
      { key: "Speed limit", val: "30 mph" },
      {
        key: "Predicted risk (prior day)",
        val: "0.91 · High",
        valStyle: { color: "var(--color-text-danger)" },
      },
      {
        key: "Was model alert active?",
        val: "Yes",
        valStyle: { color: "var(--color-text-success)" },
      },
    ],
  },
};

function defaultDetail(inc: IncidentRow) {
  return {
    title: `${inc.date} · ${inc.severity} · ${inc.location.replace(/, [A-Z]{2}$/, "")}`,
    rows: [
      { key: "Zone", val: `Grid ${inc.gridId}` },
      { key: "Severity", val: inc.severity },
      { key: "Zone risk (table)", val: inc.zoneRisk },
    ],
  };
}

function severityBadgeClass(s: IncidentRow["severity"]) {
  if (s === "Fatal" || s === "Injury") return "badge badge-danger";
  if (s === "Minor") return "badge badge-warning";
  return "badge badge-success";
}

function riskCellStyle(c: IncidentRow["zoneRiskColor"]): CSSProperties {
  if (c === "danger") return { color: "var(--color-text-danger)" };
  if (c === "warning") return { color: "var(--color-text-warning)" };
  return {};
}

export default function IncidentExplorer() {
  const [severity, setSeverity] =
    useState<(typeof SEVERITY_FILTERS)[number]>("All");
  const [borough, setBorough] = useState<(typeof BOROUGHS)[number]>("All");
  const [conditions, setConditions] = useState<Set<string>>(new Set());
  const [selectedId, setSelectedId] = useState("1");
  const [page, setPage] = useState(1);

  const selected = useMemo(
    () => INCIDENTS.find((i) => i.id === selectedId) ?? INCIDENTS[0],
    [selectedId]
  );

  const detail = DETAIL_BY_ID[selected.id] ?? defaultDetail(selected);

  return (
    <div className="incident-page">
      <div className="topbar">
        <div>
          <div className="topbar-title">Incident explorer</div>
          <div className="topbar-sub">
            214 incidents · Mar 1 – Mar 22, 2026 · All boroughs
          </div>
        </div>
        <button type="button" className="act-btn">
          Export CSV
        </button>
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
            onClick={() => setSeverity(s)}
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
            onClick={() => setBorough(b)}
          >
            {b}
          </button>
        ))}
        <span className="filter-label" style={{ marginLeft: 4 }}>
          Conditions
        </span>
        {CONDITION_FILTERS.map((c) => (
          <button
            key={c}
            type="button"
            className={`pill${conditions.has(c) ? " active" : ""}`}
            onClick={() =>
              setConditions((prev) => {
                const next = new Set(prev);
                if (next.has(c)) next.delete(c);
                else next.add(c);
                return next;
              })
            }
          >
            {c}
          </button>
        ))}
      </div>

      <div className="explorer-body">
        <div className="summary-strip">
          <div className="summary-cell">
            <div className="s-label">Total incidents</div>
            <div className="s-val">214</div>
          </div>
          <div className="summary-cell">
            <div className="s-label">Fatalities</div>
            <div className="s-val" style={{ color: "var(--color-text-danger)" }}>
              4
            </div>
          </div>
          <div className="summary-cell">
            <div className="s-label">Injuries</div>
            <div
              className="s-val"
              style={{ color: "var(--color-text-warning)" }}
            >
              61
            </div>
          </div>
          <div className="summary-cell">
            <div className="s-label">Avg risk score (zone)</div>
            <div className="s-val">0.62</div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            Daily incident count{" "}
            <span className="card-sub">
              Mar 1 – Mar 22 · bars coloured by max severity
            </span>
          </div>
          <div className="timeline-area">
            <div className="chart-row">
              {DAILY_BARS.map((bar, i) => (
                <div
                  key={i}
                  className="c-bar"
                  style={{ height: `${bar.h}%`, background: bar.bg }}
                  title={bar.title}
                />
              ))}
            </div>
            <div className="x-labels">
              <span>Mar 1</span>
              <span>Mar 6</span>
              <span>Mar 11</span>
              <span>Mar 16</span>
              <span>Mar 22</span>
            </div>
            <div
              style={{
                display: "flex",
                gap: 14,
                padding: "0 0 10px",
                fontSize: 11,
                color: "var(--color-text-secondary)",
              }}
            >
              <span>
                <span
                  style={{
                    display: "inline-block",
                    width: 8,
                    height: 8,
                    borderRadius: 2,
                    background: "#E24B4A",
                    marginRight: 4,
                  }}
                />
                Fatal/injury
              </span>
              <span>
                <span
                  style={{
                    display: "inline-block",
                    width: 8,
                    height: 8,
                    borderRadius: 2,
                    background: "#EF9F27",
                    marginRight: 4,
                  }}
                />
                Minor injury
              </span>
              <span>
                <span
                  style={{
                    display: "inline-block",
                    width: 8,
                    height: 8,
                    borderRadius: 2,
                    background: "#888780",
                    marginRight: 4,
                  }}
                />
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
                    <th style={{ width: 62 }}>Date</th>
                    <th>Location</th>
                    <th style={{ width: 70 }}>Severity</th>
                    <th style={{ width: 50 }}>Zone risk</th>
                  </tr>
                </thead>
                <tbody>
                  {INCIDENTS.map((row) => (
                    <tr
                      key={row.id}
                      onClick={() => setSelectedId(row.id)}
                      style={{
                        outline:
                          selectedId === row.id
                            ? "2px solid var(--color-border-info)"
                            : undefined,
                        outlineOffset: -2,
                      }}
                    >
                      <td>{row.date}</td>
                      <td>{row.location}</td>
                      <td>
                        <span className={severityBadgeClass(row.severity)}>
                          {row.severity === "Property" ? "Property" : row.severity}
                        </span>
                      </td>
                      <td style={riskCellStyle(row.zoneRiskColor)}>
                        {row.zoneRisk}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <div className="pagination">
                <span>Showing 1–8 of 214</span>
                <div style={{ flex: 1 }} />
                {[1, 2, 3].map((p) => (
                  <button
                    key={p}
                    type="button"
                    className={`pg-btn${page === p ? " active" : ""}`}
                    onClick={() => setPage(p)}
                  >
                    {p}
                  </button>
                ))}
                <span>…</span>
                <button type="button" className="pg-btn">
                  27
                </button>
                <button type="button" className="pg-btn">
                  →
                </button>
              </div>
            </div>
            <div className="detail-panel">
              <div className="detail-title">{detail.title}</div>
              {detail.rows.map((r) => (
                <div key={r.key} className="detail-row">
                  <span className="detail-key">{r.key}</span>
                  <span className="detail-val" style={r.valStyle}>
                    {r.val}
                  </span>
                </div>
              ))}
              <div style={{ marginTop: 12 }}>
                <Link
                  to={`/zones/${selected.gridId}`}
                  className="act-btn"
                  style={{
                    width: "100%",
                    display: "block",
                    textAlign: "center",
                    textDecoration: "none",
                    padding: "7px",
                  }}
                >
                  Open zone detail ↗
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
