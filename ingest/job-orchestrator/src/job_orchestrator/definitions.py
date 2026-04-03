from dagster import (
    AssetSelection,
    Definitions,
    definitions,
    define_asset_job,
    load_assets_from_modules,
)

from job_orchestrator.defs import assets as assets_module
from job_orchestrator.schedules import schedules

nyc_ingest_all_job = define_asset_job(
    name="nyc_ingest_all",
    selection=AssetSelection.groups("nyc_open_data"),
)

nyc_weather_job = define_asset_job(
    name="nyc_weather",
    selection=AssetSelection.assets(assets_module.nyc_weather_raw),
)


@definitions
def defs():
    return Definitions(
        assets=load_assets_from_modules([assets_module]),
        jobs=[nyc_ingest_all_job, nyc_weather_job],
        schedules=schedules,
    )
