select violation_day, jurisdiction_code, count(*)::bigint as row_count
from {{ ref('violations_daily') }}
group by 1, 2
having count(*) > 1
