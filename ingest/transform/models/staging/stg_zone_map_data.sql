{{ config(materialized='view', tags=['staging']) }}

select
    id,
    version,
    created_at,
    updated_at,
    nullif(trim(zone), '') as zone,
    nullif(trim(zonename), '') as zonename,
    nullif(trim(borocode), '') as borocode,
    nullif(trim(objectid), '') as objectid,
    shape_area::double precision as shape_area,
    shape_length::double precision as shape_length,
    geometry,
    centerpoint_latitude::double precision as centerpoint_latitude,
    centerpoint_longitude::double precision as centerpoint_longitude,
    ingested_at
from {{ source('raw', 'zone_map_data') }}
