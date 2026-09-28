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


def test_jpeg_exif_rotation_is_baked_into_pixels(
    tmp_path: Path,
) -> None:
    source = tmp_path / "portrait-from-tablet.jpg"

    image = Image.new(
        "RGB",
        (120, 80),
        color="navy",
    )
    exif = image.getexif()
    exif[274] = 6
    image.save(
        source,
        format="JPEG",
        exif=exif,
    )

    result = PptxImageNormalizer().normalize(
        image_path=source,
        work_dir=(tmp_path / "normalized"),
    )

    assert result != source
    assert result.suffix == ".png"

    with Image.open(result) as normalized:
        assert normalized.size == (80, 120)
        assert normalized.getexif().get(274) in (None, 1)


def test_jpeg_exif_half_turn_is_baked_into_pixels(
    tmp_path: Path,
) -> None:
    source = tmp_path / "half-turn.jpg"

    image = Image.new(
        "RGB",
        (120, 80),
        color="navy",
    )
    exif = image.getexif()
    exif[274] = 3
    image.save(
        source,
        format="JPEG",
        exif=exif,
    )

    result = PptxImageNormalizer().normalize(
        image_path=source,
        work_dir=(tmp_path / "normalized"),
    )

    assert result != source

    with Image.open(result) as normalized:
        assert normalized.size == (120, 80)
        assert normalized.getexif().get(274) in (None, 1)
