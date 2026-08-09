from pydantic import BaseModel, Field


class MatchedBenefit(BaseModel):
    benefit_code: str
    title: str

    category: str | None = None
    description: str | None = None


class MatchedProduct(BaseModel):
    product_code: str
    product_name: str

    relevant_to_openings: list[str] = Field(default_factory=list)

    benefits: list[MatchedBenefit] = Field(default_factory=list)


class NeedProductMatch(BaseModel):
    need_code: str

    need_description: str

    priority: int

    benefit_categories: list[str] = Field(default_factory=list)

    matching_products: list[MatchedProduct] = Field(default_factory=list)


class BenefitMatchResult(BaseModel):
    matches: list[NeedProductMatch] = Field(default_factory=list)

    uncovered_need_codes: list[str] = Field(default_factory=list)
