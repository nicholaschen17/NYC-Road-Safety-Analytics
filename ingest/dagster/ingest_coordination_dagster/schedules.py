from dagster import define_asset_job, ScheduleDefinition, AssetSelection

nyc_open_data_ingest_all_job = define_asset_job(
    name="nyc_open_data_ingest_all_job",
    selection=AssetSelection.groups("raw_nyc_data") - AssetSelection.assets("raw_zone_map_data", "zone_map_centerpoints"),
    description="Ingest all standard (non-dependent) NYC Open Data sources",
)

zone_map_data_ingest_job = define_asset_job(
    name="zone_map_data_ingest_job",
    selection=AssetSelection.assets("raw_zone_map_data", "zone_map_centerpoints"),
    description="Ingest zone map and compute centerpoints",
)

weather_data_ingest_job = define_asset_job(
    name="weather_data_ingest_job",
    selection=AssetSelection.groups("raw_weather"),
    description="Ingest weather data from Open-Meteo for all zones",
)

# Schedules

weather_schedule = ScheduleDefinition(
    job=weather_data_ingest_job,
    cron_schedule="0 0 * * *",
    description="Ingest weather data from Open-Meteo for all zones every day at midnight",
)

zone_map_schedule = ScheduleDefinition(
    job=zone_map_data_ingest_job,
    cron_schedule="0 0 1 1 *",
    description="Ingest zone map data from NYC Open Data every year on January 1st at midnight",
)

nyc_open_data_schedule = ScheduleDefinition(
    job=nyc_open_data_ingest_all_job,
    cron_schedule="0 0 * * *",
    description="Ingest all standard (non-dependent) NYC Open Data sources every day at midnight",
)