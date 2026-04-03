-- Physical weather quantities and treatment metrics must be >= 0.
-- Negative precipitation, snowfall, or salt tonnage indicates a bad source row or fill error.
{{ config(tags=['gold', 'env_features']) }}

select grid_cell_id, hour_bucket
from {{ ref('env_features') }}
where
    precipitation < 0
    or snowfall < 0
    or snow_depth < 0
    or rain < 0
    or total_tons_salted < 0
    or storm_events_count < 0
    or speed_hump_count < 0
