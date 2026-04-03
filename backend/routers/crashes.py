"""
Crash endpoints — powered by silver.crashes (raw.crashes in the DB).
"""

from typing import Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel

from db import cursor

router = APIRouter()


class CrashRow(BaseModel):
    collision_id: int
    crash_date: Optional[str]
    crash_time: Optional[str]
    borough: Optional[str]
    on_street_name: Optional[str]
    off_street_name: Optional[str]
    cross_street_name: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    persons_injured: int
    persons_killed: int
    pedestrians_injured: int
    cyclists_injured: int
    motorists_injured: int
    severity: str  # derived: "Fatal" | "Injury" | "Minor" | "Property"


class CrashPage(BaseModel):
    items: list[CrashRow]
    total: int
    page: int
    page_size: int


class CrashSummary(BaseModel):
    total: int
    fatalities: int
    injuries: int
    pedestrian_injuries: int
    cyclist_injuries: int


def _severity(killed: int, injured: int, ped_inj: int, cyc_inj: int) -> str:
    if killed > 0:
        return "Fatal"
    if injured > 0:
        return "Injury"
    if ped_inj > 0 or cyc_inj > 0:
        return "Minor"
    return "Property"


_BASE_WHERE = """
    WHERE c.crash_date IS NOT NULL
      {borough_filter}
      {severity_filter}
"""


@router.get("/crashes", response_model=CrashPage)
def list_crashes(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    borough: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
):
    offset = (page - 1) * page_size

    borough_filter = "AND UPPER(c.borough) = UPPER(%(borough)s)" if borough and borough != "All" else ""

    severity_map = {
        "Fatal": "c.number_of_persons_killed > 0",
        "Injury": "c.number_of_persons_killed = 0 AND c.number_of_persons_injured > 0",
        "Minor": "c.number_of_persons_killed = 0 AND c.number_of_persons_injured = 0 AND (c.number_of_pedestrians_injured > 0 OR c.number_of_cyclist_injured > 0)",
        "Property only": "c.number_of_persons_killed = 0 AND c.number_of_persons_injured = 0 AND c.number_of_pedestrians_injured = 0 AND c.number_of_cyclist_injured = 0",
    }
    severity_filter = f"AND ({severity_map[severity]})" if severity and severity in severity_map else ""

    where = _BASE_WHERE.format(borough_filter=borough_filter, severity_filter=severity_filter)

    count_sql = f"SELECT COUNT(*) AS total FROM raw.crashes c {where}"
    data_sql = f"""
        SELECT
            c.collision_id,
            c.crash_date::text,
            c.crash_time,
            c.borough,
            c.on_street_name,
            c.off_street_name,
            c.cross_street_name,
            c.latitude,
            c.longitude,
            COALESCE(c.number_of_persons_injured, 0)::int    AS persons_injured,
            COALESCE(c.number_of_persons_killed, 0)::int     AS persons_killed,
            COALESCE(c.number_of_pedestrians_injured, 0)::int AS pedestrians_injured,
            COALESCE(c.number_of_cyclist_injured, 0)::int    AS cyclists_injured,
            COALESCE(c.number_of_motorist_injured, 0)::int   AS motorists_injured
        FROM raw.crashes c
        {where}
        ORDER BY c.crash_date DESC, c.collision_id DESC
        LIMIT %(limit)s OFFSET %(offset)s
    """

    params = {"borough": borough, "limit": page_size, "offset": offset}
    with cursor() as cur:
        cur.execute(count_sql, params)
        total = cur.fetchone()["total"]
        cur.execute(data_sql, params)
        rows = cur.fetchall()

    items = []
    for r in rows:
        d = dict(r)
        d["severity"] = _severity(
            d["persons_killed"], d["persons_injured"],
            d["pedestrians_injured"], d["cyclists_injured"],
        )
        items.append(d)

    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/crashes/summary", response_model=CrashSummary)
def crashes_summary(borough: Optional[str] = Query(None)):
    borough_filter = "AND UPPER(borough) = UPPER(%(borough)s)" if borough and borough != "All" else ""
    sql = f"""
        SELECT
            COUNT(*)                                                        AS total,
            COALESCE(SUM(number_of_persons_killed),      0)::int           AS fatalities,
            COALESCE(SUM(number_of_persons_injured),     0)::int           AS injuries,
            COALESCE(SUM(number_of_pedestrians_injured), 0)::int           AS pedestrian_injuries,
            COALESCE(SUM(number_of_cyclist_injured),     0)::int           AS cyclist_injuries
        FROM raw.crashes
        WHERE crash_date IS NOT NULL
          {borough_filter}
    """
    with cursor() as cur:
        cur.execute(sql, {"borough": borough})
        row = cur.fetchone()
    return dict(row)


@router.get("/crashes/daily", response_model=list[dict])
def crashes_daily(days: int = Query(30, ge=7, le=90)):
    """Daily crash + fatality counts for the timeline bar chart."""
    sql = """
        SELECT
            crash_date::date                                        AS day,
            COUNT(*)::int                                           AS crash_count,
            COALESCE(SUM(number_of_persons_killed), 0)::int        AS fatalities,
            COALESCE(SUM(number_of_persons_injured), 0)::int       AS injuries
        FROM raw.crashes
        WHERE crash_date >= NOW() - (%(days)s || ' days')::interval
          AND crash_date IS NOT NULL
        GROUP BY crash_date::date
        ORDER BY day
    """
    with cursor() as cur:
        cur.execute(sql, {"days": days})
        rows = cur.fetchall()
    return [dict(r) for r in rows]
