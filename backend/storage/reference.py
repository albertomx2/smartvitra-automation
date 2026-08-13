from __future__ import annotations

import mimetypes
import os
import uuid
from pathlib import Path

from backend.storage.r2 import R2StorageClient


class ReferencePhotoStorage:
    def __init__(
        self,
        *,
        root: Path | None = None,
    ) -> None:
        self._root = root or Path("var/reference_photos")

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

    @property
    def root(self) -> Path:
        return self._root

    @staticmethod
    def _remote_key(
        storage_key: str,
    ) -> str:
        return "reference_photos/" f"{storage_key}"

    def save(
        self,
        *,
        filename: str,
        content: bytes,
    ) -> str:
        extension = Path(filename).suffix.lower()

        storage_key = f"{uuid.uuid4()}" f"{extension}"

        if self._backend == "r2":
            assert self._r2 is not None

            content_type, _ = mimetypes.guess_type(filename)

            self._r2.upload_bytes(
                storage_key=(self._remote_key(storage_key)),
                content=content,
                content_type=content_type,
            )

            return storage_key

        path = self._root / storage_key

        path.write_bytes(content)

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

    def delete(
        self,
        *,
        storage_key: str,
    ) -> None:
        path = self._root / storage_key

        if self._backend == "r2":
            assert self._r2 is not None

            self._r2.delete(
                storage_key=(self._remote_key(storage_key)),
            )

        if path.exists():
            path.unlink()
