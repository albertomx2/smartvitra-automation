from __future__ import annotations

import os
import uuid
from pathlib import Path

from backend.storage.r2 import R2StorageClient


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

        self._backend = (os.getenv("STORAGE_BACKEND") or "local").lower()

        if self._backend not in {
            "local",
            "r2",
        }:
            raise RuntimeError("Unsupported STORAGE_BACKEND: " f"{self._backend}")

        self._r2 = R2StorageClient() if self._backend == "r2" else None

    @staticmethod
    def _remote_key(
        storage_key: str,
    ) -> str:
        return f"generated/{storage_key}"

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

    def persist(
        self,
        *,
        path: Path,
        content_type: str | None = None,
    ) -> str:
        if not path.exists():
            raise FileNotFoundError(path)

        storage_key = self.relative_key(path)

        if self._backend == "r2":
            assert self._r2 is not None

            self._r2.upload_file(
                storage_key=self._remote_key(
                    storage_key,
                ),
                path=path,
                content_type=content_type,
            )

        return storage_key

    def get_path(
        self,
        *,
        storage_key: str,
    ) -> Path:
        path = self._root / storage_key

        if self._backend == "local":
            return path

        assert self._r2 is not None

        if not path.exists():
            self._r2.download_file(
                storage_key=(self._remote_key(storage_key)),
                destination=path,
            )

        return path
