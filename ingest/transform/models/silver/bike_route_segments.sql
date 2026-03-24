{{ config(unique_key='id', tags=['silver']) }}

-- Bike infrastructure with simple facility flags for gold.spatial_features / map overlays.

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
from {{ ref('stg_bike_route_data') }}
