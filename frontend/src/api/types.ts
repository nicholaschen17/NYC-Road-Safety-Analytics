// ── Zone GeoJSON (heatmap) ────────────────────────────────────────────────────

export interface ZoneGeoJSON {
  grid_cell_id: string;
  zone: string;
  zonename: string;
  borocode: string;
  centroid_lat: number;
  centroid_lon: number;
  crash_count_30d: number;
  crash_count_7d: number;
  injuries_7d: number;
  fatalities_30d: number;
  risk_score: number; // 0–1 normalised
  geometry: {
    type: "MultiPolygon" | "Polygon";
    coordinates: number[][][][];
  };
}

// ── Hotspots ────────────────────────────────────────────────────────────────

export interface HotspotRow {
  grid_cell_id: string;
  zone_name: string | null;
  borough_name: string | null;
  crash_count_7d: number;
  crash_count_30d: number;
  injuries_7d: number;
  fatalities_30d: number;
  vru_injured_30d: number;
  injury_rate_per_crash: number;
  risk_score: number; // 0–1 normalised
}

export interface HotspotSummary {
  active_zones: number;
  high_risk_zones: number;
  total_crashes_7d: number;
  total_injuries_7d: number;
  total_fatalities_30d: number;
  total_vru_injured_30d: number;
}

// ── Crashes ──────────────────────────────────────────────────────────────────

export type CrashSeverity = "Fatal" | "Injury" | "Minor" | "Property";

export interface CrashRow {
  collision_id: number;
  crash_date: string | null;
  crash_time: string | null;
  borough: string | null;
  on_street_name: string | null;
  off_street_name: string | null;
  cross_street_name: string | null;
  latitude: number | null;
  longitude: number | null;
  persons_injured: number;
  persons_killed: number;
  pedestrians_injured: number;
  cyclists_injured: number;
  motorists_injured: number;
  severity: CrashSeverity;
}

export interface CrashPage {
  items: CrashRow[];
  total: number;
  page: number;
  page_size: number;
}

export interface CrashSummary {
  total: number;
  fatalities: number;
  injuries: number;
  pedestrian_injuries: number;
  cyclist_injuries: number;
}

export interface DailyBar {
  day: string;
  crash_count: number;
  fatalities: number;
  injuries: number;
}

// ── Zones ─────────────────────────────────────────────────────────────────────

export interface ZoneMetrics {
  grid_cell_id: string;
  zone_name: string | null;
  borough_name: string | null;
  // crash
  crash_count_7d: number | null;
  crash_count_30d: number | null;
  injuries_7d: number | null;
  fatalities_30d: number | null;
  vru_injured_30d: number | null;
  injury_rate_per_crash: number | null;
  risk_score: number | null;
  // traffic
  total_volume: number | null;
  avg_hourly_volume_7d: number | null;
  violations_7d: number | null;
  // env
  temperature_2m: number | null;
  precipitation: number | null;
  is_snow_event: boolean | null;
  is_heavy_rain: boolean | null;
  is_below_freezing: boolean | null;
  salt_treatment_active: boolean | null;
  avg_pavement_rating: number | null;
  avg_speed_limit_mph: number | null;
  speed_hump_count: number | null;
  // spatial
  total_bike_segments: number | null;
  protected_lane_segments: number | null;
  protected_lane_ratio: number | null;
  has_protected_bike_lane: boolean | null;
  has_any_bike_infrastructure: boolean | null;
  centerpoint_latitude: number | null;
  centerpoint_longitude: number | null;
}

export interface ZoneCrash {
  collision_id: number;
  crash_date: string | null;
  crash_time: string | null;
  on_street_name: string | null;
  cross_street_name: string | null;
  persons_injured: number;
  persons_killed: number;
  pedestrians_injured: number;
  cyclists_injured: number;
  severity: CrashSeverity;
}
