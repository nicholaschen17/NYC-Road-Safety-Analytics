-- Raw tables are append-only: the same Socrata id or weather grain may appear many times across
-- ingests. Uniqueness is enforced downstream in silver (dedupe / merge keys), not in raw.
{{ config(
    tags=['bronze']
) }}

select 1 as _no_raw_uniqueness_assertion
where false
