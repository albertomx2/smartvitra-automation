from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from watchfiles import run_process

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run_worker() -> None:
    subprocess.run(
        [
            sys.executable,
            "-m",
            "backend.workers.generation_worker",
            "--poll-interval",
            "2",
        ],
        cwd=PROJECT_ROOT,
        check=False,
    )


if __name__ == "__main__":
    run_process(
        PROJECT_ROOT / "backend",
        target=run_worker,
    )
