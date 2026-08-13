from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from backend.db.models.reference_photo import (
    CaseReferenceSelection,
    ReferencePhoto,
)
from backend.generation.snapshot_builder import (
    GenerationSnapshotBuilder,
)
from backend.reference_photos.matcher import (
    ReferencePhotoCandidate,
    ReferencePhotoMatcher,
)
from backend.reference_photos.repository import (
    ReferencePhotoRepository,
)


class ReferencePhotoService:
    def __init__(
        self,
        db: Session,
    ) -> None:
        self._db = db

        self._repository = ReferencePhotoRepository(db)

    def suggest_for_case(
        self,
        *,
        case_id: uuid.UUID,
        limit: int = 3,
    ) -> list[
        tuple[
            ReferencePhoto,
            int,
        ]
    ]:
        snapshot = GenerationSnapshotBuilder(self._db).build(case_id=case_id)

        photos = self._repository.list_active()

        candidates = [
            ReferencePhotoCandidate(
                id=str(photo.id),
                problem_tags=(photo.problem_tags),
                room_tags=(photo.room_tags),
                window_type_tags=(photo.window_type_tags),
                feature_tags=(photo.feature_tags),
            )
            for photo in photos
        ]

        matcher = ReferencePhotoMatcher()

        photo_by_id = {str(photo.id): photo for photo in photos}

        selected_ids: set[str] = set()

        result: list[
            tuple[
                ReferencePhoto,
                int,
            ]
        ] = []

        # First pass:
        # try to represent different actual
        # windows/problems in the project.
        for window in snapshot.windows:
            ranked = matcher.rank_for_window(
                window=window,
                photos=candidates,
            )

            chosen = next(
                (
                    item
                    for item in ranked
                    if (item.photo.id not in selected_ids and item.score > 0)
                ),
                None,
            )

            if chosen is None:
                continue

            photo = photo_by_id.get(chosen.photo.id)

            if photo is None:
                continue

            selected_ids.add(chosen.photo.id)

            result.append(
                (
                    photo,
                    chosen.score,
                )
            )

            if len(result) >= limit:
                return result

        # Second pass:
        # fill any remaining slots with
        # the strongest unused candidates.
        all_scores: dict[str, int] = {}

        for window in snapshot.windows:
            ranked = matcher.rank_for_window(
                window=window,
                photos=candidates,
            )

            for item in ranked:
                all_scores[item.photo.id] = max(
                    all_scores.get(
                        item.photo.id,
                        0,
                    ),
                    item.score,
                )

        remaining = sorted(
            (
                (
                    photo_id,
                    score,
                )
                for (
                    photo_id,
                    score,
                ) in all_scores.items()
                if (photo_id not in selected_ids)
            ),
            key=lambda item: item[1],
            reverse=True,
        )

        for photo_id, score in remaining:
            photo = photo_by_id.get(photo_id)

            if photo is None:
                continue

            result.append(
                (
                    photo,
                    score,
                )
            )

            selected_ids.add(photo_id)

            if len(result) >= limit:
                break

        return result

    def ensure_selections(
        self,
        *,
        case_id: uuid.UUID,
    ) -> list[CaseReferenceSelection]:
        existing = self._repository.get_selections(case_id=case_id)

        if existing:
            return existing

        return self.refresh_suggestions(case_id=case_id)

    def refresh_suggestions(
        self,
        *,
        case_id: uuid.UUID,
        limit: int = 3,
    ) -> list[CaseReferenceSelection]:
        suggestions = self.suggest_for_case(
            case_id=case_id,
            limit=limit,
        )

        selections = [
            CaseReferenceSelection(
                case_id=case_id,
                slot=index,
                reference_photo_id=(photo.id),
                status="suggested",
                score=score,
            )
            for index, (
                photo,
                score,
            ) in enumerate(
                suggestions,
                start=1,
            )
        ]

        return self._repository.replace_selections(
            case_id=case_id,
            selections=selections,
        )

    def select_photo(
        self,
        *,
        case_id: uuid.UUID,
        slot: int,
        photo_id: uuid.UUID,
    ) -> CaseReferenceSelection:
        if not 1 <= slot <= 3:
            raise ValueError("slot must be between 1 and 3")

        photo = self._repository.get(photo_id=photo_id)

        if photo is None:
            raise LookupError(f"Reference photo " f"{photo_id} not found")

        return self._repository.set_selection(
            case_id=case_id,
            slot=slot,
            photo_id=photo_id,
            status="confirmed",
            score=None,
        )

    def confirm_all(
        self,
        *,
        case_id: uuid.UUID,
    ) -> list[CaseReferenceSelection]:
        selections = self.ensure_selections(case_id=case_id)

        for selection in selections:
            selection.status = "confirmed"

        self._repository.commit()

        return self._repository.get_selections(case_id=case_id)

    def remove_selection(
        self,
        *,
        case_id: uuid.UUID,
        slot: int,
    ) -> None:
        self._repository.delete_selection(
            case_id=case_id,
            slot=slot,
        )
