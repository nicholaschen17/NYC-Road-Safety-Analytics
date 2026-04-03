-- All volume and count columns must be >= 0.
-- violation_count is coalesced from 0, so negative values indicate a source or join error.
{{ config(tags=['gold', 'traffic_features']) }}

select grid_cell_id, hour_bucket
from {{ ref('traffic_features') }}
where
    total_volume < 0
    or observation_count < 0
    or segment_count < 0
    or violation_count < 0
    or avg_volume_per_segment < 0
