-- Every crash_locations row must come from a crash that still has coordinates in silver crashes.
select cl.collision_id
from {{ ref('crash_locations') }} as cl
inner join {{ ref('crashes') }} as c on c.collision_id = cl.collision_id
where c.latitude is null or c.longitude is null
