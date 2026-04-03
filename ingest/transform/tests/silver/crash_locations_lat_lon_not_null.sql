select collision_id, latitude, longitude
from {{ ref('crash_locations') }}
where latitude is null or longitude is null
