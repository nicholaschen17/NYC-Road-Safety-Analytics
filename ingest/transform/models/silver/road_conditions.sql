{{ config(unique_key='road_condition_sk', tags=['silver']) }}

-- Unified road-context layers (pavement rating, posted speed, humps) for zone drill-down context.
-- Common grain is "segment-ish" event; geometry present where raw provides GeoJSON.

select
    md5(concat_ws('|', 'street_rating', id::text)) as road_condition_sk,
    'street_rating'::text as condition_layer,
    id::text as source_row_id,
    boroughname as borough,
    onstreetna as street_name,
    geometry,
    systemrating as numeric_metric,
    'pavement_rating'::text as metric_type,
    inspection::timestamptz as observed_at,
    ingested_at
from {{ ref('stg_street_rating_data') }}

union all

select
    md5(concat_ws('|', 'speed_limits', id::text)),
    'speed_limits'::text,
    id::text,
    null::text,
    street,
    geometry,
    postvz_sl,
    'posted_speed_limit_mph'::text,
    ingested_at::timestamptz,
    ingested_at
from {{ ref('stg_speed_limits_data') }}

union all

select
    md5(concat_ws('|', 'speed_hump', id::text)),
    'speed_hump'::text,
    id::text,
    borough,
    onstreet,
    null::jsonb,
    null::numeric,
    'speed_hump_installation'::text,
    coalesce(installationdate::timestamptz, dateadded::timestamptz, ingested_at::timestamptz),
    ingested_at
from {{ ref('stg_speed_hump_data') }}
