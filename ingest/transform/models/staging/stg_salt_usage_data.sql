{{ config(materialized='view', tags=['staging']) }}

select
    id,
    version,
    created_at,
    updated_at,
    nullif(trim(dsny_storm), '') as dsny_storm,
    date_of_report::timestamp without time zone as date_of_report,
    manhattan::numeric as manhattan,
    bronx::numeric as bronx,
    brooklyn::numeric as brooklyn,
    queens::numeric as queens,
    staten_island::numeric as staten_island,
    total_tons::numeric as total_tons,
    ingested_at
from {{ source('raw', 'salt_usage_data') }}
