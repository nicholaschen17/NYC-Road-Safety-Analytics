-- No duplicate rows by ingest/API natural key: Socrata `id` (when present), `collision_id` on
-- crash_data (when present), or weather grain. Matches raw tables from db/init.sql.

{{ config(
    tags=['bronze', 'crash_data', 'salt_usage_data', 'bike_route_data', 'district_grid_data', 'moving_violations_data', 'speed_hump_data', 'speed_limits_data', 'street_rating_data', 'traffic_volume_cnt_data', 'weather_data', 'zone_map_data']
) }}

with
    crash as (
        select 'crash_data' as source_table, id::text as natural_key, count(*)::bigint as row_count
        from {{ source('raw', 'crash_data') }}
        where id is not null
        group by id
        having count(*) > 1
    ),
    crash_collision as (
        select
            'crash_data.collision_id' as source_table,
            collision_id::text as natural_key,
            count(*)::bigint as row_count
        from {{ source('raw', 'crash_data') }}
        where collision_id is not null
        group by collision_id
        having count(*) > 1
    ),
    salt as (
        select 'salt_usage_data' as source_table, id::text as natural_key, count(*)::bigint as row_count
        from {{ source('raw', 'salt_usage_data') }}
        where id is not null
        group by id
        having count(*) > 1
    ),
    bike as (
        select 'bike_route_data' as source_table, id::text as natural_key, count(*)::bigint as row_count
        from {{ source('raw', 'bike_route_data') }}
        where id is not null
        group by id
        having count(*) > 1
    ),
    district as (
        select 'district_grid_data' as source_table, id::text as natural_key, count(*)::bigint as row_count
        from {{ source('raw', 'district_grid_data') }}
        where id is not null
        group by id
        having count(*) > 1
    ),
    violation as (
        select 'moving_violation_data' as source_table, id::text as natural_key, count(*)::bigint as row_count
        from {{ source('raw', 'moving_violation_data') }}
        where id is not null
        group by id
        having count(*) > 1
    ),
    hump as (
        select 'speed_hump_data' as source_table, id::text as natural_key, count(*)::bigint as row_count
        from {{ source('raw', 'speed_hump_data') }}
        where id is not null
        group by id
        having count(*) > 1
    ),
    limits as (
        select 'speed_limits_data' as source_table, id::text as natural_key, count(*)::bigint as row_count
        from {{ source('raw', 'speed_limits_data') }}
        where id is not null
        group by id
        having count(*) > 1
    ),
    rating as (
        select 'street_rating_data' as source_table, id::text as natural_key, count(*)::bigint as row_count
        from {{ source('raw', 'street_rating_data') }}
        where id is not null
        group by id
        having count(*) > 1
    ),
    traffic as (
        select 'traffic_volume_cnt_data' as source_table, id::text as natural_key, count(*)::bigint as row_count
        from {{ source('raw', 'traffic_volume_cnt_data') }}
        where id is not null
        group by id
        having count(*) > 1
    ),
    zones as (
        select 'zone_map_data' as source_table, id::text as natural_key, count(*)::bigint as row_count
        from {{ source('raw', 'zone_map_data') }}
        where id is not null
        group by id
        having count(*) > 1
    ),
    weather as (
        select
            'weather_data' as source_table,
            concat_ws(
                '|',
                weather_timestamp::text,
                centerpoint_latitude::text,
                centerpoint_longitude::text
            ) as natural_key,
            count(*)::bigint as row_count
        from {{ source('raw', 'weather_data') }}
        where
            weather_timestamp is not null
            and centerpoint_latitude is not null
            and centerpoint_longitude is not null
        group by weather_timestamp, centerpoint_latitude, centerpoint_longitude
        having count(*) > 1
    )

select * from crash
union all
select * from crash_collision
union all
select * from salt
union all
select * from bike
union all
select * from district
union all
select * from violation
union all
select * from hump
union all
select * from limits
union all
select * from rating
union all
select * from traffic
union all
select * from zones
union all
select * from weather
