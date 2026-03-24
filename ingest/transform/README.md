# Bronze, Silver, Gold Layers

### Bronze: raw tables drawn from ingestion
11 "raw" Tables:
- raw.crash_data
- raw.salt_usage_data
- raw.bike_route_data
- raw.district_grid_data
- raw.moving_violation_data
- raw.speed_hump_data
- raw.speed_limits_data
- raw.street_rating_data
- raw.traffic_volume_cnt_data
- raw.weather_data
- raw.zone_map_data

### Silver: Cleaned and validated data (Deduplicated, geocoded, joined, null-handled, typed)
Key purpose: geocoding crash lat/lons to grid cells, spatial joining everything to the district grid, resampling traffic volume to hourly buckets, normalising street ratings, and flagging winter treatment events.

Silver models are **incremental tables** (`merge` strategy): each `dbt run` upserts rows by a per-model natural or surrogate unique key (see `unique_key` in each model under `models/silver/`).

Models (implemented under `models/staging/` → `models/silver/` in dbt):
- `crashes` — deduped by `collision_id`, typed; `has_coordinates` for map / incident explorer wireframes. Point-in-polygon → `grid_cell_id` is a follow-up (PostGIS).
- `road_conditions` — union of pavement rating, posted speed limits, and speed humps for drill-down context.
- `weather_hourly` — typed weather + simple null-fill flags for downstream features.
- `grid_zones` + `districts` — cleaned zone/district polygons; join `borough` on `borocode`. Full district↔zone spatial join deferred.
- `violations_daily` — daily counts by `jurisdiction_code` (export / analytics).
- `traffic_vol_hourly` — hourly `sum(vol)` by boro + `segmentid`.
- `bike_route_segments` — route rows + `has_protected_facility` flag.
- `salt_events_long` — salt tons unpivoted to storm × borough (`salt_events`).

### Gold: Feature store
Key purpose: All features are keyed on (grid_cell_id, timestamp) and exist as join key for the model. The four feature groups map cleanly to "raw" sources: crash features carry rolling counts and injury rates, env features bundle weather + road condition + salt events, traffic features combine volume with violations and speed compliance, and spatial features encode proximity to bike routes, zone type, and grid topology.

Models:
- gold.crash_features
- gold.env_features
- gold.traffic_features
- gold.spatial_features

### Bronze to Gold Architecture
![Bronze → silver → gold data lineage](images/data_lineage_source_to_gold.svg)


# Wireframe
[NYC crash hotspot dashboard wireframe](readme_resources/nyc_crash_hotspot_dashboard_wireframe.html)