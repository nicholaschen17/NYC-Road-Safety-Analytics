-- Geocoding errors and edge cases can sit outside the five-borough box; warn-only like raw crash lat/lon test.
{{ config(severity='warn') }}

{% set lat_min = 40.53052 %}
{% set lat_max = 40.917577 %}
{% set lon_min = -74.042350 %}
{% set lon_max = -73.640572 %}

select collision_id, latitude, longitude
from {{ ref('crash_locations') }}
where
    latitude::double precision not between {{ lat_min }} and {{ lat_max }}
    or longitude::double precision not between {{ lon_min }} and {{ lon_max }}
