-- Schema for the NYC Road Safety Analytics project

-- -- Drop tables if they exist
-- DROP TABLE IF EXISTS collisions;
-- DROP TABLE IF EXISTS intersections;
-- DROP TABLE IF EXISTS vehicles_involved;
-- DROP TABLE IF EXISTS persons_involved;

-- -- Drop indexes if they exist
-- DROP INDEX IF EXISTS idx_collisions_occurred_at;
-- DROP INDEX IF EXISTS idx_collisions_borough;
-- DROP INDEX IF EXISTS idx_vehicles_collision_id;
-- DROP INDEX IF EXISTS idx_persons_collision_id;
-- DROP INDEX IF EXISTS idx_intersections_borough;
-- DROP INDEX IF EXISTS idx_intersections_zip_code;

-- Schema for raw data table
CREATE TABLE raw_data (

    crash_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    crash_time VARCHAR(255) NOT NULL,
    borough VARCHAR(255),
    zip_code VARCHAR(5),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    location VARCHAR(255),
    on_street_name VARCHAR(255),
    cross_street_name VARCHAR(255),
    off_street_name VARCHAR(255),
    number_of_persons_injured INT,
    number_of_persons_killed INT,
    number_of_pedestrians_injured INT,
    number_of_pedestrians_killed INT,
    number_of_cyclist_injured INT,
    number_of_cyclist_killed INT,
    number_of_motorist_injured INT,
    number_of_motorist_killed INT,
    contributing_factor_vehicle_1 VARCHAR(255),
    contributing_factor_vehicle_2 VARCHAR(255),
    contributing_factor_vehicle_3 VARCHAR(255),
    contributing_factor_vehicle_4 VARCHAR(255),
    contributing_factor_vehicle_5 VARCHAR(255),
    collision_id VARCHAR(255),
    vehicle_type_code_1 VARCHAR(255),
    vehicle_type_code_2 VARCHAR(255),
    vehicle_type_code_3 VARCHAR(255),
    vehicle_type_code_4 VARCHAR(255),
    vehicle_type_code_5 VARCHAR(255),
    sys_crt_ts TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    sys_upd_ts TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Schema for collisions table
CREATE TABLE collisions (
    collision_pk UUID primary key,
    occurred_at TIMESTAMP WITH TIME ZONE NOT NULL,
    borough VARCHAR(255) NOT NULL,
    zip_code VARCHAR(5) NOT NULL,
    intersection_fk UUID NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    contributing_factor_vehicle_1 VARCHAR(255) NOT NULL,
    contributing_factor_vehicle_2 VARCHAR(255) NOT NULL,
    contributing_factor_vehicle_3 VARCHAR(255) NOT NULL,
    contributing_factor_vehicle_4 VARCHAR(255) NOT NULL,
    contributing_factor_vehicle_5 VARCHAR(255) NOT NULL,
    weather_condition VARCHAR(255) NOT NULL,
    temperature DECIMAL(5, 2) NOT NULL,
    precipitation DECIMAL(5, 2) NOT NULL,
    weather_fetch_status BOOLEAN NOT NULL,
    sys_crt_ts TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    sys_upd_ts TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Schema for intersections table
CREATE TABLE intersections (
    intersection_pk UUID primary key,
    street_1 VARCHAR(255) NOT NULL,
    street_2 VARCHAR(255) NOT NULL,
    borough VARCHAR(255) NOT NULL,
    zip_code VARCHAR(5) NOT NULL,
    sys_crt_ts TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    sys_upd_ts TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Schema for vehicles table
CREATE TABLE vehicles_involved (
    vehicle_involved_pk UUID primary key,
    collision_fk UUID NOT NULL,
    vehicle_type VARCHAR(255) NOT NULL,
    vehicle_action VARCHAR(255) NOT NULL,
    sys_crt_ts TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    sys_upd_ts TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Schema for persons_involved table
CREATE TABLE persons_involved (
    person_involved_pk UUID primary key,
    collision_fk UUID NOT NULL,
    person_type VARCHAR(255) NOT NULL,
    outcome VARCHAR(255) NOT NULL,
    sys_crt_ts TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    sys_upd_ts TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    injury_severity VARCHAR(255) NOT NULL,
    injury_type VARCHAR(255) NOT NULL
);

-- Indexes for tables
CREATE INDEX idx_collisions_occurred_at   ON collisions (occurred_at);
CREATE INDEX idx_collisions_borough       ON collisions (borough);
CREATE INDEX idx_vehicles_collision_id    ON vehicles_involved (collision_fk);
CREATE INDEX idx_persons_collision_id      ON persons_involved (collision_fk);
CREATE INDEX idx_intersections_borough     ON intersections (borough);
CREATE INDEX idx_intersections_zip_code   ON intersections (zip_code);
