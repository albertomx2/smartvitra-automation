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

    element_type: str | None = None
    opening_system: str | None = None
    leaf_configuration: str | None = None
    width_px: int | None = None
    height_px: int | None = None
    quality_score: int = 0

    file_url: str


class ReferenceSelectionRead(BaseModel):

    slot: int

    status: str

    score: int | None

    photo: ReferencePhotoRead


class ReferenceSelectionUpdate(BaseModel):

    reference_photo_id: uuid.UUID
