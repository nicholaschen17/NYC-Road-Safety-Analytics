{{ config(
    unique_key='id',
    tags=['silver'],
    materialized='view',
    on_schema_change='sync_all_columns',
) }}

-- Bike infrastructure with simple facility flags for gold.spatial_features / map overlays.

with base as (
    select
        id,
        segmentid,
        bikeid,
        status,
        boro,
        street,
        fromstreet,
        tostreet,
        facilitycl,
        allclasses,
        bikedir,
        lanecount,
        geometry,
        ingested_at,
        updated_at
    from {{ ref('stg_bike_route_data') }}
    where id is not null
),
ranked as (
    select
        *,
        row_number() over (
            partition by id
            order by ingested_at desc nulls last, updated_at desc nulls last
        ) as _rn
    from base
)
select
    id,
    segmentid,
    bikeid,
    status,
    boro,
    street,
    fromstreet,
    tostreet,
    facilitycl,
    allclasses,
    bikedir,
    lanecount,
    geometry,
    upper(coalesce(facilitycl, '')) like '%PBL%'
    or upper(coalesce(facilitycl, '')) like '%PROTECTED%' as has_protected_facility,
    coalesce(nullif(trim(facilitycl), ''), '') != '' as has_facility_class,
    ingested_at
from ranked
where _rn = 1
