select district_grid_id
from {{ ref('districts') }}
where geometry is null
