from decimal import Decimal

from pydantic import BaseModel, Field


class BriefCustomer(BaseModel):
    name: str
    city: str | None = None


class BriefNeed(BaseModel):
    code: str
    description: str
    priority: int
    covered: bool

    source_text: str | None = None


class BriefBenefit(BaseModel):
    code: str
    title: str
    category: str | None = None
    description: str | None = None


class BriefTechnicalProperty(BaseModel):
    code: str
    name: str

    value: str | Decimal | int | float | bool | None = None
    unit: str | None = None


class BriefPhoto(BaseModel):
    photo_id: str
    opening_id: str | None = None

    photo_type: str
    storage_key: str

    description: str | None = None

    is_ai_generated: bool = False


class BriefService(BaseModel):
    name: str

    description: str | None = None

    included: bool = True


class BriefProduct(BaseModel):
    product_code: str
    product_name: str

    relevant_to_openings: list[str] = Field(default_factory=list)

    benefits: list[BriefBenefit] = Field(default_factory=list)

    technical_properties: list[BriefTechnicalProperty] = Field(default_factory=list)

    technical_source: str | None = None


class BriefOpening(BaseModel):
    opening_id: str
    room: str | None = None
    window_type: str | None = None

    glass_description: str | None = None

    product_codes: list[str] = Field(default_factory=list)


class BriefPricing(BaseModel):
    currency: str

    subtotal: Decimal | None = None
    tax_total: Decimal | None = None
    total: Decimal | None = None

    payment_terms: str | None = None


class CommercialBrief(BaseModel):
    proposal_number: str | None = None

    customer: BriefCustomer

    primary_need: BriefNeed | None = None

    secondary_needs: list[BriefNeed] = Field(default_factory=list)

    openings: list[BriefOpening] = Field(default_factory=list)

    products: list[BriefProduct] = Field(default_factory=list)

    pricing: BriefPricing | None = None

    photos: list[BriefPhoto] = Field(default_factory=list)

    services: list[BriefService] = Field(default_factory=list)

    uncovered_need_codes: list[str] = Field(default_factory=list)
