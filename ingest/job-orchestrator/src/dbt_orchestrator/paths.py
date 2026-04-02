"""Resolve the dbt project root (`ingest/transform`) for Docker and local runs."""

from pathlib import Path


def transform_project_dir() -> Path:
    """Find the directory containing `dbt_project.yml` (transform project)."""
    docker = Path("/app/transform")
    if (docker / "dbt_project.yml").exists():
        return docker

    p = Path(__file__).resolve().parent
    for _ in range(12):
        candidate = p / "transform"
        if (candidate / "dbt_project.yml").exists():
            return candidate
        if p.parent == p:
            break
        p = p.parent

    raise FileNotFoundError(
        "Could not find transform/ with dbt_project.yml. "
        "Expected /app/transform in Docker or ingest/transform locally."
    )
