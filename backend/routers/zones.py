"""
Zone detail endpoints — combines all four gold feature tables.

crash_features / traffic_features are keyed at borough level (one
representative grid_cell_id per borough), so we look them up by matching
borough_name from spatial_features rather than exact grid_cell_id.
"""

import json
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from db import cursor

router = APIRouter()


# ── GeoJSON heatmap endpoint ────────────────────────────────────────────────

def _decimate(ring: list, step: int = 25) -> list:
    """Keep every Nth coordinate pair; always close the ring."""
    if len(ring) <= 4:
        return ring
    sampled = ring[::step]
    if sampled[-1] != ring[-1]:
        sampled.append(ring[-1])
    return sampled


def _simplify_geometry(geom: dict, step: int = 25) -> dict:
    """Decimate all rings in a MultiPolygon or Polygon GeoJSON geometry."""
    if geom.get("type") == "MultiPolygon":
        return {
            "type": "MultiPolygon",
            "coordinates": [
                [_decimate(ring, step) for ring in polygon]
                for polygon in geom["coordinates"]
            ],
        }
    if geom.get("type") == "Polygon":
        return {
            "type": "Polygon",
            "coordinates": [_decimate(ring, step) for ring in geom["coordinates"]],
        }
    return geom


@router.get("/zones/geojson")
def zones_geojson(step: int = Query(25, ge=1, le=200)) -> list[dict[str, Any]]:
    """
    Return all DSNY zones as simplified GeoJSON polygons with risk scores.
    The `step` parameter controls decimation (higher = fewer points).
    """
    zones_sql = """
        SELECT DISTINCT ON (coalesce(nullif(trim(id), ''), nullif(trim(objectid), '')))
            coalesce(nullif(trim(id), ''), nullif(trim(objectid), ''))   AS grid_cell_id,
            zone,
            zonename,
            borocode,
            centerpoint_latitude::float                                  AS centroid_lat,
            centerpoint_longitude::float                                 AS centroid_lon,
            geometry
        FROM raw.zone_map_data
        WHERE coalesce(nullif(trim(id), ''), nullif(trim(objectid), '')) IS NOT NULL
          AND centerpoint_latitude IS NOT NULL
        ORDER BY coalesce(nullif(trim(id), ''), nullif(trim(objectid), '')), ingested_at DESC NULLS LAST
    """

    risk_sql = """
        WITH latest_crash AS (
            SELECT DISTINCT ON (grid_cell_id)
                grid_cell_id,
                crash_count_30d,
                crash_count_7d,
                injuries_7d,
                fatalities_30d
            FROM raw_gold.crash_features
            ORDER BY grid_cell_id, hour_bucket DESC
        ),
        max_c AS (SELECT NULLIF(MAX(crash_count_30d), 0) AS max_30d FROM latest_crash)
        SELECT
            lc.grid_cell_id,
            lc.crash_count_30d,
            lc.crash_count_7d,
            lc.injuries_7d,
            lc.fatalities_30d,
            ROUND(lc.crash_count_30d::numeric / mc.max_30d, 3) AS risk_score
        FROM latest_crash lc CROSS JOIN max_c mc
        WHERE mc.max_30d IS NOT NULL
    """

    with cursor() as cur:
        cur.execute(zones_sql)
        zone_rows = cur.fetchall()
        cur.execute(risk_sql)
        risk_rows = {r["grid_cell_id"]: dict(r) for r in cur.fetchall()}

    result = []
    for row in zone_rows:
        gid = row["grid_cell_id"]
        raw_geom = row["geometry"]
        geom = json.loads(raw_geom) if isinstance(raw_geom, str) else raw_geom
        simplified = _simplify_geometry(geom, step=step)

        risk = risk_rows.get(gid, {})
        result.append({
            "grid_cell_id": gid,
            "zone": row["zone"],
            "zonename": row["zonename"],
            "borocode": row["borocode"],
            "centroid_lat": row["centroid_lat"],
            "centroid_lon": row["centroid_lon"],
            "crash_count_30d": risk.get("crash_count_30d", 0),
            "crash_count_7d": risk.get("crash_count_7d", 0),
            "injuries_7d": risk.get("injuries_7d", 0),
            "fatalities_30d": risk.get("fatalities_30d", 0),
            "risk_score": float(risk.get("risk_score", 0) or 0),
            "geometry": simplified,
        })

    return result


class ZoneMetrics(BaseModel):
    grid_cell_id: str
    zone_name: Optional[str]
    borough_name: Optional[str]
    # crash features
    crash_count_7d: Optional[int]
    crash_count_30d: Optional[int]
    injuries_7d: Optional[int]
    fatalities_30d: Optional[int]
    vru_injured_30d: Optional[int]
    injury_rate_per_crash: Optional[float]
    risk_score: Optional[float]
    # traffic features
    total_volume: Optional[int]
    avg_hourly_volume_7d: Optional[float]
    violations_7d: Optional[int]
    # env features
    temperature_2m: Optional[float]
    precipitation: Optional[float]
    is_snow_event: Optional[bool]
    is_heavy_rain: Optional[bool]
    is_below_freezing: Optional[bool]
    salt_treatment_active: Optional[bool]
    avg_pavement_rating: Optional[float]
    avg_speed_limit_mph: Optional[float]
    speed_hump_count: Optional[int]
    # spatial features
    total_bike_segments: Optional[int]
    protected_lane_segments: Optional[int]
    protected_lane_ratio: Optional[float]
    has_protected_bike_lane: Optional[bool]
    has_any_bike_infrastructure: Optional[bool]
    centerpoint_latitude: Optional[float]
    centerpoint_longitude: Optional[float]


@router.get("/zones/{grid_cell_id}", response_model=ZoneMetrics)
def zone_detail(grid_cell_id: str):
    # 1. Spatial features (exact match)
    spatial_sql = """
        SELECT DISTINCT ON (grid_cell_id)
            grid_cell_id, zonename, borough_name,
            total_bike_segments, protected_lane_segments,
            protected_lane_ratio, has_protected_bike_lane,
            has_any_bike_infrastructure,
            centerpoint_latitude, centerpoint_longitude
        FROM raw_gold.spatial_features
        WHERE grid_cell_id = %(gid)s
        ORDER BY grid_cell_id, snapshot_ts DESC
    """

    # 2. Env features (exact match or nearest)
    env_sql = """
        SELECT DISTINCT ON (grid_cell_id)
            temperature_2m, precipitation, is_snow_event, is_heavy_rain,
            is_below_freezing, salt_treatment_active,
            avg_pavement_rating, avg_speed_limit_mph, speed_hump_count
        FROM raw_gold.env_features
        WHERE grid_cell_id = %(gid)s
        ORDER BY grid_cell_id, hour_bucket DESC
    """

    # 3+4. Crash + traffic features by borough (borough-level proxy)
    # First get borough from spatial
    crash_by_boro_sql = """
        WITH latest_crash AS (
            SELECT DISTINCT ON (grid_cell_id)
                grid_cell_id,
                crash_count_7d, crash_count_30d, injuries_7d,
                fatalities_30d, vru_injured_30d, injury_rate_per_crash
            FROM raw_gold.crash_features
            ORDER BY grid_cell_id, hour_bucket DESC
        ),
        max_crashes AS (
            SELECT NULLIF(MAX(crash_count_30d), 0) AS max_30d FROM latest_crash
        ),
        latest_spatial_boro AS (
            SELECT DISTINCT ON (grid_cell_id)
                grid_cell_id, borough_name
            FROM raw_gold.spatial_features
            WHERE grid_cell_id = %(gid)s
            ORDER BY grid_cell_id, snapshot_ts DESC
        )
        SELECT
            lc.crash_count_7d,
            lc.crash_count_30d,
            lc.injuries_7d,
            lc.fatalities_30d,
            lc.vru_injured_30d,
            ROUND(lc.injury_rate_per_crash::numeric, 3) AS injury_rate_per_crash,
            ROUND(lc.crash_count_30d::numeric / mc.max_30d, 2) AS risk_score
        FROM latest_crash lc
        CROSS JOIN max_crashes mc
        JOIN (
            SELECT DISTINCT ON (s.grid_cell_id) s.grid_cell_id AS borough_cf_gid
            FROM raw_gold.spatial_features s
            JOIN latest_spatial_boro lb
              ON UPPER(s.borough_name) = UPPER(lb.borough_name)
            ORDER BY s.grid_cell_id, s.snapshot_ts DESC
        ) matching ON lc.grid_cell_id = matching.borough_cf_gid
        WHERE mc.max_30d IS NOT NULL
        LIMIT 1
    """

    traffic_by_boro_sql = """
        WITH latest_spatial_boro AS (
            SELECT DISTINCT ON (grid_cell_id)
                grid_cell_id, borough_name
            FROM raw_gold.spatial_features
            WHERE grid_cell_id = %(gid)s
            ORDER BY grid_cell_id, snapshot_ts DESC
        ),
        matching_gids AS (
            SELECT DISTINCT s.grid_cell_id AS tf_gid
            FROM raw_gold.spatial_features s
            JOIN latest_spatial_boro lb
              ON UPPER(s.borough_name) = UPPER(lb.borough_name)
        )
        SELECT DISTINCT ON (tf.grid_cell_id)
            tf.total_volume,
            tf.avg_hourly_volume_7d,
            tf.violations_7d
        FROM raw_gold.traffic_features tf
        JOIN matching_gids m ON tf.grid_cell_id = m.tf_gid
        ORDER BY tf.grid_cell_id, tf.hour_bucket DESC
        LIMIT 1
    """

    with cursor() as cur:
        cur.execute(spatial_sql, {"gid": grid_cell_id})
        spatial = cur.fetchone()
        if not spatial:
            raise HTTPException(status_code=404, detail=f"Zone {grid_cell_id!r} not found")

        cur.execute(env_sql, {"gid": grid_cell_id})
        env = dict(cur.fetchone() or {})

        cur.execute(crash_by_boro_sql, {"gid": grid_cell_id})
        crash = dict(cur.fetchone() or {})

        cur.execute(traffic_by_boro_sql, {"gid": grid_cell_id})
        traffic = dict(cur.fetchone() or {})

    return {
        "grid_cell_id": grid_cell_id,
        "zone_name": spatial["zonename"],
        "borough_name": spatial["borough_name"],
        # crash
        "crash_count_7d": crash.get("crash_count_7d"),
        "crash_count_30d": crash.get("crash_count_30d"),
        "injuries_7d": crash.get("injuries_7d"),
        "fatalities_30d": crash.get("fatalities_30d"),
        "vru_injured_30d": crash.get("vru_injured_30d"),
        "injury_rate_per_crash": crash.get("injury_rate_per_crash"),
        "risk_score": crash.get("risk_score"),
        # traffic
        "total_volume": traffic.get("total_volume"),
        "avg_hourly_volume_7d": traffic.get("avg_hourly_volume_7d"),
        "violations_7d": traffic.get("violations_7d"),
        # env
        "temperature_2m": env.get("temperature_2m"),
        "precipitation": env.get("precipitation"),
        "is_snow_event": env.get("is_snow_event"),
        "is_heavy_rain": env.get("is_heavy_rain"),
        "is_below_freezing": env.get("is_below_freezing"),
        "salt_treatment_active": env.get("salt_treatment_active"),
        "avg_pavement_rating": env.get("avg_pavement_rating"),
        "avg_speed_limit_mph": env.get("avg_speed_limit_mph"),
        "speed_hump_count": env.get("speed_hump_count"),
        # spatial
        "total_bike_segments": spatial["total_bike_segments"],
        "protected_lane_segments": spatial["protected_lane_segments"],
        "protected_lane_ratio": spatial["protected_lane_ratio"],
        "has_protected_bike_lane": spatial["has_protected_bike_lane"],
        "has_any_bike_infrastructure": spatial["has_any_bike_infrastructure"],
        "centerpoint_latitude": spatial["centerpoint_latitude"],
        "centerpoint_longitude": spatial["centerpoint_longitude"],
    }


@router.get("/zones/{grid_cell_id}/crashes", response_model=list[dict])
def zone_crashes(grid_cell_id: str, limit: int = 10):
    """Recent crashes for the borough containing this grid cell."""
    borough_sql = """
        SELECT DISTINCT ON (grid_cell_id) borough_name
        FROM raw_gold.spatial_features
        WHERE grid_cell_id = %(gid)s
        ORDER BY grid_cell_id, snapshot_ts DESC
    """
    with cursor() as cur:
        cur.execute(borough_sql, {"gid": grid_cell_id})
        row = cur.fetchone()
        if not row:
            return []
        borough_name = row["borough_name"]

        # Map full names to the abbreviated form stored in raw.crashes.borough
        boro_map = {
            "Manhattan": "MANHATTAN",
            "Brooklyn": "BROOKLYN",
            "Queens": "QUEENS",
            "Bronx": "BRONX",
            "Staten Island": "STATEN ISLAND",
        }
        boro_upper = boro_map.get(borough_name, borough_name.upper() if borough_name else None)

        crashes_sql = """
            SELECT
                collision_id,
                crash_date::text,
                crash_time,
                on_street_name,
                cross_street_name,
                COALESCE(number_of_persons_injured, 0)::int    AS persons_injured,
                COALESCE(number_of_persons_killed, 0)::int     AS persons_killed,
                COALESCE(number_of_pedestrians_injured, 0)::int AS pedestrians_injured,
                COALESCE(number_of_cyclist_injured, 0)::int    AS cyclists_injured
            FROM raw.crashes
            WHERE crash_date IS NOT NULL
              AND UPPER(borough) = %(boro)s
            ORDER BY crash_date DESC, collision_id DESC
            LIMIT %(limit)s
        """
        cur.execute(crashes_sql, {"boro": boro_upper, "limit": limit})
        rows = cur.fetchall()

    result = []
    for r in rows:
        d = dict(r)
        killed = d["persons_killed"]
        injured = d["persons_injured"]
        ped_inj = d["pedestrians_injured"]
        cyc_inj = d["cyclists_injured"]
        if killed > 0:
            d["severity"] = "Fatal"
        elif injured > 0:
            d["severity"] = "Injury"
        elif ped_inj > 0 or cyc_inj > 0:
            d["severity"] = "Minor"
        else:
            d["severity"] = "Property"
        result.append(d)
    return result
