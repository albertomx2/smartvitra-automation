from __future__ import annotations

import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile
from zipfile import ZIP_DEFLATED, ZipFile

FONT_MAPPING = {
    "Microsoft JhengHei UI": "Liberation Sans",
    "Tahoma": "Liberation Sans",
    "Verdana": "Liberation Sans",
    "Arial": "Liberation Sans",
    "Calibri": "Liberation Sans",
    "Georgia": "Liberation Serif",
    "Times New Roman": "Liberation Serif",
}


def _replace_fonts(
    content: bytes,
) -> tuple[bytes, dict[str, int]]:
    text = content.decode(
        "utf-8",
        errors="strict",
    )

    counts: dict[str, int] = {}

    for source, target in FONT_MAPPING.items():
        pattern = f'typeface="{source}"'
        replacement = f'typeface="{target}"'

        count = text.count(pattern)

        if count:
            text = text.replace(
                pattern,
                replacement,
            )
            counts[source] = count

    return text.encode("utf-8"), counts


def normalize_pptx_fonts(
    *,
    source_path: Path,
    output_path: Path,
) -> dict[str, int]:
    if not source_path.exists():
        raise FileNotFoundError(source_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with NamedTemporaryFile(
        suffix=".pptx",
        delete=False,
    ) as temp:
        temp_path = Path(temp.name)

    totals: dict[str, int] = {}

    try:
        with ZipFile(
            source_path,
            "r",
        ) as source_zip, ZipFile(
            temp_path,
            "w",
            compression=ZIP_DEFLATED,
        ) as target_zip:
            for info in source_zip.infolist():
                data = source_zip.read(
                    info.filename,
                )

                if info.filename.endswith(".xml"):
                    data, counts = _replace_fonts(
                        data,
                    )

                    for font, count in counts.items():
                        totals[font] = (
                            totals.get(
                                font,
                                0,
                            )
                            + count
                        )

                target_zip.writestr(
                    info,
                    data,
                )

        shutil.move(
            temp_path,
            output_path,
        )

    finally:
        if temp_path.exists():
            temp_path.unlink()

    return totals
