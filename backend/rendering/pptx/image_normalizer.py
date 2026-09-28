from __future__ import annotations

import hashlib
from pathlib import Path

from PIL import Image, ImageOps

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
            orientation = image.getexif().get(274, 1)

            if image_format in PPTX_SUPPORTED_FORMATS and orientation in (None, 1):
                return image_path

            work_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

            digest = hashlib.sha256(str(image_path.resolve()).encode()).hexdigest()[:16]

            output_path = work_dir / f"{digest}.png"

            if output_path.exists():
                return output_path

            # Phones and tablets often store landscape pixels plus an EXIF
            # instruction telling viewers to rotate them. Browsers honour that
            # instruction, but PowerPoint and image-generation APIs do not do
            # so consistently. Bake the orientation into the pixels and save a
            # metadata-free PNG before either consumer sees the image.
            upright = ImageOps.exif_transpose(image)

            converted = upright.convert("RGBA" if "A" in upright.getbands() else "RGB")

            converted.save(
                output_path,
                format="PNG",
            )

            return output_path
