-- NYC five-borough approximate bounding box (WGS84). Many raw rows sit outside (null islands,
-- geocoding errors, or non-NYC jurisdictions); severity=warn keeps dbt build green while surfacing drift.
{{ config(
    tags=['bronze', 'crash_data', 'moving_violation_data'],
    severity='warn'
) }}

{% set lat_min = 40.53052 %}
{% set lat_max = 40.917577 %}
{% set lon_min = -74.042350 %}
{% set lon_max = -73.640572 %}


with
    crash_bad as (
        select
            'crash_data' as source_table,
            id,
            latitude,
            longitude
        from {{ source('raw', 'crash_data') }}
        where
            latitude is not null
            and longitude is not null
            and (
                latitude::double precision not between {{ lat_min }} and {{ lat_max }}
                or longitude::double precision not between {{ lon_min }} and {{ lon_max }}
            )
    ),
    violation_bad as (
        select
            'moving_violation_data' as source_table,
            id,
            latitude,
            longitude
        from {{ source('raw', 'moving_violation_data') }}
        where
            latitude is not null
            and longitude is not null
            and (
                latitude::double precision not between {{ lat_min }} and {{ lat_max }}
                or longitude::double precision not between {{ lon_min }} and {{ lon_max }}
            )
    )

select * from crash_bad
union all
select * from violation_bad
