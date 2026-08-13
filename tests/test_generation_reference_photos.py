from pathlib import Path
from uuid import uuid4

from backend.generation.presentation import (
    RealPresentationGenerator,
)
from backend.generation.snapshot import (
    CaseGenerationSnapshot,
    GenerationProjectSnapshot,
    GenerationReferencePhotoSnapshot,
)


def test_reference_photos_are_mapped_to_project_photo_slots(
    tmp_path: Path,
    monkeypatch,
) -> None:
    reference_root = tmp_path / "reference_photos"
    reference_root.mkdir()

    paths = []

    for index in range(1, 4):
        path = reference_root / f"photo_{index}.jpg"
        path.write_bytes(b"fake")
        paths.append(path)

    class FakeReferenceStorage:
        def get_path(
            self,
            *,
            storage_key: str,
        ) -> Path:
            return reference_root / storage_key

    monkeypatch.setattr(
        "backend.generation.presentation.ReferencePhotoStorage",
        FakeReferenceStorage,
    )

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
            tax=21,
            final_price=1210,
            currency_symbol="€",
        ),
        windows=[],
        reference_photos=[
            GenerationReferencePhotoSnapshot(
                id=uuid4(),
                slot=1,
                filename="photo_1.jpg",
                storage_key="photo_1.jpg",
                content_type="image/jpeg",
            ),
            GenerationReferencePhotoSnapshot(
                id=uuid4(),
                slot=2,
                filename="photo_2.jpg",
                storage_key="photo_2.jpg",
                content_type="image/jpeg",
            ),
            GenerationReferencePhotoSnapshot(
                id=uuid4(),
                slot=3,
                filename="photo_3.jpg",
                storage_key="photo_3.jpg",
                content_type="image/jpeg",
            ),
        ],
    )

    images = RealPresentationGenerator()._build_images(
        snapshot=snapshot,
        work_dir=tmp_path / "work",
    )

    assert images["project_photo_1"] == paths[0]
    assert images["project_photo_2"] == paths[1]
    assert images["project_photo_3"] == paths[2]
