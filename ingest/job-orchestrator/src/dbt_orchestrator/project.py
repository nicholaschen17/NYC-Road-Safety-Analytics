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


def _ensure_manifest(project_dir: Path) -> None:
    """Run `dbt parse` whenever the manifest is absent or corrupt.

    `prepare_if_dev()` is a no-op outside of `dagster dev`, so in Docker the
    manifest must already exist or be generated explicitly. This guard runs
    `dbt parse` once at import time so the code server never starts without a
    valid manifest — even after a `docker compose restart` or new model files
    being added via the bind-mount.

    A corrupt file (e.g. truncated by a mid-write restart) is treated the same
    as a missing file: deleted and regenerated.
    """
    import json

    manifest_path = project_dir / "target" / "manifest.json"
    if manifest_path.exists():
        try:
            json.loads(manifest_path.read_bytes())
            return  # file exists and is valid JSON — nothing to do
        except (json.JSONDecodeError, ValueError):
            logger.warning(
                "Corrupt manifest at %s — deleting and regenerating.", manifest_path
            )
            manifest_path.unlink(missing_ok=True)

    logger.info("dbt manifest not found at %s — running `dbt parse`.", manifest_path)
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
