"""Op-based jobs that invoke dbt CLI without a second @dbt_assets (avoids duplicate asset keys)."""

from dagster import Nothing, OpExecutionContext, Out, job, op
from dagster_dbt import DbtCliResource

from .project import transform_project


@op(out=Out(Nothing))
def dbt_test_cli_op(context: OpExecutionContext, dbt: DbtCliResource):
    yield from dbt.cli(
        ["test"],
        context=context,
        manifest=transform_project.manifest_path,
    ).stream()


@job
def dbt_test_cli_job():
    dbt_test_cli_op()
