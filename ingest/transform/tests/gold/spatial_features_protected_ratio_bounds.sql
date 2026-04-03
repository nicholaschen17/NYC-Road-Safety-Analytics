-- protected_lane_ratio = protected_lane_segments / total_bike_segments must be in [0, 1].
-- A ratio > 1 means more protected segments than total segments — an arithmetic impossibility.
{{ config(tags=['gold', 'spatial_features']) }}

select grid_cell_id, total_bike_segments, protected_lane_segments, protected_lane_ratio
from {{ ref('spatial_features') }}
where
    protected_lane_ratio > 1
    or protected_lane_segments > total_bike_segments
