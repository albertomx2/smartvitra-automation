from __future__ import annotations

import uuid
from pathlib import Path


class GeneratedFileStorage:
    def __init__(
        self,
        *,
        root: Path | None = None,
    ) -> None:
        self._root = root or Path("var/generated")

        self._root.mkdir(
            parents=True,
            exist_ok=True,
        )

    def build_job_directory(
        self,
        *,
        case_id: uuid.UUID,
        job_id: uuid.UUID,
    ) -> Path:
        path = self._root / "cases" / str(case_id) / "generation" / str(job_id)

        path.mkdir(
            parents=True,
            exist_ok=True,
        )

        return path

    def relative_key(
        self,
        path: Path,
    ) -> str:
        return str(path.relative_to(self._root))

    def get_path(
        self,
        *,
        storage_key: str,
    ) -> Path:
        return self._root / storage_key
