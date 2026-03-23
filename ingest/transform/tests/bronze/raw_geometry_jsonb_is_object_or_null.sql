-- GeoJSON columns in db/init.sql are JSONB; non-null values should be JSON objects.
-- Fails if any row stores a non-object JSONB in geometry (passes when table is empty).
{{ config(
    tags=['bronze', 'bike_route_data', 'district_grid_data', 'moving_violation_data', 'speed_limits_data']
) }}

with
    bike as (
        select 'bike_route_data' as source_table, id
        from {{ source('raw', 'bike_route_data') }}
        where geometry is not null and jsonb_typeof(geometry) != 'object'
    ),
    district as (
        select 'district_grid_data' as source_table, id
        from {{ source('raw', 'district_grid_data') }}
        where geometry is not null and jsonb_typeof(geometry) != 'object'
    ),
    violation as (
        select 'moving_violation_data' as source_table, id
        from {{ source('raw', 'moving_violation_data') }}
        where geometry is not null and jsonb_typeof(geometry) != 'object'
    ),
    limits as (
        select 'speed_limits_data' as source_table, id
        from {{ source('raw', 'speed_limits_data') }}
        where geometry is not null and jsonb_typeof(geometry) != 'object'
    ),
    rating as (
        select 'street_rating_data' as source_table, id
        from {{ source('raw', 'street_rating_data') }}
        where geometry is not null and jsonb_typeof(geometry) != 'object'
    ),
    zones as (
        select 'zone_map_data' as source_table, id
        from {{ source('raw', 'zone_map_data') }}
        where geometry is not null and jsonb_typeof(geometry) != 'object'
    )

select * from bike
union all
select * from district
union all
select * from violation
union all
select * from limits
union all
select * from rating
union all
select * from zones
