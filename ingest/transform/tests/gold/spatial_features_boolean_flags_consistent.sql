-- Boolean infrastructure flags must be consistent with their underlying counts:
--   has_protected_bike_lane  = true  iff protected_lane_segments > 0
--   has_any_bike_infrastructure = true iff total_bike_segments > 0
-- Mismatches indicate a derived-column logic error.
{{ config(tags=['gold', 'spatial_features']) }}

select grid_cell_id, total_bike_segments, protected_lane_segments,
       has_any_bike_infrastructure, has_protected_bike_lane
from {{ ref('spatial_features') }}
where
    (has_any_bike_infrastructure  = true  and total_bike_segments    = 0)
    or (has_any_bike_infrastructure  = false and total_bike_segments    > 0)
    or (has_protected_bike_lane      = true  and protected_lane_segments = 0)
    or (has_protected_bike_lane      = false and protected_lane_segments > 0)
