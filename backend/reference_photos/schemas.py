from __future__ import annotations

import uuid

from pydantic import BaseModel


class ReferencePhotoRead(BaseModel):

    id: uuid.UUID

    filename: str

    description: str | None

    problem_tags: list[str]

    room_tags: list[str]

    window_type_tags: list[str]

    feature_tags: list[str]

    file_url: str


class ReferenceSelectionRead(BaseModel):

    slot: int

    status: str

    score: int | None

    photo: ReferencePhotoRead


class ReferenceSelectionUpdate(BaseModel):

    reference_photo_id: uuid.UUID
