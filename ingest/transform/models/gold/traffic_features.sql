{{ config(
    unique_key=['grid_cell_id', 'hour_bucket'],
    tags=['gold'],
    materialized='table',
    on_schema_change='sync_all_columns',
) }}

-- Traffic features. Grain: (grid_cell_id, hour_bucket).
-- Feeds: main heatmap traffic overlay, zone drill-down volume panel, reporting export center.
--
-- Traffic volume joined to grid_zones via borough-code normalisation.
-- Violations (daily grain) are broadcast across all hours of the matching day.
-- Replace borough proxy with segment-level spatial join once PostGIS index is available.

with boro_map(boro_code, borough_upper) as (
    values
        ('M',       'MANHATTAN'),
        ('MN',      'MANHATTAN'),
        ('BX',      'BRONX'),
        ('BRONX',   'BRONX'),
        ('BK',      'BROOKLYN'),
        ('BROOKLYN','BROOKLYN'),
        ('Q',       'QUEENS'),
        ('QN',      'QUEENS'),
        ('QUEENS',  'QUEENS'),
        ('SI',      'STATEN ISLAND'),
        ('STATEN ISLAND', 'STATEN ISLAND'),
        ('UNKNOWN', 'UNKNOWN')
),

traffic_borough as (
    select
        coalesce(bm.borough_upper, upper(tv.boro_key)) as borough_upper,
        tv.hour_bucket,
        sum(tv.total_volume)                           as total_volume,
        sum(tv.observation_count)                      as observation_count,
        count(distinct tv.segmentid_key)               as segment_count
    from {{ ref('traffic_vol_hourly') }} as tv
    left join boro_map as bm on upper(tv.boro_key) = bm.boro_code
    group by 1, 2
),

violations_borough as (
    select
        upper(trim(jurisdiction_code))  as jurisdiction_code,
        violation_day,
        sum(violation_count)            as violation_count
    from {{ ref('violations_daily') }}
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
        coalesce(bg.grid_cell_id, 'borough:' || tb.borough_upper) as grid_cell_id,
        tb.hour_bucket,
        tb.total_volume,
        tb.observation_count,
        tb.segment_count,
        -- violations are daily; broadcast to each hour in the day
        coalesce(vb.violation_count, 0)                            as violation_count,
        case
            when tb.segment_count > 0
            then tb.total_volume::numeric / tb.segment_count
            else 0
        end as avg_volume_per_segment
    from traffic_borough as tb
    left join borough_grid as bg
        on tb.borough_upper = bg.borough_upper
    left join violations_borough as vb
        on tb.borough_upper = vb.jurisdiction_code
        and tb.hour_bucket::date = vb.violation_day
),

with_rolling as (
    select
        grid_cell_id,
        hour_bucket,
        total_volume,
        observation_count,
        segment_count,
        violation_count,
        avg_volume_per_segment,
        -- rolling 24h total volume (congestion signal)
        sum(total_volume) over (
            partition by grid_cell_id
            order by hour_bucket
            rows between 23 preceding and current row
        ) as volume_24h,
        -- rolling 7-day average hourly volume (baseline)
        avg(total_volume) over (
            partition by grid_cell_id
            order by hour_bucket
            rows between 167 preceding and current row
        ) as avg_hourly_volume_7d,
        -- rolling 7-day violation count
        sum(violation_count) over (
            partition by grid_cell_id
            order by hour_bucket
            rows between 167 preceding and current row
        ) as violations_7d,
        -- volume deviation from 7d baseline (congestion spike indicator)
        total_volume - avg(total_volume) over (
            partition by grid_cell_id
            order by hour_bucket
            rows between 167 preceding and current row
        ) as volume_vs_7d_avg
    from joined
)

select * from with_rolling
