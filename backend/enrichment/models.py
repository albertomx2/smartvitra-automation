from pydantic import BaseModel, Field


class OpeningProductSelection(BaseModel):
    opening_id: str

    product_codes: list[str] = Field(default_factory=list)


class ProposalEnrichmentInput(BaseModel):
    opening_products: list[OpeningProductSelection] = Field(default_factory=list)

    global_product_codes: list[str] = Field(default_factory=list)
