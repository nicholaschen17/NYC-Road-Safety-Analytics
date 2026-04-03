{{ config(
    unique_key=['grid_cell_id', 'hour_bucket'],
    tags=['gold'],
    materialized='table',
    on_schema_change='sync_all_columns',
) }}

-- Crash feature aggregations. Grain: (grid_cell_id, hour_bucket).
-- Feeds: main heatmap risk score, zone drill-down injury panel, incident explorer timeline.
--
-- grid_cell_id is a borough-level proxy (first representative zone per borough) until the
-- PostGIS ST_Contains point-in-polygon join is wired in a later model. Replace the
-- borough_grid CTE with a spatial join on crashes.latitude/longitude once available.

with crashes_daily as (
    select
        coalesce(upper(trim(borough)), 'UNKNOWN')   as borough_upper,
        date_trunc('day', crash_date)::timestamp    as hour_bucket,
        count(*)                                    as crash_count,
        sum(coalesce(number_of_persons_injured, 0)) as persons_injured,
        sum(coalesce(number_of_persons_killed, 0))  as persons_killed,
        sum(coalesce(number_of_pedestrians_injured, 0)) as pedestrians_injured,
        sum(coalesce(number_of_pedestrians_killed, 0))  as pedestrians_killed,
        sum(coalesce(number_of_cyclist_injured, 0))     as cyclists_injured,
        sum(coalesce(number_of_cyclist_killed, 0))      as cyclists_killed,
        sum(coalesce(number_of_motorist_injured, 0))    as motorists_injured,
        sum(coalesce(number_of_motorist_killed, 0))     as motorists_killed,
        count(*) filter (where has_coordinates)         as crashes_with_coordinates
    from {{ ref('crashes') }}
    where crash_date is not null
    group by 1, 2
),

-- One representative grid_cell_id per borough (proxy until PostGIS spatial join).
borough_grid as (
    select distinct on (upper(trim(borough_name)))
        upper(trim(borough_name)) as borough_upper,
        grid_cell_id
    from {{ ref('grid_zones') }}
    where borough_name is not null
    order by upper(trim(borough_name)), grid_cell_id
),

joined as (
    select
        coalesce(bg.grid_cell_id, 'borough:' || cd.borough_upper) as grid_cell_id,
        cd.hour_bucket,
        cd.crash_count,
        cd.persons_injured,
        cd.persons_killed,
        cd.pedestrians_injured,
        cd.pedestrians_killed,
        cd.cyclists_injured,
        cd.cyclists_killed,
        cd.motorists_injured,
        cd.motorists_killed,
        cd.crashes_with_coordinates,
        case
            when cd.crash_count > 0 then cd.persons_injured::numeric / cd.crash_count
            else 0
        end as injury_rate_per_crash,
        case
            when cd.crash_count > 0 then cd.persons_killed::numeric / cd.crash_count
            else 0
        end as fatality_rate_per_crash
    from crashes_daily as cd
    left join borough_grid as bg on cd.borough_upper = bg.borough_upper
),

with_rolling as (
    select
        grid_cell_id,
        hour_bucket,
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
