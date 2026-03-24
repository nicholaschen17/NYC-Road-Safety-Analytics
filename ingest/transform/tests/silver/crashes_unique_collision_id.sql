select collision_id, count(*)::bigint as row_count
from {{ ref('crashes') }}
group by 1
having count(*) > 1
