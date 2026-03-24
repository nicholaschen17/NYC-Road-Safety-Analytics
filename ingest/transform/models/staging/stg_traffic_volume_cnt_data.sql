{{ config(materialized='view', tags=['staging']) }}

select
    id,
    version,
    created_at,
    updated_at,
    requestid::bigint as requestid,
    nullif(trim(boro), '') as boro,
    yr::int as yr,
    m::int as m,
    d::int as d,
    hh::int as hh,
    mm::int as mm,
    vol::numeric as vol,
    segmentid::bigint as segmentid,
    nullif(trim(wktgeom), '') as wktgeom,
    nullif(trim(street), '') as street,
    nullif(trim(fromst), '') as fromst,
    nullif(trim(tost), '') as tost,
    nullif(trim(direction), '') as direction,
    ingested_at
from {{ source('raw', 'traffic_volume_cnt_data') }}
where
    yr is not null
    and m between 1 and 12
    and d between 1 and 31
    and hh between 0 and 23
    and mm between 0 and 59
