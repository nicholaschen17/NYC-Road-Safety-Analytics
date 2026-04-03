{{ config(
    unique_key=['grid_cell_id', 'hour_bucket'],
    tags=['gold'],
    materialized='table',
    on_schema_change='sync_all_columns',
) }}

-- Environmental features. Grain: (grid_cell_id, hour_bucket).
-- Feeds: main heatmap weather overlay, zone drill-down env context panel, reporting export.
--
-- Weather joined to grid_zones by exact centerpoint lat/lon match (Open-Meteo
-- fetches per DSNY zone centroid, so the join is 1-to-1 when data is complete).
-- Salt events and road conditions are borough-level; PostGIS will sharpen to segment level.

with weather_zoned as (
    select
        gz.grid_cell_id,
        wh.weather_timestamp                     as hour_bucket,
        wh.temperature_2m_filled                 as temperature_2m,
        wh.precipitation_filled                  as precipitation,
        wh.weather_code,
        wh.rain,
        wh.snowfall,
        wh.apparent_temperature,
        wh.cloud_cover,
        wh.snow_depth,
        wh.temperature_2m_imputed,
        wh.precipitation_imputed
    from {{ ref('weather_hourly') }} as wh
    inner join {{ ref('grid_zones') }} as gz
        on round(wh.centerpoint_latitude::numeric, 4)
           = round(gz.centerpoint_latitude::numeric, 4)
        and round(wh.centerpoint_longitude::numeric, 4)
           = round(gz.centerpoint_longitude::numeric, 4)
),

salt_daily as (
    select
        upper(trim(borough_name))           as borough_upper,
        date_of_report::date                as salt_date,
        sum(tons_salted)                    as total_tons_salted,
        count(distinct dsny_storm)          as storm_events_count
    from {{ ref('salt_events_long') }}
    where date_of_report is not null
    group by 1, 2
),

-- Static road infrastructure context aggregated to borough.
road_context as (
    select
        upper(trim(borough))                                                        as borough_upper,
        avg(case when metric_type = 'pavement_rating' then numeric_metric end)     as avg_pavement_rating,
        avg(case when metric_type = 'posted_speed_limit_mph' then numeric_metric end) as avg_speed_limit_mph,
        count(case when metric_type = 'speed_hump_installation' then 1 end)         as speed_hump_count
    from {{ ref('road_conditions') }}
    where borough is not null
    group by 1
),

grid_borough_map as (
    select
        grid_cell_id,
        upper(trim(borough_name)) as borough_upper
    from {{ ref('grid_zones') }}
    where borough_name is not null
),

final as (
    select
        wz.grid_cell_id,
        wz.hour_bucket,
        wz.temperature_2m,
        wz.precipitation,
        wz.weather_code,
        wz.rain,
        wz.snowfall,
        wz.apparent_temperature,
        wz.cloud_cover,
        wz.snow_depth,
        wz.temperature_2m_imputed,
        wz.precipitation_imputed,
        -- derived risk flags for ML feature inputs
        (coalesce(wz.snowfall, 0) > 0 or coalesce(wz.snow_depth, 0) > 0)   as is_snow_event,
        (coalesce(wz.precipitation, 0) > 5)                                  as is_heavy_rain,
        (coalesce(wz.temperature_2m, 999) < 0)                               as is_below_freezing,
        -- salt treatment active on the same calendar day
        coalesce(sd.total_tons_salted, 0)                                    as total_tons_salted,
        coalesce(sd.storm_events_count, 0)                                   as storm_events_count,
        (coalesce(sd.total_tons_salted, 0) > 0)                              as salt_treatment_active,
        -- static road infrastructure context (refreshes each dbt run)
        rc.avg_pavement_rating,
        rc.avg_speed_limit_mph,
        coalesce(rc.speed_hump_count, 0)                                     as speed_hump_count
    from weather_zoned as wz
    left join grid_borough_map as gbm
        on wz.grid_cell_id = gbm.grid_cell_id
    left join salt_daily as sd
        on gbm.borough_upper = sd.borough_upper
        and wz.hour_bucket::date = sd.salt_date
    left join road_context as rc
        on gbm.borough_upper = rc.borough_upper
)

select * from final
