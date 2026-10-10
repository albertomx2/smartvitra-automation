from __future__ import annotations

import io
import os
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path, PurePosixPath
from typing import cast
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from PIL import Image, ImageOps


class PptxMediaOptimizer:
    """Reduce photographic media without changing PowerPoint layout XML."""

    MIN_SOURCE_BYTES = 256 * 1024
    MAX_IMAGE_EDGE = 1920
    JPEG_QUALITY = 85

    def optimize(
        self,
        *,
        presentation_path: Path,
    ) -> None:
        if not presentation_path.exists():
            raise FileNotFoundError(presentation_path)

        with ZipFile(presentation_path) as source:
            replacements = self._build_replacements(source)

            if not replacements:
                return

            with tempfile.NamedTemporaryFile(
                suffix=".pptx",
                dir=presentation_path.parent,
                delete=False,
            ) as temporary:
                temporary_path = Path(temporary.name)

            try:
                self._write_optimized_package(
                    source=source,
                    output_path=temporary_path,
                    replacements=replacements,
                )
                os.replace(
                    temporary_path,
                    presentation_path,
                )
            finally:
                temporary_path.unlink(
                    missing_ok=True,
                )

    def _build_replacements(
        self,
        source: ZipFile,
    ) -> dict[str, tuple[str, bytes]]:
        names = set(source.namelist())
        replacements: dict[str, tuple[str, bytes]] = {}

        for info in source.infolist():
            if not info.filename.startswith("ppt/media/"):
                continue

            if info.file_size < self.MIN_SOURCE_BYTES:
                continue

            original = source.read(info.filename)
            optimized = self._optimize_image(original)

            if optimized is None or len(optimized) >= len(original):
                continue

            original_path = PurePosixPath(info.filename)
            optimized_name = str(original_path.with_suffix(".jpeg"))

            if optimized_name in names and optimized_name != info.filename:
                optimized_name = str(
                    original_path.with_name(
                        f"{original_path.stem}_optimized.jpeg",
                    )
                )

            replacements[info.filename] = (
                optimized_name,
                optimized,
            )
            names.add(optimized_name)

        return replacements

    def _optimize_image(
        self,
        content: bytes,
    ) -> bytes | None:
        try:
            with Image.open(io.BytesIO(content)) as image:
                upright = ImageOps.exif_transpose(image)

                if self._has_transparency(upright):
                    return None

                converted = upright.convert("RGB")
                converted.thumbnail(
                    (
                        self.MAX_IMAGE_EDGE,
                        self.MAX_IMAGE_EDGE,
                    ),
                    Image.Resampling.LANCZOS,
                )

                output = io.BytesIO()
                converted.save(
                    output,
                    format="JPEG",
                    quality=self.JPEG_QUALITY,
                    optimize=True,
                    subsampling="4:2:0",
                )
                return output.getvalue()
        except (OSError, ValueError):
            return None

    @staticmethod
    def _has_transparency(
        image: Image.Image,
    ) -> bool:
        if image.mode in {"RGBA", "LA"}:
            alpha = image.getchannel("A")
            minimum, _ = cast(
                tuple[int, int],
                alpha.getextrema(),
            )
            return minimum < 255

        if image.mode == "P" and "transparency" in image.info:
            converted = image.convert("RGBA")
            alpha = converted.getchannel("A")
            minimum, _ = cast(
                tuple[int, int],
                alpha.getextrema(),
            )
            return minimum < 255

        return False

    def _write_optimized_package(
        self,
        *,
        source: ZipFile,
        output_path: Path,
        replacements: dict[str, tuple[str, bytes]],
    ) -> None:
        renamed = {
            old_name: new_name for old_name, (new_name, _) in replacements.items()
        }

        with ZipFile(
            output_path,
            mode="w",
            compression=ZIP_DEFLATED,
        ) as output:
            for info in source.infolist():
                if info.filename in replacements:
                    new_name, content = replacements[info.filename]
                    output.writestr(
                        self._copy_zip_info(info, filename=new_name),
                        content,
                    )
                    continue

                content = source.read(info.filename)

                if info.filename.endswith(".rels"):
                    content = self._rewrite_relationships(
                        content,
                        renamed=renamed,
                    )

                output.writestr(
                    self._copy_zip_info(info),
                    content,
                )

    @staticmethod
    def _rewrite_relationships(
        content: bytes,
        *,
        renamed: dict[str, str],
    ) -> bytes:
        try:
            root = ET.fromstring(content)
        except ET.ParseError:
            return content

        changed = False

        for relationship in root:
            target = relationship.attrib.get("Target")

            if not target:
                continue

            target_path = PurePosixPath(target)

            for old_name, new_name in renamed.items():
                old_media_name = PurePosixPath(old_name).name

                if target_path.name != old_media_name:
                    continue

                relationship.set(
                    "Target",
                    str(target_path.with_name(PurePosixPath(new_name).name)),
                )
                changed = True
                break

        if not changed:
            return content

        return ET.tostring(
            root,
            encoding="utf-8",
            xml_declaration=True,
        )

    @staticmethod
    def _copy_zip_info(
        info: ZipInfo,
        *,
        filename: str | None = None,
    ) -> ZipInfo:
        copied = ZipInfo(
            filename=(filename or info.filename),
            date_time=info.date_time,
        )
        copied.compress_type = ZIP_DEFLATED
        copied.comment = info.comment
        copied.extra = info.extra
        copied.create_system = info.create_system
        copied.external_attr = info.external_attr
        copied.internal_attr = info.internal_attr
        copied.flag_bits = info.flag_bits
        return copied
