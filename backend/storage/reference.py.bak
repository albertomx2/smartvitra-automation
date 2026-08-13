from __future__ import annotations

import uuid
from pathlib import Path


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

    @property
    def root(self) -> Path:
        return self._root

    def save(
        self,
        *,
        filename: str,
        content: bytes,
    ) -> str:
        extension = Path(filename).suffix.lower()

        storage_key = f"{uuid.uuid4()}" f"{extension}"

        path = self._root / storage_key

        path.write_bytes(content)

        return storage_key

    def get_path(
        self,
        *,
        storage_key: str,
    ) -> Path:
        return self._root / storage_key

    def delete(
        self,
        *,
        storage_key: str,
    ) -> None:
        path = self.get_path(
            storage_key=storage_key,
        )

        if path.exists():
            path.unlink()
