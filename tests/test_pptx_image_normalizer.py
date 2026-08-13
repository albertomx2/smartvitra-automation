from pathlib import Path

from PIL import Image

from backend.rendering.pptx.image_normalizer import (
    PptxImageNormalizer,
)


def test_webp_is_converted_to_png(
    tmp_path: Path,
) -> None:
    source = tmp_path / "test.webp"

    Image.new(
        "RGB",
        (100, 100),
    ).save(
        source,
        format="WEBP",
    )

    result = PptxImageNormalizer().normalize(
        image_path=source,
        work_dir=(tmp_path / "normalized"),
    )

    assert result.exists()
    assert result.suffix == ".png"

    with Image.open(result) as image:
        assert image.format == "PNG"


def test_png_is_not_modified(
    tmp_path: Path,
) -> None:
    source = tmp_path / "test.png"

    Image.new(
        "RGB",
        (100, 100),
    ).save(
        source,
        format="PNG",
    )

    result = PptxImageNormalizer().normalize(
        image_path=source,
        work_dir=(tmp_path / "normalized"),
    )

    assert result == source
