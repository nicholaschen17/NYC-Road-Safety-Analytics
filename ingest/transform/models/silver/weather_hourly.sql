{{ config(unique_key='weather_hour_sk', tags=['silver']) }}

-- Hourly Open-Meteo rows keyed by zone centerpoint; simple null-fill flags for downstream gold.env_features.
-- weather_hour_sk: stable merge key (avoids float equality issues on lat/lon).
-- Dedupe: re-fetches can repeat the same hour × location (merge requires one source row per key).

with base as (
    select
        md5(
            concat_ws(
                '|',
                weather_timestamp::text,
                round(centerpoint_latitude::numeric, 6)::text,
                round(centerpoint_longitude::numeric, 6)::text
            )
        ) as weather_hour_sk,
        weather_timestamp,
        centerpoint_latitude,
        centerpoint_longitude,
        temperature_2m,
        precipitation,
        weather_code,
        rain,
        snowfall,
        apparent_temperature,
        cloud_cover,
        snow_depth,
        coalesce(temperature_2m, 0::double precision) as temperature_2m_filled,
        (temperature_2m is null) as temperature_2m_imputed,
        coalesce(precipitation, 0::double precision) as precipitation_filled,
        (precipitation is null) as precipitation_imputed,
        ingested_at
    from {{ ref('stg_weather_data') }}
    where weather_timestamp is not null
),
ranked as (
    select
        *,
        row_number() over (
            partition by weather_hour_sk
            order by ingested_at desc nulls last
        ) as _rn
    from base
)
select
    weather_hour_sk,
    weather_timestamp,
    centerpoint_latitude,
    centerpoint_longitude,
    temperature_2m,
    precipitation,
    weather_code,
    rain,
    snowfall,
    apparent_temperature,
    cloud_cover,
    snow_depth,
    temperature_2m_filled,
    temperature_2m_imputed,
    precipitation_filled,
    precipitation_imputed,
    ingested_at
from ranked
where _rn = 1
