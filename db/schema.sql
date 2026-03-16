-- Raw Tables
CREATE TABLE raw_salt_usage_data (
    -- Socrata system metadata columns
    id              TEXT,
    version         TEXT,
    created_at      TIMESTAMPTZ,
    updated_at      TIMESTAMPTZ,

    -- Source data columns
    dsny_storm       TEXT,
    date_of_report   TIMESTAMP,
    manhattan        NUMERIC,
    bronx            NUMERIC,
    brooklyn         NUMERIC,
    queens           NUMERIC,
    staten_island    NUMERIC,
    total_tons       NUMERIC,

    -- Audit column
    ingested_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
