from dagster import Definitions, EnvVar

from ingest_coordination_dagster.assets import (
    crash_data_asset,
    salt_usage_asset,
    bike_route_asset,
    district_grid_asset,
    moving_violation_asset,
    speed_hump_asset,
    speed_limits_asset,
    street_rating_asset,
    traffic_volume_asset,
)
from ingest_coordination_dagster.assets import raw_zone_map_data, zone_map_centerpoints
from ingest_coordination_dagster.assets import raw_weather_data
from ingest_coordination_dagster.resources import NYCDataResource, WeatherDataResource, SourceConfigResource

defs = Definitions(
    assets=[
        crash_data_asset,
        salt_usage_asset,
        bike_route_asset,
        district_grid_asset,
        moving_violation_asset,
        speed_hump_asset,
        speed_limits_asset,
        street_rating_asset,
        traffic_volume_asset,
        raw_zone_map_data,
        zone_map_centerpoints,
        raw_weather_data,
    ],
    resources={
        "nyc_data": NYCDataResource(),
        "source_config": SourceConfigResource(
            nyc_app_token=EnvVar("NYC_APP_TOKEN"),
        ),
        "weather_data_resource": WeatherDataResource(),
    },
)