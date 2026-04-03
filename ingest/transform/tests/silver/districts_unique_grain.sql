select district_grid_id, count(*)::bigint as row_count
from {{ ref('districts') }}
group by 1
having count(*) > 1
