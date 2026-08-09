from pydantic import BaseModel, Field

from backend.needs.models import CustomerNeedSelection


class OpeningProductSelection(BaseModel):
    opening_id: str

    product_codes: list[str] = Field(default_factory=list)


class ProposalEnrichmentInput(BaseModel):
    opening_products: list[OpeningProductSelection] = Field(default_factory=list)

    global_product_codes: list[str] = Field(default_factory=list)

    customer_needs: list[CustomerNeedSelection] = Field(default_factory=list)
