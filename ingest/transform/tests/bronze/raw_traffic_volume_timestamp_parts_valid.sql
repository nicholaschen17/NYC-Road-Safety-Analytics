-- raw.traffic_volume_cnt_data: calendar/time parts and volume sanity (db/init.sql yr, m, d, hh, mm, vol).
-- A few bad source rows are common; warn-only so ingest pipelines are not blocked.

{{ config(
    tags=['bronze', 'traffic_volume_cnt_data'],
    severity='warn'
) }}

select
    id,
    yr,
    m,
    d,
    hh,
    mm,
    vol
from {{ source('raw', 'traffic_volume_cnt_data') }}
where
    (m is not null and (m < 1 or m > 12))
    or (d is not null and (d < 1 or d > 31))
    or (hh is not null and (hh < 0 or hh > 23))
    or (mm is not null and (mm < 0 or mm > 59))
    or (vol is not null and vol < 0)
