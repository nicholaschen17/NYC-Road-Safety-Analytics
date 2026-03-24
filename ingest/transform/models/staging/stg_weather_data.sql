{{ config(materialized='view', tags=['staging']) }}

select
    weather_timestamp::timestamptz as weather_timestamp,
    temperature_2m::double precision as temperature_2m,
    precipitation::double precision as precipitation,
    weather_code::double precision as weather_code,
    rain::double precision as rain,
    snowfall::double precision as snowfall,
    apparent_temperature::double precision as apparent_temperature,
    cloud_cover::double precision as cloud_cover,
    snow_depth::double precision as snow_depth,
    centerpoint_latitude::double precision as centerpoint_latitude,
    centerpoint_longitude::double precision as centerpoint_longitude,
    ingested_at
from {{ source('raw', 'weather_data') }}
