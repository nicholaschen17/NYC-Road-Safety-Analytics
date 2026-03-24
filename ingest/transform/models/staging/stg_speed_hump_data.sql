{{ config(materialized='view', tags=['staging']) }}

select
    id,
    version,
    created_at,
    updated_at,
    nullif(trim(projectcode), '') as projectcode,
    nullif(trim(borough), '') as borough,
    nullif(trim(onstreet), '') as onstreet,
    nullif(trim(fromstreet), '') as fromstreet,
    nullif(trim(tostreet), '') as tostreet,
    nullif(trim(segmentid), '') as segmentid,
    nullif(trim(lionkey), '') as lionkey,
    dateadded::timestamp without time zone as dateadded,
    installationdate::timestamp without time zone as installationdate,
    ingested_at
from {{ source('raw', 'speed_hump_data') }}
