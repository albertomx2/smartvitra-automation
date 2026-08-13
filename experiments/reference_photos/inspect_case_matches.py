from __future__ import annotations

import uuid

from backend.db.session import (
    SessionLocal,
)
from backend.reference_photos.service import (
    ReferencePhotoService,
)


CASE_ID = uuid.UUID(
    "10376604-2c48-4649-b5c1-438a3cf736ca"
)


def main() -> None:
    with SessionLocal() as db:
        service = (
            ReferencePhotoService(
                db
            )
        )

        suggestions = (
            service.suggest_for_case(
                case_id=CASE_ID,
                limit=10,
            )
        )

        print()
        print("=" * 80)
        print(
            "REFERENCE PHOTO MATCHES"
        )
        print("=" * 80)

        for index, (
            photo,
            score,
        ) in enumerate(
            suggestions,
            start=1,
        ):
            print()
            print(
                f"{index}. "
                f"{photo.original_filename}"
            )
            print(
                f"   score: {score}"
            )
            print(
                "   problems:",
                photo.problem_tags,
            )
            print(
                "   rooms:",
                photo.room_tags,
            )
            print(
                "   windows:",
                photo.window_type_tags,
            )
            print(
                "   features:",
                photo.feature_tags,
            )


if __name__ == "__main__":
    main()
