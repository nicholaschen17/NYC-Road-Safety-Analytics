select hour_bucket, boro_key, segmentid_key, count(*)::bigint as row_count
from {{ ref('traffic_vol_hourly') }}
group by 1, 2, 3
having count(*) > 1
