{{ config(
    unique_key='collision_id',
    tags=['silver'],
    materialized='table',
    on_schema_change='sync_all_columns',
) }}

-- Grain: one row per collision_id with full location hierarchy resolved via PostGIS.
-- Only crashes with coordinates are included (lat/lon required for spatial joins).
-- Feeds crash_features (gold) to replace the borough-level grid_cell_id proxy.

with crashes_with_coords as (
    select
        collision_id,
        latitude,
        longitude,
        on_street_name,
        cross_street_name,
        borough,
        zip_code
    from {{ ref('crashes') }}
    where latitude is not null and longitude is not null
),

-- LATERAL + geom_4326 && point uses GiST on grid_zones / districts (see post_hook there).
-- Avoids O(crashes × polygons) nested loop with per-row GeoJSON parse.
zone_join as (
    select
        c.collision_id,
        c.latitude,
        c.longitude,
        c.on_street_name,
        c.cross_street_name,
        c.zip_code,
        gz.grid_cell_id,
        gz.zone,
        gz.zonename,
        gz.borough_name
    from crashes_with_coords as c
    left join lateral (
        select g.grid_cell_id, g.zone, g.zonename, g.borough_name
        from {{ ref('grid_zones') }} as g
        where
            g.geom_4326 is not null
            and g.geom_4326 && {{ wgs84_point('c.longitude', 'c.latitude') }}
            and ST_Contains(g.geom_4326, {{ wgs84_point('c.longitude', 'c.latitude') }})
        order by g.grid_cell_id
        limit 1
    ) as gz on true
),

district_join as (
    select
        zj.*,
        d.district,
        d.districtcode
    from zone_join as zj
    left join lateral (
        select x.district, x.districtcode
        from {{ ref('districts') }} as x
        where
            x.geom_4326 is not null
            and x.geom_4326 && {{ wgs84_point('zj.longitude', 'zj.latitude') }}
            and ST_Contains(x.geom_4326, {{ wgs84_point('zj.longitude', 'zj.latitude') }})
        order by x.district_grid_id
        limit 1
    ) as d on true
)

select
    collision_id,
    latitude,
    longitude,
    on_street_name,
    cross_street_name,
    zip_code,
    grid_cell_id,
    zone,
    zonename        as neighbourhood,
    district,
    districtcode,
    borough_name
from district_join
