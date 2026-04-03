-- (grid_cell_id, hour_bucket) must be unique — the declared composite key of crash_features.
select grid_cell_id, hour_bucket, count(*)::bigint as row_count
from {{ ref('crash_features') }}
group by 1, 2
having count(*) > 1
