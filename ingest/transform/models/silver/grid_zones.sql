{{ config(
    unique_key='grid_cell_id',
    tags=['silver'],
    materialized='view',
    on_schema_change='sync_all_columns',
) }}

-- DSNY zones: supports zone drill-down / heatmap (frontend wireframes). PostGIS spatial join to
-- districts is a follow-up; grid_cell_id is stable from raw id/objectid.
-- Dedupe: raw may contain multiple ingests per zone row (merge requires one source row per key).

with base as (
    select
        coalesce(nullif(trim(z.id), ''), nullif(trim(z.objectid), '')) as grid_cell_id,
        z.zone,
        z.zonename,
        z.borocode,
        b.borough_name,
        z.shape_area,
        z.shape_length,
        z.centerpoint_latitude,
        z.centerpoint_longitude,
        z.geometry,
        z.ingested_at,
        z.updated_at
    from {{ ref('stg_zone_map_data') }} as z
    left join {{ ref('borough') }} as b on z.borocode = b.borocode
    where coalesce(nullif(trim(z.id), ''), nullif(trim(z.objectid), '')) is not null
),
ranked as (
    select
        *,
        row_number() over (
            partition by grid_cell_id
            order by ingested_at desc nulls last, updated_at desc nulls last
        ) as _rn
    from base
)
select
    grid_cell_id,
    zone,
    zonename,
    borocode,
    borough_name,
    shape_area,
    shape_length,
    centerpoint_latitude,
    centerpoint_longitude,
    geometry,
    ingested_at
from ranked
where _rn = 1
