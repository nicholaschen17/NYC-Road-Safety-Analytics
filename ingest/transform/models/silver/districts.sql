{{ config(unique_key='district_grid_id', tags=['silver']) }}

-- Cleaned district polygons for future spatial joins to zones / crashes (README silver.grid_zones intent).
-- Dedupe: raw may contain multiple ingests per logical district id (merge requires one source row per key).

with base as (
    select
        coalesce(nullif(trim(id), ''), nullif(trim(districtcode), '')) as district_grid_id,
        district,
        districtcode,
        objectid,
        shape_area,
        shape_length,
        geometry,
        ingested_at,
        updated_at
    from {{ ref('stg_district_grid_data') }}
    where coalesce(nullif(trim(id), ''), nullif(trim(districtcode), '')) is not null
),
ranked as (
    select
        *,
        row_number() over (
            partition by district_grid_id
            order by ingested_at desc nulls last, updated_at desc nulls last
        ) as _rn
    from base
)
select
    district_grid_id,
    district,
    districtcode,
    objectid,
    shape_area,
    shape_length,
    geometry,
    ingested_at
from ranked
where _rn = 1
