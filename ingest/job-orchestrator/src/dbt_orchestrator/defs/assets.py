"""dbt models as Dagster assets (requires transform/target/manifest.json — run `dbt parse` or `dbt build`)."""

from dagster import AssetExecutionContext
from dagster_dbt import DbtCliResource, DbtProject, dbt_assets

from dbt_orchestrator.paths import transform_project_dir

_TRANSFORM = transform_project_dir()
_dbt_project = DbtProject(project_dir=_TRANSFORM)


@dbt_assets(
    manifest=_dbt_project.manifest_path,
    project=_dbt_project,
    name="transform_dbt",
)
def transform_dbt_assets(context: AssetExecutionContext, dbt: DbtCliResource):
    yield from dbt.cli(["build"], context=context).stream()
