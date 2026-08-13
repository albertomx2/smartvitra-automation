from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import (
    Session,
    selectinload,
)

from backend.db.models.reference_photo import (
    CaseReferenceSelection,
    ReferencePhoto,
)


class ReferencePhotoRepository:
    def __init__(
        self,
        db: Session,
    ) -> None:
        self._db = db

    def list_active(
        self,
    ) -> list[ReferencePhoto]:
        statement = (
            select(ReferencePhoto)
            .where(ReferencePhoto.active.is_(True))
            .order_by(ReferencePhoto.created_at.desc())
        )

        return list(self._db.scalars(statement).all())

    def get(
        self,
        *,
        photo_id: uuid.UUID,
    ) -> ReferencePhoto | None:
        return self._db.scalar(
            select(ReferencePhoto).where(ReferencePhoto.id == photo_id)
        )

    def add(
        self,
        photo: ReferencePhoto,
    ) -> ReferencePhoto:
        self._db.add(photo)
        self._db.commit()
        self._db.refresh(photo)

        return photo

    def get_selections(
        self,
        *,
        case_id: uuid.UUID,
    ) -> list[CaseReferenceSelection]:
        statement = (
            select(CaseReferenceSelection)
            .options(selectinload(CaseReferenceSelection.reference_photo))
            .where(CaseReferenceSelection.case_id == case_id)
            .order_by(CaseReferenceSelection.slot)
        )

        return list(self._db.scalars(statement).all())

    def set_selection(
        self,
        *,
        case_id: uuid.UUID,
        slot: int,
        photo_id: uuid.UUID,
        status: str,
        score: int | None,
    ) -> CaseReferenceSelection:
        selection = self._db.scalar(
            select(CaseReferenceSelection).where(
                CaseReferenceSelection.case_id == case_id,
                CaseReferenceSelection.slot == slot,
            )
        )

        if selection is None:
            selection = CaseReferenceSelection(
                case_id=case_id,
                slot=slot,
                reference_photo_id=(photo_id),
                status=status,
                score=score,
            )

            self._db.add(selection)
        else:
            selection.reference_photo_id = photo_id
            selection.status = status
            selection.score = score

        self._db.commit()

        result = self._db.scalar(
            select(CaseReferenceSelection)
            .options(selectinload(CaseReferenceSelection.reference_photo))
            .where(CaseReferenceSelection.id == selection.id)
        )

        if result is None:
            raise RuntimeError("Could not reload selection")

        return result

    def delete_selection(
        self,
        *,
        case_id: uuid.UUID,
        slot: int,
    ) -> None:
        selection = self._db.scalar(
            select(CaseReferenceSelection).where(
                CaseReferenceSelection.case_id == case_id,
                CaseReferenceSelection.slot == slot,
            )
        )

        if selection is None:
            return

        self._db.delete(selection)
        self._db.commit()

    def replace_selections(
        self,
        *,
        case_id: uuid.UUID,
        selections: list[CaseReferenceSelection],
    ) -> list[CaseReferenceSelection]:
        current = self.get_selections(case_id=case_id)

        for selection in current:
            self._db.delete(selection)

        self._db.flush()

        for selection in selections:
            self._db.add(selection)

        self._db.commit()

        return self.get_selections(case_id=case_id)

    def commit(self) -> None:
        self._db.commit()
