{{ config(unique_key=['hour_bucket', 'boro_key', 'segmentid_key'], tags=['silver']) }}

-- Resampled to clock-hour buckets for gold.traffic_features (README).
-- boro_key / segmentid_key: non-null merge keys (raw boro / segmentid may be null).

select
    date_trunc(
        'hour',
        make_timestamp(yr, m, d, hh, mm, 0::double precision)
    ) as hour_bucket,
    coalesce(boro, 'UNKNOWN') as boro_key,
    coalesce(segmentid::text, 'NULL_SEGMENT') as segmentid_key,
    boro,
    segmentid,
    sum(vol) as total_volume,
    count(*) as observation_count
from {{ ref('stg_traffic_volume_cnt_data') }}
group by 1, 2, 3, 4, 5
