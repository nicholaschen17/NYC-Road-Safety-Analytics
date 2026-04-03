{% macro geojson_to_geom(column_expr) -%}
ST_SetSRID(ST_GeomFromGeoJSON({{ column_expr }}::text), 4326)
{%- endmacro %}

{# Point for spatial joins (WGS84). Prefer over ST_Point for planner familiarity. #}
{% macro wgs84_point(lon_expr, lat_expr) -%}
ST_SetSRID(ST_MakePoint({{ lon_expr }}, {{ lat_expr }}), 4326)
{%- endmacro %}
