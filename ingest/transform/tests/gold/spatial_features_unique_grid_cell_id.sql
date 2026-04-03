-- grid_cell_id must be unique within each snapshot — spatial_features is a zone-level
-- snapshot table, and duplicates within a run would mean the same zone was emitted twice.
select grid_cell_id, snapshot_ts, count(*)::bigint as row_count
from {{ ref('spatial_features') }}
group by 1, 2
having count(*) > 1
