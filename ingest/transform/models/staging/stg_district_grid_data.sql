{{ config(materialized='view', tags=['staging']) }}

select
    id,
    version,
    created_at,
    updated_at,
    nullif(trim(district), '') as district,
    nullif(trim(districtcode), '') as districtcode,
    nullif(trim(objectid), '') as objectid,
    shape_area::double precision as shape_area,
    shape_length::double precision as shape_length,
    geometry,
    ingested_at
from {{ source('raw', 'district_grid_data') }}
