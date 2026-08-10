from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from backend.domain.common import SourceReference
from backend.domain.enums import (
    GeneratedAssetType,
    PhotoType,
    ProposalStatus,
    ValidationSeverity,
)


class Customer(BaseModel):
    name: str

    email: str | None = None
    phone: str | None = None

    address: str | None = None
    city: str | None = None
    postal_code: str | None = None
    country: str | None = None

    odoo_id: str | None = None


class Commercial(BaseModel):
    name: str | None = None

    email: str | None = None

    odoo_id: str | None = None


class CustomerNeed(BaseModel):
    code: str
    description: str

    priority: int | None = Field(
        default=None,
        ge=1,
        le=5,
    )

    source_text: str | None = None


class VisitNote(BaseModel):
    text: str

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Photo(BaseModel):
    id: UUID = Field(default_factory=uuid4)

    opening_id: str | None = None

    photo_type: PhotoType = PhotoType.OTHER

    storage_key: str

    usage: list[str] = Field(default_factory=list)

    description: str | None = None

    original_filename: str | None = None

    is_ai_generated: bool = False


class GlassConfiguration(BaseModel):
    description: str | None = None

    control_solar: bool | None = None
    low_emissivity: bool | None = None
    argon: bool | None = None

    composition: str | None = None


class Dimensions(BaseModel):
    width_mm: int | None = Field(default=None, gt=0)
    height_mm: int | None = Field(default=None, gt=0)


class OpeningOption(BaseModel):
    name: str
    value: str | bool | int | float | None = None


class Opening(BaseModel):
    id: str

    position: int | None = None

    room: str | None = None

    description: str | None = None

    window_type: str | None = None

    quantity: int = Field(default=1, gt=0)

    profile: str | None = None

    glass: GlassConfiguration | None = None

    dimensions: Dimensions | None = None

    options: list[OpeningOption] = Field(default_factory=list)


class ProductReference(BaseModel):
    product_code: str

    name: str

    version: str | None = None

    technical_sheet_id: str | None = None

    relevant_to_openings: list[str] = Field(default_factory=list)


class PriceLine(BaseModel):
    opening_id: str | None = None

    description: str

    quantity: Decimal = Decimal(1)

    list_price: Decimal | None = None
    unit_price: Decimal | None = None

    discount_percentage: Decimal | None = None

    subtotal: Decimal | None = None

    tax_percentage: Decimal | None = None


class PaymentTerms(BaseModel):
    description: str | None = None

    deposit_percentage: Decimal | None = None
    pre_installation_percentage: Decimal | None = None
    final_percentage: Decimal | None = None


class ServiceLine(BaseModel):
    name: str

    description: str | None = None

    quantity: Decimal | None = None

    list_price: Decimal | None = None
    unit_price: Decimal | None = None

    discount_percentage: Decimal | None = None

    subtotal: Decimal | None = None

    tax_percentage: Decimal | None = None


class CommercialDiscount(BaseModel):
    name: str

    description: str | None = None

    amount: Decimal | None = None


class AdvancePayment(BaseModel):
    reference: str | None = None

    payment_date: date | None = None

    amount: Decimal | None = None


class Pricing(BaseModel):
    currency: str = "EUR"

    usual_cost: Decimal | None = None

    discount_total: Decimal | None = None

    subtotal: Decimal | None = None
    tax_total: Decimal | None = None
    total: Decimal | None = None

    lines: list[PriceLine] = Field(default_factory=list)

    payment_terms: PaymentTerms | None = None
    services: list[ServiceLine] = Field(default_factory=list)

    discounts: list[CommercialDiscount] = Field(default_factory=list)

    advance_payments: list[AdvancePayment] = Field(default_factory=list)


class SourceDocument(BaseModel):
    id: UUID = Field(default_factory=uuid4)

    name: str

    storage_key: str | None = None

    source: SourceReference


class GeneratedAsset(BaseModel):
    id: UUID = Field(default_factory=uuid4)

    asset_type: GeneratedAssetType

    status: str

    provider: str | None = None

    provider_id: str | None = None

    storage_key: str | None = None

    url: str | None = None

    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ValidationIssue(BaseModel):
    code: str

    severity: ValidationSeverity

    message: str

    field: str | None = None

    expected_value: str | None = None
    actual_value: str | None = None


class ValidationResult(BaseModel):
    passed: bool

    issues: list[ValidationIssue] = Field(default_factory=list)

    validated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Proposal(BaseModel):
    schema_version: str = "1.0"

    id: UUID = Field(default_factory=uuid4)

    proposal_number: str | None = None

    status: ProposalStatus = ProposalStatus.DRAFT

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    proposal_date: date | None = None

    customer: Customer

    commercial: Commercial | None = None

    prefweb_id: str | None = None
    odoo_quote_id: str | None = None
    odoo_opportunity_id: str | None = None

    openings: list[Opening] = Field(default_factory=list)

    products: list[ProductReference] = Field(default_factory=list)

    customer_needs: list[CustomerNeed] = Field(default_factory=list)

    visit_notes: list[VisitNote] = Field(default_factory=list)

    photos: list[Photo] = Field(default_factory=list)

    pricing: Pricing | None = None

    source_documents: list[SourceDocument] = Field(default_factory=list)

    generated_assets: list[GeneratedAsset] = Field(default_factory=list)

    validation_results: list[ValidationResult] = Field(default_factory=list)
