"""Ensure `job_orchestrator` is importable when pytest runs outside Make."""

import sys
from pathlib import Path

_ingest_root = Path(__file__).resolve().parents[1]
_jo_src = _ingest_root / "job-orchestrator" / "src"
for p in (_ingest_root, _jo_src):
    s = str(p)
    if s not in sys.path:
        sys.path.insert(0, s)
