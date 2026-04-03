-- Rolling window columns must be monotonically non-decreasing as the window widens:
--   crash_count_7d  >= crash_count   (7-row window includes the current row)
--   crash_count_30d >= crash_count_7d (30-row window always covers the 7-row window)
-- Violations here indicate a window-function logic error.
{{ config(tags=['gold', 'crash_features']) }}

select grid_cell_id, hour_bucket, crash_count, crash_count_7d, crash_count_30d
from {{ ref('crash_features') }}
where
    crash_count_7d < crash_count
    or crash_count_30d < crash_count_7d
