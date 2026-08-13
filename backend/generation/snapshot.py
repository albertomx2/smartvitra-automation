from __future__ import annotations

import uuid
from typing import Any

from pydantic import BaseModel, Field


class GenerationPhotoSnapshot(BaseModel):
    id: uuid.UUID
    window_id: uuid.UUID | None

    filename: str
    storage_key: str
    content_type: str

    description: str | None = None


class GenerationReferencePhotoSnapshot(BaseModel):
    id: uuid.UUID
    slot: int

    filename: str
    storage_key: str
    content_type: str

    description: str | None = None


class GenerationWindowSnapshot(BaseModel):
    id: uuid.UUID

    prefweb_item_id: str
    prefweb_id_pos: str | None = None

    position: int

    nomenclature: str | None = None
    reference: str | None = None
    description: str | None = None

    color: str | None = None
    dimensions: str | None = None

    quantity: int = 1
    total_amount: float = 0.0

    room: str | None = None

    problem_type: str | None = None
    commercial_notes: str | None = None

    photos: list[GenerationPhotoSnapshot] = Field(
        default_factory=list,
    )


class GenerationProjectSnapshot(BaseModel):
    number: int
    version: int

    alias_number: str
    version_name: str

    customer_name: str

    request_date: str | None = None
    reference: str | None = None

    customer_address: str | None = None
    customer_address2: str | None = None
    customer_postal_code: str | None = None
    customer_city: str | None = None
    customer_country: str | None = None

    subtotal: float
    tax: float
    final_price: float

    currency_symbol: str


class CaseGenerationSnapshot(BaseModel):
    case_id: uuid.UUID

    status: str

    visit_notes: str | None = None

    project: GenerationProjectSnapshot

    windows: list[GenerationWindowSnapshot]

    reference_photos: list[GenerationReferencePhotoSnapshot] = Field(
        default_factory=list,
    )

    def to_json_dict(self) -> dict[str, Any]:
        return self.model_dump(
            mode="json",
        )
