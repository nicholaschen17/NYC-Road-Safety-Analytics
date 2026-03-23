{{ config(
    tags=['bronze', 'borough']
) }}

select format('borough model has %s rows, expected 5', c) as detail
from (select count(*)::bigint as c from {{ ref('borough') }}) t
where c != 5