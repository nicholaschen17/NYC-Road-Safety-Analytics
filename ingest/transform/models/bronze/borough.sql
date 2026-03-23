{{ config(
    materialized='table',
    schema='raw',
    tags=['bronze', 'borough']
) }}

-- Reference dimension: NYC DOF / DSNY-style borocode (no raw ingest table).
-- Join downstream to raw.zone_map_data.borocode, raw.crash_data.borough (name), etc.

select
    borocode,
    borough_name,
    borough_abbr
from (
    values
        ('1', 'Manhattan', 'MN'),
        ('2', 'Bronx', 'BX'),
        ('3', 'Brooklyn', 'BK'),
        ('4', 'Queens', 'QN'),
        ('5', 'Staten Island', 'SI')
) as t (borocode, borough_name, borough_abbr)
