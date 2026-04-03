{{ config(
    tags=['silver'],
    materialized='table',
    on_schema_change='sync_all_columns',
    post_hook=[
        "create index if not exists {{ this.identifier }}_geom_4326_gist on {{ this }} using gist (geom_4326)",
    ],
) }}

-- Deduped DSNY district polygons. Supports spatial join to crashes / zones via PostGIS ST_Contains.
-- district_grid_id is coalesce(objectid, id) for a stable merge key.

with base as (
    select
        coalesce(nullif(trim(objectid), ''), nullif(trim(id), '')) as district_grid_id,
        district,
        districtcode,
        shape_area,
        shape_length,
        geometry,
        {{ geojson_to_geom('geometry') }} as geom_4326,
        ingested_at,
        updated_at
    from {{ ref('stg_district_grid_data') }}
    where coalesce(nullif(trim(objectid), ''), nullif(trim(id), '')) is not null
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
    shape_area,
    shape_length,
    geometry,
    geom_4326,
    ingested_at
from ranked
where _rn = 1
