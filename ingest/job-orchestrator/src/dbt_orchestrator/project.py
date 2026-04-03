import logging
import os
import subprocess
from pathlib import Path

from dagster_dbt import DbtProject

logger = logging.getLogger(__name__)

_PKG_ROOT = Path(__file__).resolve().parent


def _transform_project_dir() -> Path:
    """Resolve `ingest/transform` for Docker (`/app/transform`) and local monorepo checkouts."""
    candidates = [
        _PKG_ROOT.parent / "transform",  # /app/dbt_orchestrator -> /app/transform
        _PKG_ROOT.parent.parent.parent / "transform",  # .../src/dbt_orchestrator -> .../ingest/transform
    ]
    for path in candidates:
        if (path / "dbt_project.yml").exists():
            return path

    env = os.environ.get("DBT_TRANSFORM_PROJECT_DIR")
    if env:
        p = Path(env).expanduser().resolve()
        if (p / "dbt_project.yml").exists():
            return p

    raise FileNotFoundError(
        "Could not find dbt project (dbt_project.yml). Tried: "
        f"{[str(p) for p in candidates]}"
        + (f", DBT_TRANSFORM_PROJECT_DIR={env!r}" if env else "")
        + ". Set DBT_TRANSFORM_PROJECT_DIR to the folder that contains dbt_project.yml."
    )


def _is_manifest_stale(project_dir: Path, manifest_path: Path) -> bool:
    """Return True if any tracked project file is newer than the manifest.

    Watches: models/**/*.sql, models/**/*.yml, dbt_project.yml, packages.yml.
    This catches new/edited models, schema changes, and project-level config
    without requiring a manual manifest delete.
    """
    manifest_mtime = manifest_path.stat().st_mtime
    watch_patterns = ["models/**/*.sql", "models/**/*.yml", "dbt_project.yml", "packages.yml"]
    for pattern in watch_patterns:
        for path in project_dir.glob(pattern):
            if path.stat().st_mtime > manifest_mtime:
                logger.info(
                    "Manifest stale: %s is newer than %s.", path.relative_to(project_dir), manifest_path
                )
                return True
    return False


def _ensure_manifest(project_dir: Path) -> None:
    """Run `dbt parse` whenever the manifest is absent, corrupt, or stale.

    Staleness is determined by comparing the manifest mtime against every
    .sql and .yml file under models/ as well as dbt_project.yml. Adding or
    editing any model/schema file will therefore trigger an automatic re-parse
    on the next Dagster code-server start — no manual manifest deletion needed.

    A corrupt file (e.g. truncated by a mid-write restart) is treated the same
    as a missing file: deleted and regenerated.
    """
    import json

    manifest_path = project_dir / "target" / "manifest.json"
    needs_parse = False

    if not manifest_path.exists():
        logger.info("dbt manifest not found at %s — running `dbt parse`.", manifest_path)
        needs_parse = True
    else:
        try:
            json.loads(manifest_path.read_bytes())
        except (json.JSONDecodeError, ValueError):
            logger.warning(
                "Corrupt manifest at %s — deleting and regenerating.", manifest_path
            )
            manifest_path.unlink(missing_ok=True)
            needs_parse = True

        if not needs_parse and _is_manifest_stale(project_dir, manifest_path):
            logger.info("Manifest is stale — running `dbt parse` to refresh.")
            needs_parse = True

    if not needs_parse:
        return

    result = subprocess.run(
        [
            "dbt", "parse",
            "--project-dir", str(project_dir),
            "--profiles-dir", str(project_dir),
            "--no-use-colors",
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"`dbt parse` failed (exit {result.returncode}):\n"
            f"{result.stdout}\n{result.stderr}"
        )
    logger.info("`dbt parse` completed successfully.")


_project_dir = _transform_project_dir()
_ensure_manifest(_project_dir)

transform_project = DbtProject(
    project_dir=_project_dir,
    packaged_project_dir=_PKG_ROOT / "dbt-project",
)
transform_project.prepare_if_dev()
