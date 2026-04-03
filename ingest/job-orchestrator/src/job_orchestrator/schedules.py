"""Cron schedules for NYC ingest asset jobs (see defs/assets.py)."""

from dagster import DefaultScheduleStatus, ScheduleDefinition

# Job names must match define_asset_job(..., name=...) in definitions.py.
# STOPPED: enable runs from Deployment → Schedules when you are ready.

nyc_ingest_all_daily_schedule = ScheduleDefinition(
    name="nyc_ingest_all_daily",
    job_name="nyc_ingest_all",
    cron_schedule="0 6 * * *",
    execution_timezone="America/New_York",
    default_status=DefaultScheduleStatus.STOPPED,
)

nyc_weather_daily_schedule = ScheduleDefinition(
    name="nyc_weather_daily",
    job_name="nyc_weather",
    cron_schedule="0 7 * * *",
    execution_timezone="America/New_York",
    default_status=DefaultScheduleStatus.STOPPED,
)

schedules = [
    nyc_ingest_all_daily_schedule,
    nyc_weather_daily_schedule,
]
