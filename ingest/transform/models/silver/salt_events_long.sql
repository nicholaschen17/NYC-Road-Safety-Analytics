{{ config(unique_key='salt_event_sk', tags=['silver']) }}

-- Winter treatment log in long format (storm × borough) for env / intervention analysis.

select
    md5(
        concat_ws(
            '|',
            id::text,
            'Manhattan',
            coalesce(dsny_storm, ''),
            coalesce(date_of_report::text, '')
        )
    ) as salt_event_sk,
    id,
    dsny_storm,
    date_of_report,
    'Manhattan' as borough_name,
    manhattan as tons_salted,
    ingested_at
from {{ ref('stg_salt_usage_data') }}
where manhattan is not null and manhattan > 0

union all

select
    md5(
        concat_ws(
            '|',
            id::text,
            'Bronx',
            coalesce(dsny_storm, ''),
            coalesce(date_of_report::text, '')
        )
    ),
    id,
    dsny_storm,
    date_of_report,
    'Bronx',
    bronx,
    ingested_at
from {{ ref('stg_salt_usage_data') }}
where bronx is not null and bronx > 0

union all

select
    md5(
        concat_ws(
            '|',
            id::text,
            'Brooklyn',
            coalesce(dsny_storm, ''),
            coalesce(date_of_report::text, '')
        )
    ),
    id,
    dsny_storm,
    date_of_report,
    'Brooklyn',
    brooklyn,
    ingested_at
from {{ ref('stg_salt_usage_data') }}
where brooklyn is not null and brooklyn > 0

union all

select
    md5(
        concat_ws(
            '|',
            id::text,
            'Queens',
            coalesce(dsny_storm, ''),
            coalesce(date_of_report::text, '')
        )
    ),
    id,
    dsny_storm,
    date_of_report,
    'Queens',
    queens,
    ingested_at
from {{ ref('stg_salt_usage_data') }}
where queens is not null and queens > 0

union all

select
    md5(
        concat_ws(
            '|',
            id::text,
            'Staten Island',
            coalesce(dsny_storm, ''),
            coalesce(date_of_report::text, '')
        )
    ),
    id,
    dsny_storm,
    date_of_report,
    'Staten Island',
    staten_island,
    ingested_at
from {{ ref('stg_salt_usage_data') }}
where staten_island is not null and staten_island > 0
