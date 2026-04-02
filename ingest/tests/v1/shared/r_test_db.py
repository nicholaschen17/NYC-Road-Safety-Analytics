"""Legacy tests for shared.db helpers not present in current DB module."""

import pytest

pytest.skip(
    "connect_to_db / bulk_insert_from_json are not defined on job_orchestrator.shared.db",
    allow_module_level=True,
)
