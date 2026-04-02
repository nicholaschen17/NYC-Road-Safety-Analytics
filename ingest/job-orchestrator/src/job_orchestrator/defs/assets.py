"""Dagster assets wrapping NYC ingest scripts."""

from dagster import asset

from job_orchestrator.ingest_scripts import ingest_nyc_bike_route_data as bike
from job_orchestrator.ingest_scripts import ingest_nyc_crash_data as crash
from job_orchestrator.ingest_scripts import ingest_nyc_district_grid_data as district
from job_orchestrator.ingest_scripts import ingest_nyc_moving_violation_data as violations
from job_orchestrator.ingest_scripts import ingest_nyc_salt_usage_data as salt
from job_orchestrator.ingest_scripts import ingest_nyc_speed_hump_data as speed_humps
from job_orchestrator.ingest_scripts import ingest_nyc_speed_limits_data as speed_limits
from job_orchestrator.ingest_scripts import ingest_nyc_street_rating_data as street_rating
from job_orchestrator.ingest_scripts import ingest_nyc_traffic_volume_cnt_data as traffic
from job_orchestrator.ingest_scripts import ingest_nyc_weather_data as weather
from job_orchestrator.ingest_scripts import ingest_nyc_zone_map_data as zone_map


@asset(group_name="nyc_open_data")
def nyc_crash_raw():
    crash.get_crash_data_from_api()


@asset(group_name="nyc_open_data")
def nyc_salt_usage_raw():
    salt.get_salt_usage_data_from_api()


@asset(group_name="nyc_weather")
def nyc_weather_raw():
    weather.main()


@asset(group_name="nyc_open_data")
def nyc_bike_route_raw():
    bike.get_bike_route_data_from_api()


@asset(group_name="nyc_open_data")
def nyc_district_grid_raw():
    district.get_district_grid_data_from_api()


@asset(group_name="nyc_open_data")
def nyc_moving_violation_raw():
    violations.get_moving_violation_data_from_api()


@asset(group_name="nyc_open_data")
def nyc_speed_hump_raw():
    speed_humps.get_speed_hump_data_from_api()


@asset(group_name="nyc_open_data")
def nyc_speed_limits_raw():
    speed_limits.get_speed_limits_data_from_api()


@asset(group_name="nyc_open_data")
def nyc_street_rating_raw():
    street_rating.get_street_rating_data_from_api()


@asset(group_name="nyc_open_data")
def nyc_traffic_volume_raw():
    traffic.get_traffic_volume_cnt_data_from_api()


@asset(group_name="nyc_open_data")
def nyc_zone_map_raw():
    zone_map.get_zone_map_data_from_api()


@asset(deps=[nyc_zone_map_raw], group_name="nyc_open_data")
def nyc_zone_map_centerpoints():
    zone_map.populate_centerpoint_zone_data()
