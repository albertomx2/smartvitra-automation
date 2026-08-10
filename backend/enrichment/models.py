from pydantic import BaseModel, Field

from backend.needs.models import CustomerNeedSelection


class VisitPhotoInput(BaseModel):
    opening_id: str | None = None

    photo_type: str = "other"

    usage: list[str] = Field(default_factory=list)

    storage_key: str

    description: str | None = None

    original_filename: str | None = None


class OpeningProductSelection(BaseModel):
    opening_id: str

    product_codes: list[str] = Field(default_factory=list)


class ProposalEnrichmentInput(BaseModel):
    opening_products: list[OpeningProductSelection] = Field(default_factory=list)

    global_product_codes: list[str] = Field(default_factory=list)

    customer_needs: list[CustomerNeedSelection] = Field(default_factory=list)

    photos: list[VisitPhotoInput] = Field(default_factory=list)
