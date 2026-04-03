-- All person/vehicle injury and death counts must be >= 0 (they are sums of raw NUMERIC fields).
{{ config(tags=['gold', 'crash_features']) }}

select grid_cell_id, hour_bucket
from {{ ref('crash_features') }}
where
    crash_count < 0
    or persons_injured < 0
    or persons_killed < 0
    or pedestrians_injured < 0
    or pedestrians_killed < 0
    or cyclists_injured < 0
    or cyclists_killed < 0
    or motorists_injured < 0
    or motorists_killed < 0
    or crashes_with_coordinates < 0
