from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class RawOpening(BaseModel):
    position: int
    identifier: str

    description: str | None = None
    room: str | None = None
    glass_description: str | None = None

    quantity: Decimal | None = None

    list_price: Decimal | None = None
    discounted_unit_price: Decimal | None = None

    discount_percentage: Decimal | None = None

    tax_percentage: Decimal | None = None

    subtotal: Decimal | None = None


class RawServiceLine(BaseModel):
    name: str

    description: str | None = None

    quantity: Decimal | None = None

    list_price: Decimal | None = None
    discounted_unit_price: Decimal | None = None

    discount_percentage: Decimal | None = None
    tax_percentage: Decimal | None = None

    subtotal: Decimal | None = None


class RawDiscountLine(BaseModel):
    name: str

    description: str | None = None

    amount: Decimal | None = None


class RawAdvancePayment(BaseModel):
    reference: str | None = None
    payment_date: date | None = None

    amount: Decimal | None = None


class RawPaymentTerms(BaseModel):
    text: str | None = None


class RawProposalData(BaseModel):
    proposal_number: str | None = None
    proposal_date: date | None = None

    customer_name: str | None = None
    customer_address: str | None = None
    customer_city: str | None = None
    customer_country: str | None = None

    commercial_name: str | None = None

    usual_cost: Decimal | None = None
    discount_total: Decimal | None = None
    subtotal: Decimal | None = None
    tax_total: Decimal | None = None
    total: Decimal | None = None

    openings: list[RawOpening] = Field(default_factory=list)

    services: list[RawServiceLine] = Field(default_factory=list)

    discounts: list[RawDiscountLine] = Field(default_factory=list)

    advance_payments: list[RawAdvancePayment] = Field(default_factory=list)

    payment_terms: RawPaymentTerms | None = None

    raw_text: str | None = None
