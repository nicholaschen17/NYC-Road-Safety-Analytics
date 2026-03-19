from dagster import Definitions, load_assets_from_modules
from ingest_coordination_dagster.resources import NYCDataResource, WeatherDataResource, SourceConfigResource
from ingest_coordination_dagster import assets
from ingest_coordination_dagster.schedules import (
    nyc_open_data_ingest_all_job,
    zone_map_data_ingest_job,
    weather_data_ingest_job,
    weather_schedule,
    zone_map_schedule,
    nyc_open_data_schedule,
)
all_assets = load_assets_from_modules([assets])

defs = Definitions(
    assets=all_assets,
    resources={
        "nyc_data": NYCDataResource(),
        "weather_data_resource": WeatherDataResource(),
        "source_config": SourceConfigResource(),
    },
    jobs=[nyc_open_data_ingest_all_job, zone_map_data_ingest_job, weather_data_ingest_job],
    schedules=[weather_schedule, zone_map_schedule, nyc_open_data_schedule],
)