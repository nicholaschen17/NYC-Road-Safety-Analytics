-- raw.crash_data: injury / death count columns must be >= 0 when present (db/init.sql NUMERIC fields).
{{ config(
    tags=['bronze', 'crash_data']
) }}

select
    id,
    number_of_persons_injured,
    number_of_persons_killed,
    number_of_pedestrians_injured,
    number_of_pedestrians_killed,
    number_of_cyclist_injured,
    number_of_cyclist_killed,
    number_of_motorist_injured,
    number_of_motorist_killed
from {{ source('raw', 'crash_data') }}
where
    (number_of_persons_injured is not null and number_of_persons_injured < 0)
    or (number_of_persons_killed is not null and number_of_persons_killed < 0)
    or (number_of_pedestrians_injured is not null and number_of_pedestrians_injured < 0)
    or (number_of_pedestrians_killed is not null and number_of_pedestrians_killed < 0)
    or (number_of_cyclist_injured is not null and number_of_cyclist_injured < 0)
    or (number_of_cyclist_killed is not null and number_of_cyclist_killed < 0)
    or (number_of_motorist_injured is not null and number_of_motorist_injured < 0)
    or (number_of_motorist_killed is not null and number_of_motorist_killed < 0)
