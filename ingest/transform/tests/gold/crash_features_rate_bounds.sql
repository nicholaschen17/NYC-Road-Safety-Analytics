-- Per-crash injury and fatality rates must be in [0, 1].
-- A rate > 1 would imply more deaths/injuries recorded than crashes, which is a data error.
{{ config(tags=['gold', 'crash_features']) }}

select grid_cell_id, hour_bucket, injury_rate_per_crash, fatality_rate_per_crash
from {{ ref('crash_features') }}
where
    injury_rate_per_crash < 0
    or injury_rate_per_crash > 1
    or fatality_rate_per_crash < 0
    or fatality_rate_per_crash > 1
