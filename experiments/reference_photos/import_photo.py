from __future__ import annotations

import argparse
import mimetypes
from pathlib import Path

from backend.db.models.reference_photo import (
    ReferencePhoto,
)
from backend.db.session import (
    SessionLocal,
)
from backend.reference_photos.repository import (
    ReferencePhotoRepository,
)
from backend.storage.reference import (
    ReferencePhotoStorage,
)


def parse_tags(
    value: str,
) -> list[str]:
    return [
        item.strip().lower()
        for item in value.split(",")
        if item.strip()
    ]


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "file",
        type=Path,
    )

    parser.add_argument(
        "--description",
        default=None,
    )

    parser.add_argument(
        "--problems",
        default="",
    )

    parser.add_argument(
        "--rooms",
        default="",
    )

    parser.add_argument(
        "--window-types",
        default="",
    )

    parser.add_argument(
        "--features",
        default="",
    )

    args = parser.parse_args()

    path: Path = args.file

    if not path.exists():
        raise FileNotFoundError(
            path
        )

    content = path.read_bytes()

    content_type = (
        mimetypes.guess_type(
            path.name
        )[0]
        or "application/octet-stream"
    )

    storage = (
        ReferencePhotoStorage()
    )

    storage_key = storage.save(
        filename=path.name,
        content=content,
    )

    with SessionLocal() as db:
        repository = (
            ReferencePhotoRepository(
                db
            )
        )

        photo = ReferencePhoto(
            original_filename=(
                path.name
            ),
            storage_key=storage_key,
            content_type=content_type,
            description=(
                args.description
            ),
            problem_tags=parse_tags(
                args.problems
            ),
            room_tags=parse_tags(
                args.rooms
            ),
            window_type_tags=parse_tags(
                args.window_types
            ),
            feature_tags=parse_tags(
                args.features
            ),
        )

        photo = repository.add(
            photo
        )

    print()
    print(
        "Reference photo imported"
    )
    print(
        f"ID: {photo.id}"
    )
    print(
        f"Storage: {storage_key}"
    )
    print(
        "Problems:",
        photo.problem_tags,
    )
    print(
        "Rooms:",
        photo.room_tags,
    )
    print(
        "Window types:",
        photo.window_type_tags,
    )
    print(
        "Features:",
        photo.feature_tags,
    )


if __name__ == "__main__":
    main()
