-- Bike infrastructure counts and ratio must be non-negative.
-- Negative values are impossible; they would indicate a coalesce / arithmetic error.
{{ config(tags=['gold', 'spatial_features']) }}

select grid_cell_id
from {{ ref('spatial_features') }}
where
    total_bike_segments < 0
    or protected_lane_segments < 0
    or total_lane_count < 0
    or unique_bike_routes < 0
    or protected_lane_ratio < 0
