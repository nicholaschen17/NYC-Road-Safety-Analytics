-- Derived boolean risk flags must not be NULL — NULL would silently drop rows from ML feature joins.
-- is_snow_event, is_heavy_rain, is_below_freezing, and salt_treatment_active are all
-- computed with coalesce() so they should always resolve to true or false.
{{ config(tags=['gold', 'env_features']) }}

select grid_cell_id, hour_bucket
from {{ ref('env_features') }}
where
    is_snow_event is null
    or is_heavy_rain is null
    or is_below_freezing is null
    or salt_treatment_active is null
