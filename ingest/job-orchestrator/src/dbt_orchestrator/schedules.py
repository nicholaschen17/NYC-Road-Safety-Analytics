from dagster import DefaultScheduleStatus, ScheduleDefinition

materialize_dbt_models_daily_schedule = ScheduleDefinition(
    name="materialize_dbt_models_daily",
    job_name="materialize_dbt_models",
    cron_schedule="0 0 * * *",
    execution_timezone="America/New_York",
    default_status=DefaultScheduleStatus.STOPPED,
)

schedules = [materialize_dbt_models_daily_schedule]
