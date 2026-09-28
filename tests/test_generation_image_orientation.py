from pathlib import Path
from uuid import uuid4

from PIL import Image

from backend.generation.presentation import (
    RealPresentationGenerator,
)
from backend.generation.snapshot import (
    CaseGenerationSnapshot,
    GenerationPhotoSnapshot,
    GenerationProjectSnapshot,
    GenerationWindowSnapshot,
)


def test_slides_two_and_three_share_the_same_upright_source(
    tmp_path: Path,
    monkeypatch,
) -> None:
    source = tmp_path / "tablet-photo.jpg"
    image = Image.new("RGB", (120, 80), color="navy")
    exif = image.getexif()
    exif[274] = 6
    image.save(source, format="JPEG", exif=exif)

    class FakeStorage:
        def get_path(self, *, storage_key: str) -> Path:
            assert storage_key == "tablet-photo.jpg"
            return source

    generated = tmp_path / "generated-solution.png"
    generated.write_bytes(b"generated")
    source_seen_by_gemini: list[Path] = []

    def fake_generate_solution_image(
        *, snapshot, scene, source_photo: Path, work_dir: Path
    ) -> Path:
        source_seen_by_gemini.append(source_photo)
        return generated

    monkeypatch.setattr(
        "backend.generation.presentation.LocalFileStorage",
        FakeStorage,
    )
    monkeypatch.setattr(
        RealPresentationGenerator,
        "_generate_solution_image",
        staticmethod(fake_generate_solution_image),
    )

    window_id = uuid4()
    snapshot = CaseGenerationSnapshot(
        case_id=uuid4(),
        status="draft",
        project=GenerationProjectSnapshot(
            number=1,
            version=1,
            alias_number="TEST-001",
            version_name="Version 1",
            customer_name="Cliente prueba",
            subtotal=1000,
            tax=210,
            final_price=1210,
            currency_symbol="€",
        ),
        windows=[
            GenerationWindowSnapshot(
                id=window_id,
                prefweb_item_id="item-1",
                position=1,
                problem_type="thermal",
                photos=[
                    GenerationPhotoSnapshot(
                        id=uuid4(),
                        window_id=window_id,
                        filename="tablet-photo.jpg",
                        storage_key="tablet-photo.jpg",
                        content_type="image/jpeg",
                    )
                ],
            )
        ],
    )

    images = RealPresentationGenerator()._build_images(
        snapshot=snapshot,
        work_dir=(tmp_path / "work"),
    )

    upright = images["problem_photo"]

    assert upright == source_seen_by_gemini[0]
    assert upright.suffix == ".png"

    with Image.open(upright) as normalized:
        assert normalized.size == (80, 120)
        assert normalized.getexif().get(274) in (None, 1)
