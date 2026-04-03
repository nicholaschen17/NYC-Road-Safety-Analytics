"""
Ad-hoc export endpoint — streams CSV or JSON from gold / silver tables.
"""

import csv
import io
import json
from typing import Literal, Optional

from fastapi import APIRouter, Query
from fastapi.responses import Response, StreamingResponse

from db import cursor

router = APIRouter()

_DATASETS: dict[str, str] = {
    "gold.crash_features": """
        SELECT DISTINCT ON (grid_cell_id) *
        FROM raw_gold.crash_features
        ORDER BY grid_cell_id, hour_bucket DESC
    """,
    "gold.env_features": """
        SELECT DISTINCT ON (grid_cell_id) *
        FROM raw_gold.env_features
        ORDER BY grid_cell_id, hour_bucket DESC
    """,
    "gold.traffic_features": """
        SELECT DISTINCT ON (grid_cell_id) *
        FROM raw_gold.traffic_features
        ORDER BY grid_cell_id, hour_bucket DESC
    """,
    "gold.spatial_features": """
        SELECT DISTINCT ON (grid_cell_id) *
        FROM raw_gold.spatial_features
        ORDER BY grid_cell_id, snapshot_ts DESC
    """,
    "silver.crashes": """
        SELECT * FROM raw.crashes
        WHERE crash_date IS NOT NULL
        ORDER BY crash_date DESC, collision_id DESC
        LIMIT 10000
    """,
}


@router.get("/export")
def export_data(
    dataset: str = Query("gold.crash_features"),
    fmt: Literal["csv", "json"] = Query("csv", alias="format"),
    borough: Optional[str] = Query(None),
):
    if dataset not in _DATASETS:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=f"Unknown dataset. Choose from: {list(_DATASETS)}")

    sql = _DATASETS[dataset]
    borough_clause = ""
    if borough and borough != "All" and dataset == "silver.crashes":
        borough_clause = f"AND UPPER(borough) = UPPER('{borough.replace(chr(39), '')}') "

    if borough_clause:
        sql = sql.rstrip() + f"\n{borough_clause}"

    with cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()

    if not rows:
        return Response(content="", media_type="text/plain")

    columns = list(rows[0].keys())

    if fmt == "json":
        data = json.dumps(
            [
                {k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in row.items()}
                for row in rows
            ],
            default=str,
        )
        return Response(
            content=data,
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="{dataset.replace(".", "_")}.json"'},
        )

    # CSV
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=columns, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow({k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in row.items()})

    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{dataset.replace(".", "_")}.csv"'},
    )
