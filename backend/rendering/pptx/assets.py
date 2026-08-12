from pathlib import Path
from typing import Protocol


class ImageAssetResolver(Protocol):
    def resolve(
        self,
        storage_key: str,
    ) -> Path: ...


class LocalImageAssetResolver:
    def __init__(
        self,
        root: Path,
    ) -> None:
        self._root = root

    def resolve(
        self,
        storage_key: str,
    ) -> Path:
        path = self._root / storage_key

        if not path.exists():
            raise FileNotFoundError(f"Image asset not found: {path}")

        return path
