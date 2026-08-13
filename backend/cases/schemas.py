from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CaseCreate(BaseModel):
    prefweb_number: int
    prefweb_version: int


class ProjectCaseUpdate(BaseModel):
    visit_notes: str | None = None


class CaseWindowUpdate(BaseModel):
    problem_type: str | None = None
    commercial_notes: str | None = None


class CasePhotoUpdate(BaseModel):
    description: str | None = None


class CasePhotoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    case_id: uuid.UUID
    window_id: uuid.UUID | None
    original_filename: str
    storage_key: str
    content_type: str
    size_bytes: int
    description: str | None
    created_at: datetime


class CaseWindowRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    prefweb_item_id: str
    prefweb_id_pos: str | None
    position: int
    room: str | None
    problem_type: str | None
    commercial_notes: str | None
    photos: list[CasePhotoRead] = []


class ProjectCaseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID

    prefweb_number: int
    prefweb_version: int

    alias_number: str
    customer_name: str
    status: str
    visit_notes: str | None

    created_at: datetime
    updated_at: datetime

    windows: list[CaseWindowRead]
    photos: list[CasePhotoRead]


class CaseWorkspacePhoto(BaseModel):
    id: uuid.UUID
    filename: str
    content_type: str
    description: str | None
    file_url: str


class CaseWorkspaceWindow(BaseModel):
    id: uuid.UUID

    prefweb_item_id: str
    prefweb_id_pos: str | None

    position: int
    nomenclature: str | None
    reference: str | None
    description: str | None
    color: str | None
    dimensions: str | None
    quantity: int
    total_amount: float

    room: str | None

    problem_type: str | None
    commercial_notes: str | None

    prefweb_svg_url: str

    photos: list[CaseWorkspacePhoto]


class CaseWorkspaceProject(BaseModel):
    number: int
    version: int

    alias_number: str
    version_name: str

    customer_name: str

    request_date: str | None
    reference: str | None

    customer_address: str | None
    customer_address2: str | None
    customer_postal_code: str | None
    customer_city: str | None
    customer_country: str | None

    subtotal: float
    tax: float
    final_price: float
    currency_symbol: str


class CaseWorkspaceRead(BaseModel):
    id: uuid.UUID
    status: str

    visit_notes: str | None

    project: CaseWorkspaceProject

    windows: list[CaseWorkspaceWindow]
