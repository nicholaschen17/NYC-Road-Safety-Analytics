import sys
from pathlib import Path

# Add ingest/ to sys.path so `shared` is importable as a top-level package
# regardless of where pytest is invoked from.
sys.path.insert(0, str(Path(__file__).parent.parent))
