{{ config(
    unique_key=['grid_cell_id', 'snapshot_ts'],
    tags=['gold'],
    materialized='table',
    on_schema_change='sync_all_columns',
) }}

-- Spatial features. Grain: (grid_cell_id, snapshot_ts).
-- snapshot_ts is set to the current run timestamp so the table is append-friendly for versioning.
-- Feeds: zone drill-down infrastructure panel, SHAP explainability context, heatmap polygon overlays.
--
-- Bike-route proximity is aggregated at borough level; PostGIS ST_DWithin will enable
-- true segment-distance features once the geometry index is built.

with zone_base as (
    select
        grid_cell_id,
        zone,
        zonename,
        borocode,
        borough_name,
        shape_area,
        shape_length,
        centerpoint_latitude,
        centerpoint_longitude
    from {{ ref('grid_zones') }}
),

-- Map NYCOpenData borocode ('1'–'5') to the short boro code used in bike_route_segments.boro.
boro_code_map(borocode, boro_short) as (
    values
        ('1', 'M'),
        ('2', 'BX'),
        ('3', 'BK'),
        ('4', 'Q'),
        ('5', 'SI')
),

bike_by_boro as (
    select
        upper(trim(boro))                                           as boro_short,
        count(*)                                                    as total_bike_segments,
        sum(case when has_protected_facility then 1 else 0 end)    as protected_lane_segments,
        sum(coalesce(lanecount::int, 0))                           as total_lane_count,
        count(distinct bikeid)                                      as unique_bike_routes,
        count(distinct facilitycl) filter (where facilitycl is not null) as facility_class_count
    from {{ ref('bike_route_segments') }}
    where boro is not null
    group by 1
),

zone_with_bike as (
    select
        zb.grid_cell_id,
        zb.zone,
        zb.zonename,
        zb.borocode,
        zb.borough_name,
        zb.shape_area,
        zb.shape_length,
        zb.centerpoint_latitude,
        zb.centerpoint_longitude,
        coalesce(bb.total_bike_segments, 0)       as total_bike_segments,
        coalesce(bb.protected_lane_segments, 0)   as protected_lane_segments,
        coalesce(bb.total_lane_count, 0)          as total_lane_count,
        coalesce(bb.unique_bike_routes, 0)        as unique_bike_routes,
        coalesce(bb.facility_class_count, 0)      as facility_class_count,
        case
            when coalesce(bb.total_bike_segments, 0) > 0
            then bb.protected_lane_segments::numeric / bb.total_bike_segments
            else 0
        end                                        as protected_lane_ratio
    from zone_base as zb
    left join boro_code_map as bcm
        on zb.borocode = bcm.borocode
    left join bike_by_boro as bb
        on upper(bcm.boro_short) = bb.boro_short
)

select
    grid_cell_id,
    current_timestamp::timestamp                       as snapshot_ts,
    zone,
    zonename,
    borocode,
    borough_name,
    shape_area,
    shape_length,
    centerpoint_latitude,
    centerpoint_longitude,
    -- bike infrastructure proximity (borough-level proxy)
    total_bike_segments,
    protected_lane_segments,
    total_lane_count,
    unique_bike_routes,
    facility_class_count,
    protected_lane_ratio,
    -- zone topology / compactness features
    case
        when shape_area is not null then shape_area::numeric
        else null
    end                                                as zone_area_sqft,
    case
        when shape_length is not null
             and shape_area is not null
             and shape_area > 0
        then shape_length::numeric / sqrt(shape_area::numeric)
        else null
    end                                                as zone_compactness_ratio,
    -- binary flags for ML model inputs
    (protected_lane_segments > 0)                      as has_protected_bike_lane,
    (total_bike_segments > 0)                          as has_any_bike_infrastructure
from zone_with_bike
