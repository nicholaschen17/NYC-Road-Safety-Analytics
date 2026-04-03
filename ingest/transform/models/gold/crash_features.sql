{{ config(
    unique_key=['grid_cell_id', 'hour_bucket'],
    tags=['gold'],
    materialized='table',
    on_schema_change='sync_all_columns',
) }}

-- Crash feature aggregations. Grain: (grid_cell_id, hour_bucket).
-- Feeds: main heatmap risk score, zone drill-down injury panel, incident explorer timeline.
--
-- grid_cell_id is resolved per crash via crash_locations (PostGIS ST_Contains).
-- Crashes without coordinates fall back to 'borough:<NAME>'.
-- Location dimensions match crash_locations / grid_zones (zone, neighbourhood, borough_name).
-- max() picks one value per (grid_cell_id, day); all crashes in a cell share the same labels.

with crashes_enriched as (
    -- Resolve spatial grid_cell_id per collision; fall back to borough text for unlocated crashes.
    select
        c.crash_date,
        c.collision_id,
        c.number_of_persons_injured,
        c.number_of_persons_killed,
        c.number_of_pedestrians_injured,
        c.number_of_pedestrians_killed,
        c.number_of_cyclist_injured,
        c.number_of_cyclist_killed,
        c.number_of_motorist_injured,
        c.number_of_motorist_killed,
        c.has_coordinates,
        coalesce(
            cl.grid_cell_id,
            'borough:' || coalesce(upper(trim(c.borough)), 'UNKNOWN')
        ) as grid_cell_id,
        cl.on_street_name,
        cl.zone,
        cl.neighbourhood,
        cl.district,
        coalesce(gz.borough_name, cl.borough_name, upper(trim(c.borough))) as borough_name
    from {{ ref('crashes') }} as c
    left join {{ ref('crash_locations') }} as cl on c.collision_id = cl.collision_id
    left join {{ ref('grid_zones') }} as gz on cl.grid_cell_id = gz.grid_cell_id
    where c.crash_date is not null
),

crashes_daily as (
    select
        grid_cell_id,
        date_trunc('day', crash_date)::timestamp        as hour_bucket,
        -- location dimension: pick any representative value per zone (all identical within a grid_cell)
        max(on_street_name) as street,
        max(zone)           as zone,
        max(neighbourhood)  as neighbourhood,
        max(district)       as district,
        max(borough_name)   as borough_name,
        count(*)                                        as crash_count,
        sum(coalesce(number_of_persons_injured, 0))     as persons_injured,
        sum(coalesce(number_of_persons_killed, 0))      as persons_killed,
        sum(coalesce(number_of_pedestrians_injured, 0)) as pedestrians_injured,
        sum(coalesce(number_of_pedestrians_killed, 0))  as pedestrians_killed,
        sum(coalesce(number_of_cyclist_injured, 0))     as cyclists_injured,
        sum(coalesce(number_of_cyclist_killed, 0))      as cyclists_killed,
        sum(coalesce(number_of_motorist_injured, 0))    as motorists_injured,
        sum(coalesce(number_of_motorist_killed, 0))     as motorists_killed,
        count(*) filter (where has_coordinates)         as crashes_with_coordinates
    from crashes_enriched
    group by 1, 2
),

joined as (
    select
        grid_cell_id,
        hour_bucket,
        street,
        zone,
        neighbourhood,
        district,
        borough_name,
        crash_count,
        persons_injured,
        persons_killed,
        pedestrians_injured,
        pedestrians_killed,
        cyclists_injured,
        cyclists_killed,
        motorists_injured,
        motorists_killed,
        crashes_with_coordinates,
        case
            when crash_count > 0 then persons_injured::numeric / crash_count
            else 0
        end as injury_rate_per_crash,
        case
            when crash_count > 0 then persons_killed::numeric / crash_count
            else 0
        end as fatality_rate_per_crash
    from crashes_daily
),

with_rolling as (
    select
        grid_cell_id,
        hour_bucket,
        street,
        zone,
        neighbourhood,
        district,
        borough_name,
        crash_count,
        persons_injured,
        persons_killed,
        pedestrians_injured,
        pedestrians_killed,
        cyclists_injured,
        cyclists_killed,
        motorists_injured,
        motorists_killed,
        crashes_with_coordinates,
        injury_rate_per_crash,
        fatality_rate_per_crash,
        -- rolling 7-day crash count (7 daily rows preceding + current)
        sum(crash_count) over (
            partition by grid_cell_id
            order by hour_bucket
            rows between 6 preceding and current row
        ) as crash_count_7d,
        -- rolling 30-day crash count
        sum(crash_count) over (
            partition by grid_cell_id
            order by hour_bucket
            rows between 29 preceding and current row
        ) as crash_count_30d,
        sum(persons_injured) over (
            partition by grid_cell_id
            order by hour_bucket
            rows between 6 preceding and current row
        ) as injuries_7d,
        sum(persons_killed) over (
            partition by grid_cell_id
            order by hour_bucket
            rows between 29 preceding and current row
        ) as fatalities_30d,
        avg(crash_count) over (
            partition by grid_cell_id
            order by hour_bucket
            rows between 6 preceding and current row
        ) as avg_daily_crashes_7d,
        -- pedestrian + cyclist combined vulnerable road user counts
        sum(pedestrians_injured + cyclists_injured) over (
            partition by grid_cell_id
            order by hour_bucket
            rows between 29 preceding and current row
        ) as vru_injured_30d
    from joined
)

select * from with_rolling
