{{ config(unique_key='collision_id', tags=['silver']) }}

-- One row per collision_id (deduped). Supports main crash heatmap + incident explorer wireframes.
-- Assigning grid_cell_id via ST_Contains is deferred (needs geometry parse + index in a later model).

with ranked as (
    select
        stg.*,
        row_number() over (
            partition by stg.collision_id
            order by coalesce(stg.updated_at, stg.ingested_at) desc nulls last
        ) as _rn
    from {{ ref('stg_crash_data') }} as stg
    where stg.collision_id is not null
)

select
    id,
    collision_id,
    crash_date,
    crash_time,
    borough,
    zip_code,
    latitude,
    longitude,
    (latitude is not null and longitude is not null) as has_coordinates,
    location,
    on_street_name,
    off_street_name,
    cross_street_name,
    number_of_persons_injured,
    number_of_persons_killed,
    number_of_pedestrians_injured,
    number_of_pedestrians_killed,
    number_of_cyclist_injured,
    number_of_cyclist_killed,
    number_of_motorist_injured,
    number_of_motorist_killed,
    contributing_factor_vehicle_1,
    contributing_factor_vehicle_2,
    contributing_factor_vehicle_3,
    contributing_factor_vehicle_4,
    contributing_factor_vehicle_5,
    vehicle_type_code1,
    vehicle_type_code2,
    vehicle_type_code_3,
    vehicle_type_code_4,
    vehicle_type_code_5,
    ingested_at
from ranked
where _rn = 1
