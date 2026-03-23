-- zone_map_data and district_grid_data: no null ids; exact expected row counts for NYC reference extracts.

{{ config(
    tags=['bronze', 'zone_map_data', 'district_grid_data']
) }}

{% set expected_zone_map_rows = 7 %}
{% set expected_district_grid_rows = 59 %}

select 'zone_map_data' as source_table, 'id_is_null' as failure_reason, id as detail
from {{ source('raw', 'zone_map_data') }}
where id is null

union all

select 'district_grid_data' as source_table, 'id_is_null' as failure_reason, id as detail
from {{ source('raw', 'district_grid_data') }}
where id is null

union all

select
    'zone_map_data' as source_table,
    'unexpected_row_count' as failure_reason,
    format('count=%s expected=%s', c, {{ expected_zone_map_rows }}) as detail
from (select count(*)::bigint as c from {{ source('raw', 'zone_map_data') }}) t
where c != {{ expected_zone_map_rows }}

union all

select
    'district_grid_data' as source_table,
    'unexpected_row_count' as failure_reason,
    format('count=%s expected=%s', c, {{ expected_district_grid_rows }}) as detail
from (select count(*)::bigint as c from {{ source('raw', 'district_grid_data') }}) t
where c != {{ expected_district_grid_rows }}
