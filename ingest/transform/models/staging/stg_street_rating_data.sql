{{ config(materialized='view', tags=['staging']) }}

select
    id,
    version,
    created_at,
    updated_at,
    nullif(trim(oftcode), '') as oftcode,
    nullif(trim(boroughname), '') as boroughname,
    nullif(trim(onstreetna), '') as onstreetna,
    nullif(trim(fromstreet), '') as fromstreet,
    nullif(trim(tostreetna), '') as tostreetna,
    ismultipass::numeric as ismultipass,
    nullif(trim(direction), '') as direction,
    nullif(trim(road_type), '') as road_type,
    systemrating::numeric as systemrating,
    nullif(trim(nonratingreason), '') as nonratingreason,
    inspection::timestamp without time zone as inspection,
    locationgeometry_stlength::numeric as locationgeometry_stlength,
    geometry,
    ingested_at
from {{ source('raw', 'street_rating_data') }}
