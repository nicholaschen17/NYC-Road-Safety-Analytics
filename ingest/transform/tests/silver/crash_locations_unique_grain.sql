select collision_id, count(*)::bigint as row_count
from {{ ref('crash_locations') }}
group by 1
having count(*) > 1
