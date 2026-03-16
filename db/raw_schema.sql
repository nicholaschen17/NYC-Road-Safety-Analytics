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

CREATE TABLE raw_bike_route_data (
    -- Socrata system metadata columns
    id              TEXT,
    version         TEXT,
    created_at      TIMESTAMPTZ,
    updated_at      TIMESTAMPTZ,

    -- Source data columns
    segmentid       TEXT,
    bikeid          TEXT,
    prevbikeid      TEXT,
    status          TEXT,
    boro            TEXT,
    street          TEXT,
    fromstreet      TEXT,
    tostreet        TEXT,
    onoffst         TEXT,
    facilitycl      TEXT,
    allclasses      TEXT,
    bikedir         TEXT,
    lanecount       NUMERIC,
    ft_facilit      TEXT,
    tf_facilit      TEXT,
    ft2facilit      TEXT,
    tf2facilit      TEXT,
    instdate        TEXT,
    ret_date        TEXT,
    grnwy           TEXT,
    gwsystem        TEXT,
    gwsys2          TEXT,
    spur            TEXT,
    gwyjuris        TEXT,
    geometry        TEXT,

    -- Audit column
    ingested_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE raw_district_grid_data (
    -- Socrata system metadata columns
    id              TEXT,
    version         TEXT,
    created_at      TIMESTAMPTZ,
    updated_at      TIMESTAMPTZ,

    -- Source data columns
    district        TEXT,
    districtcode    TEXT,
    objectid        TEXT,
    shape_area      NUMERIC,
    shape_length    NUMERIC,
    geometry        TEXT,

    -- Audit column
    ingested_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

/*
CREATE TABLE raw_moving_violation_data (
    -- Socrata system metadata columns
    id              TEXT,
    version         TEXT,
    created_at      TIMESTAMPTZ,
    updated_at      TIMESTAMPTZ,

    -- Source data columns
    evnt_key        TEXT,
    violation_date  TIMESTAMP,
    violation_time  TEXT,
    chg_law_cd      TEXT,
    violation_code  TEXT,
    veh_category    TEXT,
    reg_plate_num   TEXT,
    reg_state_cd    TEXT,
    city_nm         TEXT,
    rpt_owning_cmd  TEXT,
    x_coord_cd      NUMERIC,
    y_coord_cd      NUMERIC,
    latitude        NUMERIC,
    longitude       NUMERIC,
    location_point  TEXT,
    juris_cd        TEXT,
    geometry        TEXT,

    -- Audit column
    ingested_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
*/

CREATE TABLE raw_speed_limits_data (
    -- Socrata system metadata columns
    id              TEXT,
    version         TEXT,
    created_at      TIMESTAMPTZ,
    updated_at      TIMESTAMPTZ,

    -- Source data columns
    street          TEXT,
    postvz_sl       NUMERIC,
    postvz_sg       TEXT,
    shape_leng      NUMERIC,
    geometry        TEXT,

    -- Audit column
    ingested_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE raw_street_rating_data (
    -- Socrata system metadata columns
    id                          TEXT,
    version                     TEXT,
    created_at                  TIMESTAMPTZ,
    updated_at                  TIMESTAMPTZ,

    -- Source data columns
    oftcode                     TEXT,
    boroughname                 TEXT,
    onstreetna                  TEXT,
    fromstreet                  TEXT,
    tostreetna                  TEXT,
    ismultipass                 NUMERIC,
    direction                   TEXT,
    road_type                   TEXT,
    systemrating                NUMERIC,
    nonratingreason             TEXT,
    inspection                  TIMESTAMP,
    locationgeometry_stlength   NUMERIC,
    geometry                    TEXT,

    -- Audit column
    ingested_at                 TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE raw_zone_map_data (
    -- Socrata system metadata columns
    id              TEXT,
    version         TEXT,
    created_at      TIMESTAMPTZ,
    updated_at      TIMESTAMPTZ,

    -- Source data columns
    zone            TEXT,
    zonename        TEXT,
    borocode        TEXT,
    objectid        TEXT,
    shape_area      NUMERIC,
    shape_length    NUMERIC,
    geometry        TEXT,

    -- Audit column
    ingested_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);