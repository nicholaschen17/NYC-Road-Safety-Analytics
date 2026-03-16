-- Drop all raw tables
DROP TABLE IF EXISTS raw_salt_usage_data, raw_speed_hump_data, raw_traffic_volume_cnt_data, raw_crash_data CASCADE;

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


CREATE TABLE raw_speed_hump_data (
    -- Socrata system metadata columns
    id                          TEXT,
    version                     TEXT,
    created_at                  TIMESTAMPTZ,
    updated_at                  TIMESTAMPTZ,

    -- Source data columns
    projectcode                 TEXT,
    groupowner                  TEXT,
    locationdescription         TEXT,
    borough                     TEXT,
    projectstatus               TEXT,
    nextstep                    TEXT,
    dateadded                   TIMESTAMP,
    bctsnum                     TEXT,
    ccunum                      TEXT,
    requestorletterreplydate    TIMESTAMP,
    cbletterrequestdate         TIMESTAMP,
    cbletterrecieveddate        TIMESTAMP,
    oldsign                     TEXT,
    newsign                     TEXT,
    markingsdate                TIMESTAMP,
    installationdate            TIMESTAMP,
    secondstudycode             TEXT,
    closeddate                  TIMESTAMP,
    speedcushion                TEXT,
    requestdate                 TIMESTAMP,
    requestortype               TEXT,
    segmentid                   TEXT,
    onstreet                    TEXT,
    fromstreet                  TEXT,
    tostreet                    TEXT,
    geoboroughname              TEXT,
    lionkey                     TEXT,
    fromlatitude                TEXT,
    fromlongitude               TEXT,
    tolatitude                  TEXT,
    tolongitude                 TEXT,
    oft                         TEXT,
    cb                          TEXT,
    segmentstatus               TEXT,
    segmentstatusdescription    TEXT,
    denialreason                TEXT,
    numsrproposed               NUMERIC,
    trafficdirection            TEXT,
    trafficdirectiondesc        TEXT,
    oldsign1                    TEXT,
    newsign1                    TEXT,
    oldsign2                    TEXT,
    newsign2                    TEXT,

    -- Audit column
    ingested_at                 TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE raw_traffic_volume_cnt_data (
    -- Socrata system metadata columns
    id              TEXT,
    version         TEXT,
    created_at      TIMESTAMPTZ,
    updated_at      TIMESTAMPTZ,

    -- Source data columns
    requestid       NUMERIC,
    boro            TEXT,
    yr              NUMERIC,
    m               NUMERIC,
    d               NUMERIC,
    hh              NUMERIC,
    mm              NUMERIC,
    vol             NUMERIC,
    segmentid       NUMERIC,
    wktgeom         TEXT,
    street          TEXT,
    fromst          TEXT,
    tost            TEXT,
    direction       TEXT,

    -- Audit column
    ingested_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE TABLE raw_crash_data (
    -- Socrata system metadata columns
    id                              TEXT,
    version                         TEXT,
    created_at                      TIMESTAMPTZ,
    updated_at                      TIMESTAMPTZ,

    -- Source data columns
    crash_date                      TIMESTAMP,
    crash_time                      TEXT,
    borough                         TEXT,
    zip_code                        TEXT,
    latitude                        NUMERIC,
    longitude                       NUMERIC,
    location                        TEXT,
    on_street_name                  TEXT,
    off_street_name                 TEXT,
    cross_street_name               TEXT,
    number_of_persons_injured       NUMERIC,
    number_of_persons_killed        NUMERIC,
    number_of_pedestrians_injured   NUMERIC,
    number_of_pedestrians_killed    NUMERIC,
    number_of_cyclist_injured       NUMERIC,
    number_of_cyclist_killed        NUMERIC,
    number_of_motorist_injured      NUMERIC,
    number_of_motorist_killed       NUMERIC,
    contributing_factor_vehicle_1   TEXT,
    contributing_factor_vehicle_2   TEXT,
    contributing_factor_vehicle_3   TEXT,
    contributing_factor_vehicle_4   TEXT,
    contributing_factor_vehicle_5   TEXT,
    collision_id                    NUMERIC,
    vehicle_type_code1              TEXT,
    vehicle_type_code2              TEXT,
    vehicle_type_code_3             TEXT,
    vehicle_type_code_4             TEXT,
    vehicle_type_code_5             TEXT,

    -- Audit column
    ingested_at                     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
