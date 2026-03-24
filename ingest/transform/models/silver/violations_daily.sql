{{ config(unique_key=['violation_day', 'jurisdiction_code'], tags=['silver']) }}

-- Aggregated violations for dashboards / export center; grain: day × jurisdiction code.

select
    (violation_date::date) as violation_day,
    coalesce(nullif(trim(juris_cd), ''), 'UNKNOWN') as jurisdiction_code,
    count(*) as violation_count
from {{ ref('stg_moving_violation_data') }}
where violation_date is not null
group by 1, 2
