from __future__ import annotations

import hashlib
from pathlib import Path

from PIL import Image

PPTX_SUPPORTED_FORMATS = {
    "BMP",
    "GIF",
    "JPEG",
    "PNG",
    "TIFF",
    "WMF",
}


class PptxImageNormalizer:
    def normalize(
        self,
        *,
        image_path: Path,
        work_dir: Path,
    ) -> Path:
        if not image_path.exists():
            raise FileNotFoundError(image_path)

        with Image.open(image_path) as image:
            image_format = image.format.upper() if image.format else None

            if image_format in PPTX_SUPPORTED_FORMATS:
                return image_path

            work_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

            digest = hashlib.sha256(str(image_path.resolve()).encode()).hexdigest()[:16]

            output_path = work_dir / f"{digest}.png"

            if output_path.exists():
                return output_path

            converted = image.convert("RGBA")

            converted.save(
                output_path,
                format="PNG",
            )

            return output_path
