from __future__ import annotations

import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile
from zipfile import ZIP_DEFLATED, ZipFile

TEMPLATE = Path("experiments/pptx_template/input/template.pptx")

BACKUP = Path("experiments/pptx_template/input/" "template_before_linux_fonts.pptx")

FONT_MAPPING = {
    "Microsoft JhengHei UI": "Liberation Sans",
    "Tahoma": "Liberation Sans",
    "Verdana": "Liberation Sans",
    "Arial": "Liberation Sans",
    "Calibri": "Liberation Sans",
    "Georgia": "Liberation Serif",
    "Times New Roman": "Liberation Serif",
}


def replace_fonts(
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


def main() -> None:
    if not TEMPLATE.exists():
        raise SystemExit(f"No existe la plantilla: {TEMPLATE}")

    if not BACKUP.exists():
        shutil.copy2(
            TEMPLATE,
            BACKUP,
        )
        print(f"Backup creado: {BACKUP}")
    else:
        print(f"Backup ya existente: {BACKUP}")

    totals: dict[str, int] = {}

    with NamedTemporaryFile(
        suffix=".pptx",
        delete=False,
    ) as temp:
        temp_path = Path(temp.name)

    try:
        with ZipFile(
            TEMPLATE,
            "r",
        ) as source_zip, ZipFile(
            temp_path,
            "w",
            compression=ZIP_DEFLATED,
        ) as target_zip:
            for info in source_zip.infolist():
                data = source_zip.read(info.filename)

                if info.filename.endswith(".xml"):
                    data, counts = replace_fonts(data)

                    for font, count in counts.items():
                        totals[font] = totals.get(font, 0) + count

                target_zip.writestr(
                    info,
                    data,
                )

        shutil.move(
            temp_path,
            TEMPLATE,
        )

    finally:
        if temp_path.exists():
            temp_path.unlink()

    print()
    print("=" * 70)
    print("FUENTES NORMALIZADAS")
    print("=" * 70)

    for source, target in FONT_MAPPING.items():
        print(
            f"{source:28} -> " f"{target:18} " f"({totals.get(source, 0)} referencias)"
        )

    print()
    print(f"Plantilla actualizada: {TEMPLATE}")
    print(f"Backup original:      {BACKUP}")


if __name__ == "__main__":
    main()
