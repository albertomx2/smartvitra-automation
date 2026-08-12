from pathlib import Path

from pydantic import BaseModel, Field


class TemplateV2SolutionItem(BaseModel):
    text: str

    icon_key: str


class TemplateV2Slide01Content(BaseModel):
    intro_text: str

    customer_name: str

    address: str

    proposal_number: str

    date: str


class TemplateV2IssueContent(BaseModel):
    keyword: str

    detail: str


class TemplateV2Slide02Content(BaseModel):
    issues: list[TemplateV2IssueContent] = Field(
        min_length=1,
        max_length=5,
    )

    impact_statement: str


class TemplateV2Slide03Content(BaseModel):
    solutions: list[TemplateV2SolutionItem] = Field(
        min_length=1,
        max_length=6,
    )

    main_benefit: str

    secondary_benefit: str

    benefit_claim: str


class TemplateV2Slide07Content(BaseModel):
    project_summary: list[str] = Field(
        min_length=1,
        max_length=5,
    )

    budget_amount: str

    budget_valid_until: str

    payment_terms: list[str]


class TemplateV2PresentationContent(BaseModel):
    slide01: TemplateV2Slide01Content

    slide02: TemplateV2Slide02Content

    slide03: TemplateV2Slide03Content

    slide07: TemplateV2Slide07Content

    cover_photo: Path | None = None

    problem_photo: Path | None = None

    generated_solution_image: Path | None = None

    project_photos: list[Path] = Field(
        default_factory=list,
        max_length=3,
    )

    generated_result_image: Path | None = None
