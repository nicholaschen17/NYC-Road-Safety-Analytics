import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent

if __name__ == "__main__":
    subprocess.run(
        [sys.executable, "-m", "uvicorn", "main:app", "--reload", "--port", "8000"],
        cwd=ROOT,
        check=True,
    )
