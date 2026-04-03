import type {
  CrashPage,
  CrashSummary,
  DailyBar,
  HotspotRow,
  HotspotSummary,
  ZoneCrash,
  ZoneGeoJSON,
  ZoneMetrics,
} from "./types";

const BASE = "/api/v1";

async function get<T>(path: string, params?: Record<string, string | number | undefined>): Promise<T> {
  const url = new URL(BASE + path, window.location.origin);
  if (params) {
    for (const [k, v] of Object.entries(params)) {
      if (v !== undefined && v !== null && v !== "All" && v !== "") {
        url.searchParams.set(k, String(v));
      }
    }
  }
  const res = await fetch(url.toString());
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText);
    throw new Error(`API ${res.status}: ${text}`);
  }
  return res.json() as Promise<T>;
}

// ── Hotspots ─────────────────────────────────────────────────────────────────

export function fetchHotspots(opts?: { borough?: string; limit?: number }) {
  return get<HotspotRow[]>("/hotspots", {
    borough: opts?.borough,
    limit: opts?.limit ?? 10,
  });
}

export function fetchHotspotSummary() {
  return get<HotspotSummary>("/hotspots/summary");
}

// ── Crashes ───────────────────────────────────────────────────────────────────

export function fetchCrashes(opts?: {
  page?: number;
  page_size?: number;
  borough?: string;
  severity?: string;
}) {
  return get<CrashPage>("/crashes", {
    page: opts?.page ?? 1,
    page_size: opts?.page_size ?? 20,
    borough: opts?.borough,
    severity: opts?.severity,
  });
}

export function fetchCrashSummary(borough?: string) {
  return get<CrashSummary>("/crashes/summary", { borough });
}

export function fetchDailyBars(days = 30) {
  return get<DailyBar[]>("/crashes/daily", { days });
}

// ── Zones ─────────────────────────────────────────────────────────────────────

export function fetchZonesGeoJSON() {
  return get<ZoneGeoJSON[]>("/zones/geojson");
}

export function fetchZone(gridCellId: string) {
  return get<ZoneMetrics>(`/zones/${encodeURIComponent(gridCellId)}`);
}

export function fetchZoneCrashes(gridCellId: string, limit = 10) {
  return get<ZoneCrash[]>(`/zones/${encodeURIComponent(gridCellId)}/crashes`, { limit });
}

// ── Export ────────────────────────────────────────────────────────────────────

export function buildExportUrl(opts: {
  dataset: string;
  format: "csv" | "json";
  borough?: string;
}) {
  const url = new URL(BASE + "/export", window.location.origin);
  url.searchParams.set("dataset", opts.dataset);
  url.searchParams.set("format", opts.format);
  if (opts.borough && opts.borough !== "All") {
    url.searchParams.set("borough", opts.borough);
  }
  return url.toString();
}
