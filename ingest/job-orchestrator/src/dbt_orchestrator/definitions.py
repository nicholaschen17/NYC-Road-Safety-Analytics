from dagster import AssetSelection, Definitions, define_asset_job
from dagster_dbt import DbtCliResource
from .assets import transform_dbt_assets
from .cli_jobs import dbt_test_cli_job
from .project import transform_project
from .schedules import schedules

materialize_dbt_models_job = define_asset_job(
    name="materialize_dbt_models",
    selection=AssetSelection.assets(transform_dbt_assets),
)

defs = Definitions(
    assets=[transform_dbt_assets],
    schedules=schedules,
    jobs=[materialize_dbt_models_job, dbt_test_cli_job],
    resources={
        "dbt": DbtCliResource(project_dir=transform_project),
    },
)