import json
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from backend.integrations.llm.models import (
    StructuredLLMClient,
)
from backend.presentation.content.template_v2 import (
    TemplateV2PresentationContent,
)
from backend.presentation.content.template_v2_constraints import (
    TEMPLATE_V2_TEXT_LIMITS,
)
from backend.presentation.content.template_v2_corrector import (
    TemplateV2ContentCorrector,
)
from backend.presentation.content.template_v2_llm_models import (
    TemplateV2LLMContent,
)
from backend.presentation.content.template_v2_normalizer import (
    TemplateV2ContentNormalizer,
)
from backend.presentation.content.template_v2_prompts import (
    TEMPLATE_V2_SYSTEM_PROMPT,
)
from backend.presentation.content.template_v2_validator import (
    TemplateV2ContentValidator,
    TemplateV2ValidationError,
)


@dataclass(frozen=True)
class TemplateV2DeterministicData:
    customer_name: str
    address: str
    proposal_number: str
    proposal_date: date

    budget_amount: Decimal
    budget_valid_until: date | None

    payment_terms: list[str]


class LLMTemplateV2ContentGenerator:
    def __init__(
        self,
        llm_client: StructuredLLMClient,
    ) -> None:
        self._llm_client = llm_client

    def generate(
        self,
        *,
        context: dict,
        deterministic: TemplateV2DeterministicData,
    ) -> TemplateV2PresentationContent:
        allowed_icon_keys = [
            "thermal",
            "acoustic",
            "energy",
            "solar_control",
            "daylight",
            "ventilation",
            "security",
            "privacy",
            "durability",
            "maintenance",
            "home_value",
            "aesthetics",
            "comfort",
            "humidity",
        ]

        customer_name = str(
            context.get(
                "customer",
                {},
            ).get(
                "name",
                "",
            )
            or ""
        ).strip()

        customer_first_name = customer_name.split()[0] if customer_name else None

        payload = {
            "customer_context": context,
            "customer_first_name": customer_first_name,
            "allowed_icon_keys": allowed_icon_keys,
            "text_limits": {
                "slide01_intro": (TEMPLATE_V2_TEXT_LIMITS["sv_s01_intro_text"]),
                "slide02_issue": max(
                    TEMPLATE_V2_TEXT_LIMITS[f"sv_s02_issue_{index}"]
                    for index in range(1, 6)
                ),
                "slide02_impact": (TEMPLATE_V2_TEXT_LIMITS["sv_s02_issue_6"]),
                "slide03_solution": max(
                    TEMPLATE_V2_TEXT_LIMITS[f"sv_s03_solution_{index}"]
                    for index in range(1, 7)
                ),
                "slide03_main_benefit": (
                    TEMPLATE_V2_TEXT_LIMITS["sv_s03_main_benefit"]
                ),
                "slide03_secondary_benefit": (
                    TEMPLATE_V2_TEXT_LIMITS["sv_s03_main_benefit_secondary"]
                ),
                "slide03_benefit_claim": (
                    TEMPLATE_V2_TEXT_LIMITS["sv_s03_benefit_claim"]
                ),
                "slide07_summary": max(
                    TEMPLATE_V2_TEXT_LIMITS[f"sv_s07_summary_{index}"]
                    for index in range(1, 6)
                ),
            },
        }

        llm_content = self._llm_client.generate_structured(
            system_prompt=(TEMPLATE_V2_SYSTEM_PROMPT),
            user_prompt=(
                "Genera el contenido comercial "
                "de la presentación a partir "
                "exclusivamente de estos datos:\n\n"
                + json.dumps(
                    payload,
                    ensure_ascii=False,
                    indent=2,
                    default=str,
                )
            ),
            response_model=(TemplateV2LLMContent),
        )

        normalizer = TemplateV2ContentNormalizer()

        validator = TemplateV2ContentValidator()

        corrector = TemplateV2ContentCorrector(self._llm_client)

        max_corrections = 2

        for attempt in range(max_corrections + 1):
            content = self._build_content(
                llm_content=llm_content,
                deterministic=deterministic,
            )

            content = normalizer.normalize(content)

            try:
                validator.validate(content)

                return content

            except TemplateV2ValidationError as exc:
                if attempt >= max_corrections:
                    raise

                llm_content = corrector.correct(
                    llm_content=llm_content,
                    error=exc,
                )

        raise RuntimeError("Unexpected Template V2 " "validation state")

    def _build_content(
        self,
        *,
        llm_content: TemplateV2LLMContent,
        deterministic: TemplateV2DeterministicData,
    ) -> TemplateV2PresentationContent:
        return TemplateV2PresentationContent.model_validate(
            {
                "slide01": {
                    "intro_text": (llm_content.slide01.intro_text),
                    "customer_name": (deterministic.customer_name),
                    "address": (deterministic.address),
                    "proposal_number": (deterministic.proposal_number),
                    "date": (deterministic.proposal_date.strftime("%d/%m/%y")),
                },
                "slide02": (llm_content.slide02.model_dump()),
                "slide03": (llm_content.slide03.model_dump()),
                "slide07": {
                    "project_summary": (llm_content.slide07.project_summary),
                    "budget_amount": (self._format_eur(deterministic.budget_amount)),
                    "budget_valid_until": (
                        deterministic.budget_valid_until.strftime("%d/%m/%y")
                        if deterministic.budget_valid_until is not None
                        else "Consultar"
                    ),
                    "payment_terms": (deterministic.payment_terms),
                },
            }
        )

    @staticmethod
    def _format_eur(
        value: Decimal,
    ) -> str:
        formatted = f"{value:,.0f}"

        formatted = formatted.replace(",", ".")

        return f"{formatted}€"
