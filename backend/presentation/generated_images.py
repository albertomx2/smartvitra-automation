from pathlib import Path
from typing import Protocol

from backend.presentation.models import (
    PresentationSpec,
)


class GeneratedImageProvider(Protocol):
    def get_before_after_image(
        self,
        spec: PresentationSpec,
    ) -> Path: ...


class LocalGeneratedImageProvider:
    def __init__(
        self,
        image_path: Path,
    ) -> None:
        self._image_path = image_path

    def get_before_after_image(
        self,
        spec: PresentationSpec,
    ) -> Path:
        if not self._image_path.exists():
            raise FileNotFoundError(self._image_path)

        return self._image_path
