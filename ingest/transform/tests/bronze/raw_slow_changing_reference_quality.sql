-- zone_map_data and district_grid_data: no null ids.
-- Row counts are not asserted: raw is append-only, so totals grow with re-ingests.

{{ config(
    tags=['bronze', 'zone_map_data', 'district_grid_data']
) }}

select 'zone_map_data' as source_table, 'id_is_null' as failure_reason, id as detail
from {{ source('raw', 'zone_map_data') }}
where id is null

union all

select 'district_grid_data' as source_table, 'id_is_null' as failure_reason, id as detail
from {{ source('raw', 'district_grid_data') }}
where id is null
