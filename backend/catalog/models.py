from decimal import Decimal

from pydantic import BaseModel, Field


class TechnicalProperty(BaseModel):
    code: str
    name: str

    value: str | Decimal | int | float | bool | None = None

    unit: str | None = None

    source_text: str | None = None


class ProductBenefit(BaseModel):
    code: str
    title: str

    description: str | None = None

    category: str | None = None


class ProductTechnicalData(BaseModel):
    product_code: str
    name: str

    category: str

    source_document: str

    description: str | None = None

    properties: list[TechnicalProperty] = Field(default_factory=list)

    benefits: list[ProductBenefit] = Field(default_factory=list)
