-- (grid_cell_id, hour_bucket) must be unique — the declared composite key of traffic_features.
select grid_cell_id, hour_bucket, count(*)::bigint as row_count
from {{ ref('traffic_features') }}
group by 1, 2
having count(*) > 1
