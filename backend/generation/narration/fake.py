from __future__ import annotations

import os
from pathlib import Path

from backend.storage.r2 import (
    R2StorageClient,
)


class FakeNarrationGenerator:
    DEFAULT_STORAGE_KEY = "system/test-assets/elevenlabs/" "smartvitra_voice_test.mp3"

    def generate(
        self,
        *,
        output_path: Path,
    ) -> Path:
        storage_key = (
            os.getenv(
                "FAKE_NARRATION_STORAGE_KEY",
            )
            or self.DEFAULT_STORAGE_KEY
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        R2StorageClient().download_file(
            storage_key=storage_key,
            destination=output_path,
        )

        if not output_path.exists():
            raise RuntimeError("Fake narration could not be downloaded")

        if output_path.stat().st_size == 0:
            raise RuntimeError("Fake narration is empty")

        return output_path
