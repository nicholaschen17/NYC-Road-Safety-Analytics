"""
Hotspot endpoints — powered by gold.crash_features + gold.spatial_features.

crash_features is keyed at borough-level (one representative grid_cell_id per
borough) until PostGIS point-in-polygon is wired.  The JOIN to spatial_features
on grid_cell_id therefore returns one row per borough, not per DSNY zone.
"""

from typing import Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel

from db import cursor

router = APIRouter()


class HotspotRow(BaseModel):
    grid_cell_id: str
    zone_name: Optional[str]
    borough_name: Optional[str]
    crash_count_7d: int
    crash_count_30d: int
    injuries_7d: int
    fatalities_30d: int
    vru_injured_30d: int
    injury_rate_per_crash: float
    risk_score: float  # normalised 0–1 from crash_count_30d


class HotspotSummary(BaseModel):
    active_zones: int
    high_risk_zones: int
    total_crashes_7d: int
    total_injuries_7d: int
    total_fatalities_30d: int
    total_vru_injured_30d: int


_LATEST_CRASH_CTE = """
latest_crash AS (
    SELECT DISTINCT ON (grid_cell_id)
        grid_cell_id,
        crash_count_7d,
        crash_count_30d,
        injuries_7d,
        fatalities_30d,
        vru_injured_30d,
        injury_rate_per_crash
    FROM raw_gold.crash_features
    ORDER BY grid_cell_id, hour_bucket DESC
),
latest_spatial AS (
    SELECT DISTINCT ON (grid_cell_id)
        grid_cell_id,
        zonename,
        borough_name
    FROM raw_gold.spatial_features
    ORDER BY grid_cell_id, snapshot_ts DESC
),
max_crashes AS (
    SELECT NULLIF(MAX(crash_count_30d), 0) AS max_30d FROM latest_crash
)
"""


@router.get("/hotspots", response_model=list[HotspotRow])
def list_hotspots(
    borough: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=100),
):
    borough_filter = "AND UPPER(ls.borough_name) = UPPER(%(borough)s)" if borough and borough != "All" else ""

    sql = f"""
        WITH {_LATEST_CRASH_CTE}
        SELECT
            lc.grid_cell_id,
            ls.zonename                                                 AS zone_name,
            ls.borough_name,
            lc.crash_count_7d,
            lc.crash_count_30d,
            lc.injuries_7d,
            lc.fatalities_30d,
            lc.vru_injured_30d,
            ROUND(lc.injury_rate_per_crash::numeric, 3)                AS injury_rate_per_crash,
            ROUND(lc.crash_count_30d::numeric / mc.max_30d, 2)         AS risk_score
        FROM latest_crash lc
        CROSS JOIN max_crashes mc
        LEFT JOIN latest_spatial ls ON lc.grid_cell_id = ls.grid_cell_id
        WHERE lc.crash_count_30d > 0
          AND mc.max_30d IS NOT NULL
          AND lc.grid_cell_id NOT LIKE 'borough:%'
          {borough_filter}
        ORDER BY lc.crash_count_30d DESC
        LIMIT %(limit)s
    """
    with cursor() as cur:
        cur.execute(sql, {"borough": borough, "limit": limit})
        rows = cur.fetchall()
    return [dict(r) for r in rows]


@router.get("/hotspots/summary", response_model=HotspotSummary)
def hotspots_summary():
    sql = f"""
        WITH {_LATEST_CRASH_CTE}
        SELECT
            COUNT(*)                                                                AS active_zones,
            COUNT(*) FILTER (
                WHERE lc.crash_count_30d::numeric / mc.max_30d > 0.6
            )                                                                       AS high_risk_zones,
            COALESCE(SUM(lc.crash_count_7d),  0)                                   AS total_crashes_7d,
            COALESCE(SUM(lc.injuries_7d),     0)                                   AS total_injuries_7d,
            COALESCE(SUM(lc.fatalities_30d),  0)                                   AS total_fatalities_30d,
            COALESCE(SUM(lc.vru_injured_30d), 0)                                   AS total_vru_injured_30d
        FROM latest_crash lc
        CROSS JOIN max_crashes mc
        WHERE lc.crash_count_30d > 0
          AND mc.max_30d IS NOT NULL
          AND lc.grid_cell_id NOT LIKE 'borough:%'
    """
    with cursor() as cur:
        cur.execute(sql)
        row = cur.fetchone()
    return dict(row)
