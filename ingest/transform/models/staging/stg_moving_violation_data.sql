{{ config(materialized='view', tags=['staging']) }}

select
    id,
    version,
    created_at,
    updated_at,
    nullif(trim(evnt_key), '') as evnt_key,
    violation_date::timestamp without time zone as violation_date,
    nullif(trim(violation_time), '') as violation_time,
    nullif(trim(chg_law_cd), '') as chg_law_cd,
    nullif(trim(violation_code), '') as violation_code,
    nullif(trim(veh_category), '') as veh_category,
    nullif(trim(reg_plate_num), '') as reg_plate_num,
    nullif(trim(reg_state_cd), '') as reg_state_cd,
    nullif(trim(city_nm), '') as city_nm,
    nullif(trim(rpt_owning_cmd), '') as rpt_owning_cmd,
    x_coord_cd::double precision as x_coord_cd,
    y_coord_cd::double precision as y_coord_cd,
    latitude::double precision as latitude,
    longitude::double precision as longitude,
    nullif(trim(location_point), '') as location_point,
    nullif(trim(juris_cd), '') as juris_cd,
    geometry,
    ingested_at
from {{ source('raw', 'moving_violation_data') }}
