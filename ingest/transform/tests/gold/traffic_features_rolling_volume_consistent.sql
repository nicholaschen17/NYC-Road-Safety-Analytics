-- volume_24h is a rolling 24-row sum that includes the current row, so it must be
-- >= total_volume for the same row. A violation indicates a window frame error.
{{ config(tags=['gold', 'traffic_features']) }}

select grid_cell_id, hour_bucket, total_volume, volume_24h
from {{ ref('traffic_features') }}
where volume_24h < total_volume
