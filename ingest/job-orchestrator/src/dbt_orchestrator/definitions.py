"""Second Dagster code location: dbt / transform (parallel to job_orchestrator)."""

from dagster import (
    AssetSelection,
    Definitions,
    definitions,
    define_asset_job,
)

from dagster_dbt import DbtCliResource

from dbt_orchestrator.defs.assets import transform_dbt_assets
from dbt_orchestrator.paths import transform_project_dir

dbt_build_all_job = define_asset_job(
    name="dbt_build_all",
    selection=AssetSelection.assets(*transform_dbt_assets.keys),
)


@definitions
def defs():
    return Definitions(
        assets=[transform_dbt_assets],
        resources={
            "dbt": DbtCliResource(project_dir=str(transform_project_dir())),
        },
        jobs=[dbt_build_all_job],
    )
