{{ config(materialized='view', tags=['staging']) }}

select
    id,
    version,
    created_at,
    updated_at,
    nullif(trim(street), '') as street,
    postvz_sl::numeric as postvz_sl,
    nullif(trim(postvz_sg), '') as postvz_sg,
    shape_leng::numeric as shape_leng,
    geometry,
    ingested_at
from {{ source('raw', 'speed_limits_data') }}
